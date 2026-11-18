"""Audit the recorded C28 attempt without loading a model or reading C23 data."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs/20261118-c28-c23-config-probe"
OUT = RUN / "initial-v1"
FREEZE = RUN / "freeze-v1.json"
CONTRACT = RUN / "contract-initial-v1.json"
REPORT = RUN / "verification-final.json"
CASE_ID = "765e3caadee5"
SOURCE_CASES = ROOT / "runs/20261115-c19-instruct-repair/test_cases.json"
ACQUISITION = ROOT / "runs/20261115-c22-model-capacity/acquisition.json"
NATIVE_HELP = ROOT / "runs/20261117-c27-quantized-kv-v2/native-help.json"
SERVER_BINARY = ROOT / "research/external/c16-public/runtime/llama-b12359/llama-server"


def read_json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def add_check(checks, name, passed, details=None):
    checks[name] = {"passed": bool(passed), "details": details}


def audit():
    frozen = read_json(FREEZE)
    contract = read_json(CONTRACT)
    manifest_path = OUT / "manifest.json"
    generation_path = OUT / "driver/generation.json"
    request_path = OUT / "driver/http/000.request.json"
    response_path = OUT / "driver/http/000.response.json"
    raw_path = OUT / "driver/raw.jsonl"
    stderr_path = OUT / "driver/server.stderr.txt"
    manifest = read_json(manifest_path)
    generation = read_json(generation_path)
    request = read_json(request_path)
    raw_rows = [
        json.loads(line)
        for line in raw_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
    acquisition = read_json(ACQUISITION)
    native_help = read_json(NATIVE_HELP).get("help", "")
    runner = manifest.get("run", {})
    prompt_tokens = len(request.get("prompt", []))
    server_command = generation.get("server_command", [])
    failures = []
    checks = {}

    changed = [
        path for path, expected in frozen.get("sha256", {}).items()
        if not (ROOT / path).is_file() or digest(ROOT / path) != expected
    ]
    add_check(checks, "frozen_sources_unchanged", not changed, changed)
    add_check(
        checks,
        "execution_contract_unchanged",
        digest(CONTRACT) == frozen.get("contract_sha256"),
        frozen.get("contract_sha256"),
    )

    source_cases = read_json(SOURCE_CASES)
    candidates = [case for case in source_cases if case.get("data", {}).get("n") == 7]
    selected = max(candidates, key=lambda case: (len(case["intention"]), case["id"]))
    case = read_json(RUN / "case.json")
    add_check(
        checks,
        "selected_case_matches_C19_development_source",
        selected.get("id") == CASE_ID and case == [selected],
        {"case_id": selected.get("id"), "n7_cases": len(candidates),
         "intention_characters": len(selected.get("intention", ""))},
    )
    inputs = contract.get("mathematics", {}).get("inputs", [])
    forbidden_inputs = [
        path for path in inputs
        if path.startswith("runs/20261115-c23-compositional-repair/")
        or Path(path).name.lower() in {"gold.json", "private_gold.json"}
        or "private_gold" in Path(path).name.lower()
    ]
    add_check(checks, "no_reserved_C23_corpus_or_gold_input", not forbidden_inputs, forbidden_inputs)

    help_ok = (
        "--flash-attn [on|off|auto]" in native_help
        and "default: 'auto'" in native_help
        and "--cache-type-k TYPE" in native_help
        and "(default: f16)" in native_help
    )
    add_check(checks, "pinned_runtime_default_help", help_ok)
    actual_flags = {
        "flash_attn_auto": "flash_attn            = auto" in stderr,
        "kv_k_f16": "K (f16):" in stderr,
        "kv_v_f16": "V (f16):" in stderr,
    }
    add_check(checks, "observed_C23_runtime_defaults", all(actual_flags.values()), actual_flags)

    requested_flags = {
        "--ctx-size": "6144",
        "--threads": "4",
        "--threads-batch": "4",
        "--batch-size": "128",
        "--ubatch-size": "128",
        "--n-gpu-layers": "30",
        "--device": "MTL0",
    }
    command_ok = all(
        flag in server_command and server_command[server_command.index(flag) + 1] == value
        for flag, value in requested_flags.items()
    )
    no_overrides = not any(
        flag in server_command
        for flag in ("--flash-attn", "--cache-type-k", "--cache-type-v")
    )
    add_check(checks, "requested_server_configuration", command_ok and no_overrides)
    observed = generation.get("backend_observed", {})
    add_check(
        checks,
        "Metal_tensor_offload_observed",
        observed.get("device") == "Metal" and observed.get("offloaded_gpu_layers") == 30,
        observed,
    )

    response_exists = response_path.is_file()
    parser_valid = len(raw_rows) == 1 and raw_rows[0].get("parsed", {}).get("valid") is True
    complete_response = (
        response_exists
        and parser_valid
        and raw_rows[0].get("finish_reason") == "eos"
        and generation.get("status") == "completed"
        and generation.get("completed") == 1
    )
    add_check(
        checks,
        "complete_parser_valid_EOS_response",
        complete_response,
        {"response_file_exists": response_exists, "raw_rows": len(raw_rows),
         "generation_status": generation.get("status"),
         "completed": generation.get("completed")},
    )
    runner_complete = (
        runner.get("status") == "completed"
        and runner.get("exit_status") == 0
        and not runner.get("missing_results")
        and not runner.get("invalid_results")
    )
    add_check(checks, "bounded_runner_completed", runner_complete, runner)
    reaped = generation.get("server_reaped") is True and generation.get("cleanup_error") is None
    add_check(checks, "server_reaped_without_cleanup_error", reaped)

    timeout_observed = (
        generation.get("status") == "partial_error"
        and "TimeoutError: signal 14" in str(generation.get("error"))
        and generation.get("completed") == 0
        and not response_exists
    )
    add_check(
        checks,
        "single_request_timeout_recorded",
        timeout_observed,
        {"error": generation.get("error"), "request_timeout_seconds":
         generation.get("request_timeout_seconds")},
    )
    oom_markers = ("MetalInsufficientMemory", "failed to allocate", "out of memory")
    explicit_oom = any(marker.lower() in stderr.lower() for marker in oom_markers)
    add_check(checks, "explicit_OOM_log_marker", not explicit_oom, explicit_oom)

    # These are integrity checks on the recorded outcome, not the C28 pass criterion.
    for name, check in checks.items():
        if name in {
            "frozen_sources_unchanged",
            "execution_contract_unchanged",
            "selected_case_matches_C19_development_source",
            "no_reserved_C23_corpus_or_gold_input",
            "pinned_runtime_default_help",
            "observed_C23_runtime_defaults",
            "requested_server_configuration",
            "Metal_tensor_offload_observed",
            "server_reaped_without_cleanup_error",
            "single_request_timeout_recorded",
            "explicit_OOM_log_marker",
        } and not check["passed"]:
            failures.append(name)

    gate_passed = complete_response and runner_complete and reaped
    evidence_paths = (
        FREEZE, CONTRACT, RUN / "protocol.md", RUN / "case.json",
        manifest_path, generation_path, request_path, raw_path, stderr_path,
    )
    report = {
        "cycle": "C28",
        "cycle_status": "complete",
        "gate_status": "passed" if gate_passed else "blocked",
        "gate_passed": gate_passed,
        "integrity_checks_passed": not failures,
        "integrity_failures": failures,
        "primary_outcome": "request_timeout_without_complete_response",
        "interpretation": (
            "The exact 180-second request bound expired before the client received a complete "
            "response. The driver recorded zero completed rows and no response file; this does "
            "not establish that zero tokens were sampled by the server."
        ),
        "measurements": {
            "runner_seconds": runner.get("runtime_seconds"),
            "driver_wall_seconds": generation.get("wall_seconds"),
            "model_load_seconds": generation.get("load_seconds"),
            "request_timeout_seconds": generation.get("request_timeout_seconds"),
            "prompt_tokens_in_HTTP_request": prompt_tokens,
            "prompt_tokens_logged_by_server": 740 if "task.n_tokens = 740" in stderr else None,
            "prompt_progress_tokens_logged": 640 if "n_tokens =    640" in stderr else None,
            "prompt_progress_seconds": 126.05 if "t = 126.05 s" in stderr else None,
            "client_recorded_output_tokens": generation.get("output_tokens"),
            "actual_generated_token_count": None,
        },
        "runtime": {
            "tag": generation.get("runtime_tag"),
            "revision": generation.get("revision"),
            "backend_requested": generation.get("backend_requested"),
            "backend_observed": observed,
            "flash_attention": "auto" if actual_flags["flash_attn_auto"] else None,
            "cache_k": "f16" if actual_flags["kv_k_f16"] else None,
            "cache_v": "f16" if actual_flags["kv_v_f16"] else None,
            "server_reaped": generation.get("server_reaped"),
            "server_exit_status": generation.get("server_exit_status"),
            "cleanup_error": generation.get("cleanup_error"),
            "explicit_OOM_log_marker": explicit_oom,
        },
        "runner": {
            "status": runner.get("status"),
            "exit_status": runner.get("exit_status"),
            "missing_results": runner.get("missing_results"),
            "invalid_results": runner.get("invalid_results"),
        },
        "checks": checks,
        "c23_corpus_or_gold_inputs": forbidden_inputs,
        "audit_scope": "offline evidence audit; no model, network, corpus, or gold access",
        "independent_review": "No separate reviewer; audit is by the integrator.",
        "preliminary_checker": {
            "file": "runs/20261118-c28-c23-config-probe/verification.json",
            "superseded_by": "runs/20261118-c28-c23-config-probe/verification-final.json",
            "false_positives": [
                "Substring matching treated the C28 directory name as a C23 corpus path.",
                "The first checker looked for filtered_help at the wrong JSON level."
            ],
            "gate_outcome_remains_blocked": True,
        },
        "sha256": {str(path.relative_to(ROOT)): digest(path) for path in evidence_paths},
        "audit_script_sha256": digest(Path(__file__)),
    }
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return report


if __name__ == "__main__":
    result = audit()
    print(json.dumps({
        "cycle_status": result["cycle_status"],
        "gate_status": result["gate_status"],
        "gate_passed": result["gate_passed"],
        "integrity_checks_passed": result["integrity_checks_passed"],
        "integrity_failures": result["integrity_failures"],
    }, ensure_ascii=False))
