"""C20 literal-edit copy of the frozen linear driver; self/guided only.

Only an explicitly invoked CLI run starts the pinned local server. Tests inject
a server lifecycle and use HTTP fixtures, never an ML executable. Server children
inherit the caller's process group so the outer 1800-second runner also owns
them. A server watchdog and per-HTTP remaining-deadline timeouts are additional
bounds, not a substitute for that outer process-group watchdog.
"""

import argparse
from contextlib import contextmanager
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import resource
import shutil
import signal
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.request

from .repair_feedback import validate_feedback
from .repair_patch_language import INTERPRETATION, PATCH_GRAMMAR, PATCH_SCHEMA, parse_patch
from .repair_model import no_duplicates


BUILD = "b12359"
CONTEXT = 4096
MAX_NEW_TOKENS = 512
PHASE_SECONDS = 1650.0
WATCHDOG_SECONDS = 1800.0
REQUEST_SECONDS = 180.0
THREADS = 4
METAL_DEVICE = "MTL0"
GPU_LAYERS = 99
MAX_HTTP_BYTES = 8 * 1024 * 1024
SAMPLERS = ["top_k", "top_p", "temperature"]
PHASES = ("self", "guided")

# Generic patch grammar is independent of request data and reference labels.
FORM_SCHEMA = PATCH_SCHEMA
FORM_GRAMMAR = PATCH_GRAMMAR
SOURCE_DRIVER_SHA256 = "27da08e8c072ae711aaf8451e761ed91bea0bec421974626241503e74b4195be"

