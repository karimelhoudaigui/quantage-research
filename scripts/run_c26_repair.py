"""C26 prospective wrapper: one authorized development call; import has no effects."""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RUN = Path("runs/20261116-c26-quantized-kv")
STATE = Path("runs/20261116-c24-second-repair")
ACQUISITION = Path("runs/20261115-c22-model-capacity/acquisition.json")
RUNTIME = Path("research/external/c16-public/runtime")
MODEL = Path("research/external/c22-public/models/Qwen3-8B-Q4_K_M.gguf")
DRIVER = "quantage.repair_second_round_q8_inference"
RUNNER = Path("/Users/karimelhoudaigui/.codex/plugins/cache/openai-curated-remote/mathbox/4.0.0/skills/computation-audit/scripts/run_experiment.py")
OUT = RUN / "guided-round2-v1"
TIMEOUT = 480


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024*1024), b""):
            result.update(chunk)
    return result.hexdigest()


def driver_command():
    return ["/usr/bin/caffeinate", "-i", "-t", str(TIMEOUT), sys.executable,
            "-m", DRIVER, "--cases", str(STATE/"public_case.json"),
            "--instructions", str(STATE/"instructions.txt"),
            "--state-instructions", str(STATE/"instructions.txt"),
            "--state-records", str(STATE/"states.json"),
            "--feedback", str(STATE/"feedback.json"), "--phase", "guided",
            "--output", str(OUT/"driver"),
            "--server-binary", str(RUNTIME/"llama-b12359/llama-server"),
            "--model", str(MODEL), "--acquisition", str(ACQUISITION), "--execute"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true",
                        help="one authorized call through the bounded process-group runner")
    args = parser.parse_args(argv)
    if not args.execute:
        print(json.dumps({"prospective_only": True, "timeout_seconds": TIMEOUT,
                          "driver_command": driver_command()}, indent=2))
        return 0
    if Path.cwd().resolve() != ROOT:
        raise ValueError("launch from project root")
    freeze = RUN/"freeze-round2-v1.json"
    contract = RUN/"contract-guided-round2-v1.json"
    if OUT.exists() or freeze.exists() or contract.exists():
        raise ValueError("C26 is one attempt only; refuse any output/freeze/contract reuse")
    acquisition = json.loads(ACQUISITION.read_text())
    runtime_files = []
    for entry in acquisition["runtime_extraction"]["files"]:
        relative = Path(entry["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("runtime artifact path escapes extraction")
        runtime_files.append(str(RUNTIME/relative))
    artifacts = [
        "scripts/run_c26_repair.py", "quantage/repair_second_round_q8_inference.py",
        "quantage/repair_iterative_patch_inference.py", "quantage/repair_iterative_state.py",
        "quantage/repair_patch_tool_language.py", "quantage/repair_language.py",
        "quantage/repair_model.py", "quantage/repair_feedback.py", "quantage/repair_trace_feedback.py",
        str(RUN/"protocol.md"), str(RUN/"native-help.json"), str(RUN/"code-checks.json"),
        str(STATE/"public_case.json"), str(STATE/"instructions.txt"),
        str(STATE/"states.json"), str(STATE/"feedback.json"),
        str(STATE/"before-verification.json"), str(STATE/"freeze-round2-v1.json"),
        str(ACQUISITION), str(MODEL), *runtime_files]
    artifacts = list(dict.fromkeys(artifacts))
    cases = json.loads((STATE/"public_case.json").read_text())
    if len(cases) != 1:
        raise ValueError("exactly one pre-existing C24 development case required")
    seed = (int(hashlib.sha256(cases[0]["id"].encode()).hexdigest()[:8], 16)+2) % 2**32
    if seed == 2**32-1:
        raise ValueError("reserved seed sentinel")
    with freeze.open("x") as handle:
        json.dump({"client_date": "2026-11-16", "development_only": True,
                   "new_guided_call_budget": 1, "initial_resampled": False,
                   "state_source": str(STATE/"states.json"),
                   "sha256": {p: digest(p) for p in artifacts if not p.startswith("research/external/")}},
                  handle, indent=2)
        handle.write("\n")
    artifacts.append(str(freeze))
    data = {
        "claim_id": "C26-Q8-KV-DEVELOPMENT-SECOND-REPAIR",
        "mathematics": {
            "assertion_tested": "One complete second-repair response under explicit Flash Attention and q8_0 K/V cache, using the unchanged C24 recorded development state",
            "coefficient_domain": "exact binary integer ILP after literal model-authored edits; quantized local LLM",
            "conventions": "Same prior state, prompt, own-row feedback, id+2 seed and grammar; no resampling initial or first patch; numerical/runtime configuration changed prospectively",
            "inputs": [str(STATE/"public_case.json"), str(STATE/"states.json")],
            "bounds": {"cases": 1, "new_calls": 1, "context": 6144,
                       "max_output_tokens": 1024, "max_input_tokens": 5119,
                       "gpu_layers_requested": 99, "batch": 128, "ubatch": 128,
                       "flash_attn": "on", "cache_type_k": "q8_0", "cache_type_v": "q8_0",
                       "completion_seconds": 180, "phase_seconds": 420, "outer_group_seconds": 480},
            "non_claims": ["No fit/speed guarantee", "No held-out generalization or H23 result",
                           "No isolated causal effect of KV precision", "No QPU or external spending"]},
        "execution_artifacts": artifacts,
        "software": [{"name": "Python", "version": platform.python_version()},
                     {"name": "llama.cpp", "version": "b12359"},
                     {"name": "Qwen3-8B-GGUF", "version": acquisition["model"]["commit"]}],
        "randomness": {"used": True, "generator": "first8hex SHA256(id)+2 modulo2**32", "seed": seed}}
    with contract.open("x") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
    command = [sys.executable, str(RUNNER), "--root", str(ROOT), "--contract", str(contract),
               "--output", str(OUT), "--timeout", str(TIMEOUT),
               "--max-output-bytes", "8388608", "--max-threads", "4"]
    for path in artifacts:
        command.extend(["--input", path])
    for result in ("raw.jsonl", "generation.json", "patch-schema.json", "patch-grammar.gbnf",
                   "native-flags.json", "server.stdout.txt", "server.stderr.txt",
                   "http/000.request.json", "http/000.response.json"):
        command.extend(["--result", str(OUT/"driver"/result)])
    command.extend(["--", *driver_command()])
    return subprocess.call(command, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
