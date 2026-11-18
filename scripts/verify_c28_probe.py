"""Verify the frozen C28 probe outcome without consulting any reference labels."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs/20261118-c28-c23-config-probe"
OUT = RUN / "initial-v1"
FREEZE = RUN / "freeze-v1.json"
CONTRACT = RUN / "contract-initial-v1.json"
REPORT = RUN / "verification.json"
ACQUISITION = ROOT / "runs/20261115-c22-model-capacity/acquisition.json"
SERVER_BINARY = ROOT / "research/external/c16-public/runtime/llama-b12359/llama-server"
NATIVE_HELP = ROOT / "runs/20261117-c27-quantized-kv-v2/native-help.json"


def read_json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def verify():
    failures = []
    evidence = {"gate_passed": False, "failures": failures}
    if not FREEZE.is_file() or not CONTRACT.is_file():
        failures.append("frozen protocol artifacts are missing")
        REPORT.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        return evidence

    frozen = read_json(FREEZE)
    contract = read_json(CONTRACT)
    if digest(CONTRACT) != frozen.get("contract_sha256"):
        failures.append("frozen execution contract hash changed")
    acquisition = read_json(ACQUISITION)
    native_help = read_json(NATIVE_HELP).get("filtered_help", "")
    if ("--flash-attn [on|off|auto]" not in native_help
            or "default: 'auto'" not in native_help
            or "--cache-type-k TYPE" not in native_help
            or "(default: f16)" not in native_help):
        failures.append("pinned runtime help does not support the preregistered defaults")
    changed = [
        path for path, expected in frozen.get("sha256", {}).items()
        if not Path(path).is_file() or digest(path) != expected
    ]
    if changed:
        failures.append("frozen source hashes changed: " + ", ".join(changed))

    forbidden_inputs = [
        path for path in contract.get("mathematics", {}).get("inputs", [])
        if "c23" in path.lower() or "gold" in Path(path).name.lower()
    ]
    if forbidden_inputs:
        failures.append("C23 corpus or gold listed as a model input")

    manifest_path = OUT / "manifest.json"
    generation_path = OUT / "driver/generation.json"
    raw_path = OUT / "driver/raw.jsonl"
    if not manifest_path.is_file():
        failures.append("runner manifest is missing")
        manifest = {}
    else:
        manifest = read_json(manifest_path)
        run = manifest.get("run", {})
        if (run.get("status") != "completed" or run.get("exit_status") != 0
                or run.get("missing_results") or run.get("invalid_results")):
            failures.append("bounded runner did not complete with all declared results")

    generation = read_json(generation_path) if generation_path.is_file() else {}
    if not generation:
        failures.append("driver generation record is missing")
    else:
        for key, expected in (
            ("runtime_tag", "b12359"),
            ("revision", acquisition.get("model", {}).get("commit")),
            ("status", "completed"),
            ("phase", "initial"),
            ("round", 0),
            ("planned", 1),
            ("completed", 1),
            ("max_new_tokens", 1024),
            ("max_input_tokens", 5119),
            ("context", 6144),
            ("server_reaped", True),
        ):
            if generation.get(key) != expected:
                failures.append(f"generation {key} differs from preregistration")
        if generation.get("error") is not None or generation.get("cleanup_error") is not None:
            failures.append("driver or cleanup error is recorded")
        if generation.get("reference_or_gold_input") is not False:
            failures.append("reference/gold input is not explicitly absent")
        if generation.get("model", {}).get("sha256") != acquisition.get("model", {}).get("sha256_expected"):
            failures.append("model hash differs from the frozen acquisition")
        if (generation.get("binary", {}).get("sha256") != digest(SERVER_BINARY)):
            failures.append("runtime binary hash differs from the local pinned binary")
        if generation.get("input_tokens", 5120) > 5119:
            failures.append("prompt exceeds the fixed output reserve")
        if not 0 < generation.get("output_tokens", 0) <= 1024:
            failures.append("output token count is outside its registered cap")

        observed = generation.get("backend_observed", {})
        if observed.get("device") != "Metal" or not observed.get("offloaded_gpu_layers"):
            failures.append("Metal tensor offload was not observed")
        if generation.get("backend_requested") != {
            "device": "MTL0", "gpu_layers": 30, "cpu_threads": 4
        }:
            failures.append("requested C23 backend configuration differs")

        command = generation.get("server_command", [])
        expected_flags = {
            "--ctx-size": "6144",
            "--threads": "4",
            "--threads-batch": "4",
            "--batch-size": "128",
            "--ubatch-size": "128",
            "--n-gpu-layers": "30",
            "--device": "MTL0",
        }
        for flag, value in expected_flags.items():
            if flag not in command or command[command.index(flag) + 1] != value:
                failures.append(f"server command differs for {flag}")
        if any(flag in command for flag in (
            "--flash-attn", "--cache-type-k", "--cache-type-v"
        )):
            failures.append("C28 command overrides C23 runtime defaults")

    rows = []
    if raw_path.is_file():
        rows = [json.loads(line) for line in raw_path.read_text(encoding="utf-8").splitlines()]
    if len(rows) != 1:
        failures.append("raw output does not contain exactly one response")
    else:
        row = rows[0]
        if row.get("id") != frozen.get("selection", {}).get("case_id"):
            failures.append("response case ID differs from frozen selection")
        if row.get("phase") != "initial" or row.get("round") != 0:
            failures.append("response phase differs from preregistration")
        if row.get("finish_reason") != "eos":
            failures.append("response did not terminate with EOS")
        if row.get("parsed", {}).get("valid") is not True:
            failures.append("response is not parser-valid")
        evidence["response"] = {
            "id": row.get("id"),
            "input_tokens": row.get("input_tokens"),
            "output_tokens": row.get("output_tokens"),
            "finish_reason": row.get("finish_reason"),
            "parser_valid": row.get("parsed", {}).get("valid"),
        }

    evidence.update({
        "gate_passed": not failures,
        "runner_status": manifest.get("run", {}).get("status"),
        "runner_exit_status": manifest.get("run", {}).get("exit_status"),
        "generation_status": generation.get("status"),
        "server_exit_status": generation.get("server_exit_status"),
        "server_reaped": generation.get("server_reaped"),
        "backend_observed": generation.get("backend_observed"),
        "backend_requested": generation.get("backend_requested"),
        "input_sha256": {
            path: digest(path) for path in frozen.get("sha256", {})
            if Path(path).is_file()
        },
        "c23_corpus_or_gold_inputs": forbidden_inputs,
        "claim_scope": "single development-case runtime gate only; not a fidelity or population result",
    })
    REPORT.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return evidence


if __name__ == "__main__":
    result = verify()
    print(json.dumps({"gate_passed": result["gate_passed"], "failures": result["failures"]}))
    raise SystemExit(0 if result["gate_passed"] else 1)