SELF_INSTRUCTION = (
    "Review the previous model against every original clause and numerical datum. "
    "Evaluate the original clauses and numerical data before editing. Return diagnosis and explicit edits only."
)
GUIDED_INSTRUCTION = (
    "Use this verifier result to correct the previous model. Recheck ALL original clauses, "
    "not just the witness. Evaluate a witness against the current rows, reread the original clause, then return diagnosis and explicit edits only."
)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def acquisition_pins(path, binary, model):
    """Authenticate the public acquisition's extracted runtime and GGUF bytes."""
    metadata = strict_json(Path(path).read_text())
    binary, model = Path(binary).resolve(), Path(model).resolve()
    if metadata.get("status") != "completed" or metadata.get("runtime_tag") != BUILD:
        raise ValueError("completed pinned b12359 acquisition required")
    runtime_root = binary.parent.parent
    files = metadata.get("runtime_extraction", {}).get("files", [])
    pinned = {}
    for entry in files:
        relative = Path(entry["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("runtime acquisition path escapes its extraction")
        candidate = (runtime_root / relative).resolve()
        if not candidate.is_relative_to(runtime_root) or digest(candidate) != entry["sha256"]:
            raise ValueError("extracted runtime artifact hash changed")
        pinned[candidate] = entry["sha256"]
    downloads = [entry for entry in metadata.get("downloads", [])
                 if Path(entry["destination"]).resolve() == model]
    if binary not in pinned or len(downloads) != 1:
        raise ValueError("requested binary/model are not the acquired files")
    download = downloads[0]
    expected = metadata.get("model", {}).get("sha256_expected")
    if (download.get("status") != "completed" or download.get("sha256_expected") != expected
            or download.get("sha256_observed") != expected or digest(model) != expected):
        raise ValueError("GGUF differs from completed acquisition")
    return pinned[binary], expected, metadata


def strict_json(text):
    def reject_constant(_):
        raise ValueError("nonfinite HTTP or input JSON")
    return json.loads(text, object_pairs_hook=no_duplicates, parse_constant=reject_constant)


def seed_for(identifier, phase):
    value = (int(hashlib.sha256(identifier.encode("utf-8")).hexdigest()[:8], 16)
             + (0 if phase == "initial" else 1)) % (2 ** 32)
    if value == 2 ** 32 - 1:
        raise ValueError("derived seed is llama.cpp's reserved random-seed value")
    return value


def validate_phase_inputs(phase, initial_path, feedback_path):
    if phase not in PHASES:
        raise ValueError("unknown phase")
    if (phase in ("self", "guided")) != (initial_path is not None):
        raise ValueError("only revision phases may read an initial response")
    if (phase == "guided") != (feedback_path is not None):
        raise ValueError("only guided phase may read minimal verifier feedback")


def public_cases(path):
    cases = strict_json(Path(path).read_text())
    if not isinstance(cases, list) or not cases:
        raise ValueError("nonempty public case list required")
    seen = set()
    for case in cases:
        if (type(case) is not dict or not {"id", "intention", "data"} <= set(case)
                or not set(case) <= {"id", "language", "intention", "data"}):
            raise ValueError("public fields only; no annotation input")
        identifier = case["id"]
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise ValueError("unique nonempty public IDs required")
        seen.add(identifier)
        if type(case["intention"]) is not str:
            raise ValueError("intention must be text")
        data = case["data"]
        if type(data) is not dict or set(data) != {"n", "weights", "costs", "edges"}:
            raise ValueError("public numerical data shape")
        n = data["n"]
        if type(n) is not int or not 1 <= n <= 8:
            raise ValueError("unsupported public size")
        if any(type(data[k]) is not list or len(data[k]) != n
               or any(type(v) is not int or v <= 0 for v in data[k]) for k in ("weights", "costs")):
            raise ValueError("positive public weights/costs required")
        if type(data["edges"]) is not list or any(
                type(pair) is not list or len(pair) != 2
                or any(type(i) is not int or not 0 <= i < n for i in pair)
                or pair[0] == pair[1] for pair in data["edges"]):
            raise ValueError("invalid public exclusion pair")
    return sorted(cases, key=lambda case: case["id"])


def initial_records(path, cases, system):
    result = {}
    for line in Path(path).read_text().splitlines():
        row = strict_json(line)
        if type(row) is not dict or row.get("id") in result:
            raise ValueError("duplicate or malformed initial record")
        result[row.get("id")] = row
    for case in cases:
        row = result.get(case["id"])
        expected_user = {"intention": case["intention"], "data": case["data"]}
        if row is None or row.get("phase") != "initial" or type(row.get("raw_response")) is not str:
            raise ValueError("missing initial observation; no imputation")
        messages = row.get("messages")
        if (type(messages) is not list or len(messages) != 2
                or messages[0] != {"role": "system", "content": system}
                or messages[1].get("role") != "user"
                or strict_json(messages[1]["content"]) != expected_user):
            raise ValueError("initial history does not match public request/instructions")
    return result


def messages_for(case, system, phase, initial=None, feedback=None):
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": json.dumps(
                    {"intention": case["intention"], "data": case["data"]}, ensure_ascii=False)}]
    if phase in ("self", "guided"):
        if initial is None:
            raise ValueError("revision needs an actual initial response")
        messages.append({"role": "assistant", "content": initial["raw_response"]})
        follow = SELF_INSTRUCTION
        if phase == "guided":
            validate_feedback(feedback, case["data"]["n"])
            follow = json.dumps({"verifier_feedback": feedback, "instruction": GUIDED_INSTRUCTION},
                                ensure_ascii=False)
        messages.append({"role": "user", "content": follow})
    return messages


def chatml(messages):
    """Qwen2.5 text-only system/user/assistant template, no automatic defaults."""
    output = []
    for message in messages:
        role, content = message["role"], message["content"]
        if role not in ("system", "user", "assistant") or type(content) is not str:
            raise ValueError("unsupported ChatML turn")
        if any(marker in content for marker in ("<|im_start|>", "<|im_end|>", "<|endoftext|>")):
            raise ValueError("literal ChatML control token in message")
        output.append("<|im_start|>" + role + "\n" + content + "<|im_end|>\n")
    return "".join(output) + "<|im_start|>assistant\n"


def completion_request(prompt_ids, seed, max_new_tokens=MAX_NEW_TOKENS):
    if (type(max_new_tokens) is not int or not 1 <= max_new_tokens <= MAX_NEW_TOKENS
            or type(seed) is not int or not 0 <= seed < 2 ** 32 - 1):
        raise ValueError("invalid prediction cap or deterministic seed")
    if (not prompt_ids or any(type(i) is not int or i < 0 for i in prompt_ids)
            or len(prompt_ids) + max_new_tokens + 1 > CONTEXT):
        raise ValueError("context cap including full output reserve; no truncation")
    return {"prompt": prompt_ids, "n_predict": max_new_tokens, "stream": False,
            "seed": seed, "temperature": 0.7, "top_k": 20, "top_p": 0.8,
            "min_p": 0.0, "typical_p": 1.0, "repeat_penalty": 1.0,
            "repeat_last_n": 0, "presence_penalty": 0.0, "frequency_penalty": 0.0,
            "dry_multiplier": 0.0, "mirostat": 0, "samplers": SAMPLERS[:],
            "cache_prompt": False, "return_tokens": True, "n_probs": 1,
            "post_sampling_probs": True, "ignore_eos": False, "stop": [],
            "grammar": FORM_GRAMMAR}


def decode_completion(response, input_count, seed, max_new_tokens):
    """Accept only matched chosen-token probabilities, never a top-1 fallback."""
    if type(response) is not dict or "error" in response or type(response.get("content")) is not str:
        raise ValueError("invalid completion response")
    ids = response.get("tokens")
    probabilities = response.get("completion_probabilities")
    if (type(ids) is not list or not 0 < len(ids) <= max_new_tokens
            or any(type(i) is not int or i < 0 for i in ids)
            or type(probabilities) is not list or len(probabilities) != len(ids)):
        raise ValueError("missing or misaligned generated IDs/chosen-token probabilities")
    if (type(response.get("tokens_predicted")) is not int or response["tokens_predicted"] != len(ids)
            or type(response.get("tokens_evaluated")) is not int or response["tokens_evaluated"] != input_count
            or response.get("truncated") is not False):
        raise ValueError("inconsistent token accounting or truncated context")
    settings = response.get("generation_settings", {})
    if (settings.get("post_sampling_probs") is not True or settings.get("samplers") != SAMPLERS
            or settings.get("seed") != seed or settings.get("top_k") != 20
            or not math.isclose(settings.get("temperature", -1), 0.7, rel_tol=1e-6)
            or not math.isclose(settings.get("top_p", -1), 0.8, rel_tol=1e-6) or settings.get("min_p") != 0.0
            or settings.get("n_predict") != max_new_tokens):
        raise ValueError("server sampling settings differ from requested processed probabilities")
    if settings.get("backend_sampling", False) is not False:
        raise ValueError("backend sampling not admitted by this driver")
    speculative = settings.get("speculative.types", "")
    if isinstance(speculative, str):
        speculative = [kind.strip() for kind in speculative.split(",") if kind.strip()]
    if type(speculative) is not list or any(kind not in ("none", "disabled") for kind in speculative):
        raise ValueError("post-sampling probabilities unsupported with speculative decoding")
    logs = []
    for token, entry in zip(ids, probabilities):
        if type(entry) is not dict or type(entry.get("id")) is not int or entry["id"] != token:
            raise ValueError("chosen-token probability ID mismatch")
        probability = entry.get("prob")
        if type(probability) not in (int, float) or not math.isfinite(probability) or not 0 < probability <= 1:
            raise ValueError("finite positive chosen-token post-sampling probability required")
        logs.append(math.log(probability))
    stop = response.get("stop_type")
    if stop not in ("eos", "limit") or (stop == "limit" and len(ids) != max_new_tokens):
        raise ValueError("unexplained completion stop; no invented token-limit result")
    return ids, logs, "eos" if stop == "eos" else "token_limit"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        raise ValueError("local API redirects are not permitted")


class LoopbackClient:
    def __init__(self, port):
        if type(port) is not int or not 1 <= port <= 65535:
            raise ValueError("invalid loopback port")
        self.base = "http://127.0.0.1:" + str(port)
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        self.last_response_bytes = None

    def request(self, endpoint, payload=None, timeout=10.0):
        if endpoint not in ("/health", "/tokenize", "/completion", "/apply-template") or not 0 < timeout <= PHASE_SECONDS:
            raise ValueError("unsupported local endpoint or timeout")
        request = urllib.request.Request(self.base + endpoint,
                                         data=None if payload is None else json_bytes(payload),
                                         headers={"Content-Type": "application/json"})
        self.last_response_bytes = None
        try:
            with self.opener.open(request, timeout=timeout) as response:
                self.last_response_bytes = response.read(MAX_HTTP_BYTES + 1)
        except urllib.error.HTTPError as exc:
            self.last_response_bytes = exc.read(MAX_HTTP_BYTES + 1)
            raise
        if len(self.last_response_bytes) > MAX_HTTP_BYTES:
            raise ValueError("local HTTP response exceeds byte cap")
        return strict_json(self.last_response_bytes.decode("utf-8"))


def server_command(binary, model, port):
    return [str(Path(binary).resolve()), "--model", str(Path(model).resolve()),
            "--host", "127.0.0.1", "--port", str(port), "--offline",
            "--ctx-size", str(CONTEXT), "--threads", str(THREADS),
            "--threads-batch", str(THREADS), "--n-gpu-layers", str(GPU_LAYERS), "--device", METAL_DEVICE,
            "--parallel", "1", "--no-warmup", "--no-context-shift", "--cache-ram", "0",
            "--no-webui", "--no-agent", "--no-cache-prompt", "--threads-http", "1",
            "--log-verbosity", "4", "--jinja", "--chat-template-kwargs", '{"enable_thinking":false}']


def observe_backend(log_path):
    """Read loader evidence; a requested/available device is not observed use."""
    gpu_layers = total_layers = None
    metal_buffer = False
    evidence = []
    if Path(log_path).exists():
        with Path(log_path).open(errors="replace") as handle:
            for line in handle:
                offload = re.search(r"offloaded (\d+)/(\d+) layers to GPU", line)
                if offload:
                    gpu_layers, total_layers = map(int, offload.groups())
                    evidence.append(line.strip())
                buffer = re.search(r"\b(?:Metal|MTL)[^\s]*\s+model buffer size\s*=\s*([0-9.]+) MiB", line)
                if buffer and float(buffer.group(1)) > 0:
                    metal_buffer = True
                    evidence.append(line.strip())
    return {"device": "Metal" if gpu_layers is not None and gpu_layers > 0 and metal_buffer else "unverified",
            "offloaded_gpu_layers": gpu_layers, "reported_total_layers": total_layers,
            "positive_metal_model_buffer": metal_buffer, "evidence_lines": evidence[-8:],
            "scope": "loader tensor placement evidence, not a claim of GPU-only execution or memory fit"}


class ServerProcess:
    def __init__(self, binary, model, output, deadline):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        self.client = LoopbackClient(port)
        self.command = server_command(binary, model, port)
        self.output = output
        self.deadline = deadline
        self.process = None
        self.watchdog = None
        self.handles = []
        self.stats = {}

    def start(self):
        self.child_cpu_before = resource.getrusage(resource.RUSAGE_CHILDREN)
        env = {"PATH": os.defpath, "DYLD_LIBRARY_PATH": str(Path(self.command[0]).parent),
               "OMP_NUM_THREADS": str(THREADS), "OPENBLAS_NUM_THREADS": str(THREADS),
               "VECLIB_MAXIMUM_THREADS": str(THREADS), "LC_ALL": "C"}
        self.handles = [(self.output / name).open("xb") for name in ("server.stdout.txt", "server.stderr.txt")]
        # Keep the outer runner's process group: no detached orphan on timeout.
        self.process = subprocess.Popen(self.command, stdout=self.handles[0], stderr=self.handles[1], env=env)
        self.watchdog = threading.Timer(WATCHDOG_SECONDS, self.kill)
        self.watchdog.daemon = True
        self.watchdog.start()
        while time.perf_counter() < self.deadline:
            if self.process.poll() is not None:
                raise RuntimeError("local server exited before readiness")
            try:
                if self.client.request("/health", timeout=min(1.0, self.deadline - time.perf_counter())).get("status") == "ok":
                    self.stats["backend_observed"] = observe_backend(self.output / "server.stderr.txt")
                    if self.stats["backend_observed"]["device"] != "Metal":
                        raise RuntimeError("requested Metal tensor offload not confirmed; no inference attempted")
                    return self.client
            except (urllib.error.URLError, TimeoutError, OSError):
                pass
            time.sleep(min(0.1, max(0.0, self.deadline - time.perf_counter())))
        raise TimeoutError("phase deadline during local model load")

    def kill(self):
        if self.process is not None and self.process.poll() is None:
            self.process.kill()

    def stop(self):
        if self.watchdog is not None:
            self.watchdog.cancel()
        try:
            if self.process is not None:
                if self.process.poll() is None:
                    self.process.terminate()
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.kill()
                    self.process.wait(timeout=2)
                usage = resource.getrusage(resource.RUSAGE_CHILDREN)
                self.stats.update({"server_exit_status": self.process.returncode,
                                   "server_cpu_seconds": (usage.ru_utime + usage.ru_stime
                                                          - self.child_cpu_before.ru_utime - self.child_cpu_before.ru_stime),
                                   "child_peak_rss_native_units": usage.ru_maxrss,
                                   "backend_observed": observe_backend(self.output / "server.stderr.txt")})
        finally:
            for handle in self.handles:
                handle.close()


def remaining(deadline):
    value = deadline - time.perf_counter()
    if value <= 0:
        raise TimeoutError("bounded inference phase")
    return min(value, PHASE_SECONDS)


@contextmanager
def hard_completion_timeout(phase_deadline):
    """Hard wall cap on a completion, then restore the absolute phase deadline."""
    if threading.current_thread() is not threading.main_thread():
        raise RuntimeError("bounded inference must execute on the main thread")
    signal.setitimer(signal.ITIMER_REAL, min(REQUEST_SECONDS, remaining(phase_deadline)))
    try:
        yield
    finally:
        phase_left = phase_deadline - time.perf_counter()
        signal.setitimer(signal.ITIMER_REAL, max(0.0, phase_left))
        if phase_left <= 0:
            raise TimeoutError("absolute phase deadline reached during completion")


def run_phase(*, cases_path, instructions_path, phase, output, binary, model,
              binary_sha256=None, model_sha256=None, initial_path=None, feedback_path=None,
              initial_instructions_path=None,
              max_new_tokens=MAX_NEW_TOKENS, acquisition_path=None, case_limit=None,
              server_factory=ServerProcess):
    validate_phase_inputs(phase, initial_path, feedback_path)
    if initial_instructions_path is None:
        raise ValueError("historical initial instructions are required to authenticate reused history")
    if threading.current_thread() is not threading.main_thread():
        raise RuntimeError("phase signal deadlines require the main thread")
    if type(max_new_tokens) is not int or not 1 <= max_new_tokens <= MAX_NEW_TOKENS:
        raise ValueError("max_new_tokens must be within 1..512")
    output = Path(output)
    if output.exists():
        raise ValueError("refuse to overwrite or reuse any inference output directory")
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    deadline = started + PHASE_SECONDS
    cpu_start = time.process_time()
    record = {"runtime": "llama.cpp", "runtime_tag": BUILD, "python": platform.python_version(),
              "response_format": "diagnosis_and_literal_edits", "patch_interpretation": INTERPRETATION,
              "diagnosis_scope": "unverified LLM text; no semantic effect",
              "copied_driver_sha256": SOURCE_DRIVER_SHA256, "initial_response_reused": True,
              "phase": phase, "status": "running", "error": None, "planned": None, "completed": 0,
              "input_tokens": 0, "output_tokens": 0, "threads": THREADS,
              "backend_requested": {"device": METAL_DEVICE, "gpu_layers": GPU_LAYERS, "cpu_threads": THREADS},
              "backend_observed": {"device": "unverified"},
              "context": CONTEXT, "max_new_tokens": max_new_tokens,
              "max_input_tokens": CONTEXT - max_new_tokens - 1,
              "phase_deadline_seconds": PHASE_SECONDS, "server_watchdog_seconds": WATCHDOG_SECONDS,
              "request_timeout_seconds": REQUEST_SECONDS,
              "outer_process_group_watchdog_required_seconds": 1800,
              "sampling": {"temperature": 0.7, "top_k": 20, "top_p": 0.8, "samplers": SAMPLERS},
              "seed_rule": "first8hexsha256(id) + phase offset modulo2**32; reject reserved 0xffffffff",
              "patch_schema_sha256": hashlib.sha256(json_bytes(FORM_SCHEMA)).hexdigest(),
              "patch_grammar_sha256": hashlib.sha256(FORM_GRAMMAR.encode()).hexdigest(),
              "cpu_cost_scope": "row CPU is Python HTTP client only; server total recorded once after reaping",
              "network_scope": "HTTP only to owned 127.0.0.1 server, proxy/redirects disabled; server --offline",
              "external_purchase_eur": 0, "reference_or_gold_input": False,
              "prompt_rendering": "pinned GGUF template via /apply-template; global enable_thinking=false; no hidden reasoning calls"}
    server = None
    old_handlers = {}
    previous_alarm = None

    def interrupted(signum, _frame):
        raise TimeoutError("signal " + str(signum) + ": interrupted phase, preserve actual rows")

    try:
        for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGALRM):
            if threading.current_thread() is threading.main_thread():
                old_handlers[signum] = signal.signal(signum, interrupted)
        if threading.current_thread() is threading.main_thread():
            previous_alarm = signal.setitimer(signal.ITIMER_REAL, PHASE_SECONDS)
        cases = public_cases(cases_path)
        record["public_cases_total"] = len(cases)
        if case_limit is not None:
            if type(case_limit) is not int or not 1 <= case_limit <= len(cases):
                raise ValueError("case_limit must select a nonempty sorted prefix")
            cases = cases[:case_limit]
        record["case_selection"] = {"rule": "first IDs in lexicographic order", "limit": case_limit}
        record["planned"] = len(cases)
        system = Path(instructions_path).read_text()
        initial_system = Path(initial_instructions_path).read_text()
        initial = initial_records(initial_path, cases, initial_system)
        feedback = strict_json(Path(feedback_path).read_text()) if feedback_path is not None else {}
        if feedback_path is not None:
            if type(feedback) is not dict or not {case["id"] for case in cases} <= set(feedback):
                raise ValueError("missing minimal feedback observations")
            for case in cases:
                validate_feedback(feedback[case["id"]], case["data"]["n"])
        if acquisition_path is None:
            raise ValueError("public acquisition metadata required; no unpinned runtime")
        acquired_binary, acquired_model, acquisition = acquisition_pins(acquisition_path, binary, model)
        if ((binary_sha256 is not None and binary_sha256 != acquired_binary)
                or (model_sha256 is not None and model_sha256 != acquired_model)):
            raise ValueError("explicit digest disagrees with acquisition metadata")
        binary_sha256, model_sha256 = acquired_binary, acquired_model
        record["runtime_commit"] = acquisition.get("runtime_commit")
        record["model_repository"] = acquisition.get("model", {}).get("repo")
        record["revision"] = acquisition.get("model", {}).get("commit")
        record["quantization_file"] = acquisition.get("model", {}).get("file")
        pins = [(Path(binary), binary_sha256), (Path(model), model_sha256)]
        if any(len(expected) != 64 or digest(path) != expected for path, expected in pins):
            raise ValueError("runtime binary or GGUF hash differs from acquisition pin")
        with Path(model).open("rb") as handle:
            if handle.read(4) != b"GGUF":
                raise ValueError("pinned checkpoint is not GGUF")
        inputs = [Path(cases_path), Path(instructions_path)] + [path for path in
                  (initial_path, initial_instructions_path, feedback_path, acquisition_path) if path is not None]
        record["input_sha256"] = {str(path): digest(path) for path in inputs}
        record["binary"] = {"path": str(Path(binary).resolve()), "sha256": binary_sha256}
        record["model"] = {"path": str(Path(model).resolve()), "sha256": model_sha256}
        (output / "patch-schema.json").write_bytes(json_bytes(FORM_SCHEMA))
        (output / "patch-grammar.gbnf").write_text(FORM_GRAMMAR)
        remaining(deadline)
        if shutil.disk_usage(output).free < 3*1024**3:
            raise OSError("disk reserve below 3GiB before model startup; no generation attempted")
        server = server_factory(binary, model, output, deadline)
        record["server_command"] = server.command
        client = server.start()
        record["load_seconds"] = time.perf_counter() - started
        (output / "http").mkdir()
        with (output / "raw.jsonl").open("x") as raw:
            for index, case in enumerate(cases):
                remaining(deadline)
                if shutil.disk_usage(output).free < 1024**3:
                    raise OSError("disk reserve below 1GiB before next call; stop without resampling")
                messages = messages_for(case, system, phase, initial.get(case["id"]), feedback.get(case["id"]))
                chatml(messages)  # retain control-token whitelist validation
                template_request = {"messages": messages}
                rendered = client.request("/apply-template", template_request,
                                          timeout=min(REQUEST_SECONDS, remaining(deadline)))
                (output/"http"/("%03d.template.request.json" % index)).write_bytes(json_bytes(template_request))
                (output/"http"/("%03d.template.response.json" % index)).write_bytes(json_bytes(rendered))
                prompt = rendered.get("prompt")
                if type(prompt) is not str or prompt.rstrip().endswith("<think>"):
                    raise ValueError("GGUF template missing or reasoning remains open")
                (output/"http"/("%03d.prompt.txt" % index)).write_text(prompt)
                tokenize = client.request("/tokenize", {"content": prompt, "add_special": True,
                                                        "parse_special": True, "with_pieces": False},
                                          timeout=min(REQUEST_SECONDS, remaining(deadline)))
                prompt_ids = tokenize.get("tokens")
                if type(prompt_ids) is not list:
                    raise ValueError("tokenizer response lacks token IDs")
                seed = seed_for(case["id"], phase)
                request = completion_request(prompt_ids, seed, max_new_tokens)
                stem = output / "http" / ("%03d" % index)
                stem.with_suffix(".request.json").write_bytes(json_bytes(request))
                t0, c0 = time.perf_counter(), time.process_time()
                try:
                    with hard_completion_timeout(deadline):
                        response = client.request("/completion", request, timeout=min(REQUEST_SECONDS, remaining(deadline)))
                finally:
                    if client.last_response_bytes is not None:
                        stem.with_suffix(".response.json").write_bytes(client.last_response_bytes)
                generation_wall, generation_cpu = time.perf_counter() - t0, time.process_time() - c0
                ids, logs, finish = decode_completion(response, len(prompt_ids), seed, max_new_tokens)
                row = {"id": case["id"], "phase": phase, "seed": seed, "messages": messages,
                       "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                       "input_token_ids": prompt_ids, "raw_response": response["content"],
                       "parsed": parse_patch(response["content"], case["data"]["n"], initial[case["id"]]["raw_response"]),
                       "response_format": "diagnosis_and_literal_edits",
                       "initial_response_sha256": hashlib.sha256(initial[case["id"]]["raw_response"].encode()).hexdigest(),
                       "input_tokens": len(prompt_ids), "output_tokens": len(ids),
                       "generated_token_ids": ids, "generated_token_log_probabilities": logs,
                       "mean_generated_log_probability": sum(logs) / len(logs),
                       "log_probability_scope": "chosen token probability reported by pinned API after sampler processing; grammar acceptance/resampling branch may affect normalization; heuristic selection, not unconditional/grammar-conditioned likelihood; reported EOS included",
                       "finish_reason": finish, "generation_wall_seconds": generation_wall,
                       "generation_cpu_seconds": generation_cpu,
                       "wall_seconds": time.perf_counter() - t0, "cpu_seconds": time.process_time() - c0,
                       "cpu_seconds_scope": "Python HTTP client only; server CPU is phase-level metadata",
                       "server_timings": response.get("timings"),
                       "http_response": str(stem.with_suffix(".response.json").relative_to(output))}
                raw.write(json_bytes(row).decode("utf-8"))
                raw.flush()
                record["completed"] += 1
                record["input_tokens"] += len(prompt_ids)
                record["output_tokens"] += len(ids)
                print(json.dumps({"completed": record["completed"], "phase": phase, "id": case["id"],
                                  "valid_schema": row["parsed"]["valid"], "tokens": len(ids)}), flush=True)
                remaining(deadline)
        record["status"] = "completed"
        return record
    except BaseException as exc:
        record["status"] = "partial_error"
        record["error"] = type(exc).__name__ + ": " + str(exc)
        raise
    finally:
        try:
            if server is not None:
                server.stop()
                record.update(server.stats)
        except BaseException as exc:
            record["status"] = "partial_error"
            record["shutdown_error"] = type(exc).__name__ + ": " + str(exc)
            if record["error"] is None:
                record["error"] = record["shutdown_error"]
            raise
        finally:
            record["wall_seconds"] = time.perf_counter() - started
            record["client_cpu_seconds"] = time.process_time() - cpu_start
            record["cpu_seconds"] = record["client_cpu_seconds"] + record.get("server_cpu_seconds", 0)
            record["peak_rss_native_units"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            record["recorded_at_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            (output / "generation.json").write_bytes(json_bytes(record))
            if previous_alarm is not None:
                signal.setitimer(signal.ITIMER_REAL, 0)
            for signum, handler in old_handlers.items():
                signal.signal(signum, handler)
            if previous_alarm is not None and previous_alarm[0] > 0:
                signal.setitimer(signal.ITIMER_REAL, max(0.000001, previous_alarm[0] - record["wall_seconds"]), previous_alarm[1])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--instructions", type=Path, required=True)
    parser.add_argument("--phase", choices=PHASES, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--server-binary", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--server-sha256")
    parser.add_argument("--model-sha256")
    parser.add_argument("--acquisition", type=Path, required=True)
    parser.add_argument("--initial", type=Path, required=True)
    parser.add_argument("--initial-instructions", type=Path, required=True)
    parser.add_argument("--feedback", type=Path)
    parser.add_argument("--max-new-tokens", type=int, default=MAX_NEW_TOKENS)
    parser.add_argument("--case-limit", type=int, help="prospectively select the first N sorted IDs, e.g. preflight 2")
    parser.add_argument("--execute", action="store_true", help="start the pinned local server after acquisition and protocol authorization")
    args = parser.parse_args(argv)
    if not args.execute:
        parser.error("--execute is required to start a real local inference phase")
    run_phase(cases_path=args.cases, instructions_path=args.instructions, phase=args.phase,
              output=args.output, binary=args.server_binary, model=args.model,
              binary_sha256=args.server_sha256, model_sha256=args.model_sha256,
              initial_path=args.initial, feedback_path=args.feedback,
              initial_instructions_path=args.initial_instructions,
              max_new_tokens=args.max_new_tokens, acquisition_path=args.acquisition,
              case_limit=args.case_limit)


if __name__ == "__main__":
    main()
