"""Freeze and run the single prospective C28 local viability probe."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RUN = Path("runs/20261118-c28-c23-config-probe")
SOURCE_RUN = Path("runs/20261115-c19-instruct-repair")
ACQUISITION = Path("runs/20261115-c22-model-capacity/acquisition.json")
RUNTIME = Path("research/external/c16-public/runtime")
MODEL = Path("research/external/c22-public/models/Qwen3-8B-Q4_K_M.gguf")
DRIVER = "quantage.repair_iterative_full_inference"
RUNNER = Path("/Users/karimelhoudaigui/.codex/plugins/cache/openai-curated-remote/mathbox/4.0.0/skills/computation-audit/scripts/run_experiment.py")
OUT = RUN / "initial-v1"
FREEZE = RUN / "freeze-v1.json"
CONTRACT = RUN / "contract-initial-v1.json"
TIMEOUT = 1800
CASE_ID = "765e3caadee5"

SOURCE_CASES = SOURCE_RUN / "test_cases.json"
CASE_FILE = RUN / "case.json"
INSTRUCTIONS = SOURCE_RUN / "instructions.frozen.txt"


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def json_file(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def driver_command():
    return [
        "/usr/bin/caffeinate", "-i", "-t", str(TIMEOUT), sys.executable,
        "-m", DRIVER, "--cases", str(CASE_FILE), "--instructions", str(INSTRUCTIONS),
        "--phase", "initial", "--round", "0", "--output", str(OUT / "driver"),
        "--server-binary", str(RUNTIME / "llama-b12359/llama-server"),
        "--model", str(MODEL), "--acquisition", str(ACQUISITION),
        "--max-new-tokens", "1024", "--case-limit", "1", "--execute",
    ]


def checked_artifacts():
    source_cases = json_file(SOURCE_CASES)
    candidates = [case for case in source_cases if case.get("data", {}).get("n") == 7]
    if not candidates:
        raise ValueError("the frozen C19 development source has no n=7 case")
    selected = max(candidates, key=lambda case: (len(case["intention"]), case["id"]))
    if selected["id"] != CASE_ID or json_file(CASE_FILE) != [selected]:
        raise ValueError("C28 case must be the exact preregistered longest n=7 C19 development case")
    acquisition = json_file(ACQUISITION)
    if acquisition.get("status") != "completed" or acquisition.get("runtime_tag") != "b12359":
        raise ValueError("completed pinned b12359 acquisition required")
    if acquisition.get("model", {}).get("commit") != "7c41481f57cb95916b40956ab2f0b139b296d974":
        raise ValueError("unexpected pinned Qwen3-8B model revision")
    runtime_files = []
    for entry in acquisition["runtime_extraction"]["files"]:
        relative = Path(entry["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("runtime acquisition path escapes extraction")
        runtime_files.append(str(RUNTIME / relative))
    artifacts = [
        "scripts/run_c28_probe.py",
        "scripts/verify_c28_probe.py",
        "quantage/repair_iterative_full_inference.py",
        "quantage/repair_language.py",
        "quantage/repair_model.py",
        "runs/20261118-c28-c23-config-probe/protocol.md",
        "runs/20261118-c28-c23-config-probe/c23-gate-amendment.md",
        str(CASE_FILE),
        str(SOURCE_CASES),
        str(SOURCE_RUN / "protocol-test.md"),
        str(SOURCE_RUN / "test-corpus-provenance.md"),
        str(INSTRUCTIONS),
        str(ACQUISITION),
        "runs/20261116-c25-partial-gpu/protocol.md",
        "runs/20261116-c25-partial-gpu/before-verification.json",
        "runs/20261116-c25-partial-gpu/guided-round2-v1/manifest.json",
        "runs/20261116-c25-partial-gpu/guided-round2-v1/driver/generation.json",
        "runs/20261117-c27-quantized-kv-v2/protocol.md",
        "runs/20261117-c27-quantized-kv-v2/summary.md",
        "runs/20261117-c27-quantized-kv-v2/native-help.json",
        "research/c23-v2-code-notes.md",
        str(MODEL),
        *runtime_files,
    ]
    artifacts = list(dict.fromkeys(artifacts))
    missing = [path for path in artifacts if not Path(path).is_file()]
    if missing:
        raise FileNotFoundError("missing frozen C28 artifacts: " + ", ".join(missing))
    return artifacts, acquisition


def make_freeze():
    if Path.cwd().resolve() != ROOT:
        raise ValueError("freeze from project root")
    if OUT.exists() or FREEZE.exists() or CONTRACT.exists():
        raise ValueError("C28 is one attempt only; refuse output/freeze/contract reuse")
    artifacts, acquisition = checked_artifacts()
    source_hashes = {
        path: digest(path)
        for path in artifacts
        if not path.startswith("research/external/")
    }
    seed = int(hashlib.sha256(CASE_ID.encode("utf-8")).hexdigest()[:8], 16)
    if seed == 2**32 - 1:
        raise ValueError("derived seed is reserved sentinel")
    freeze_data = {
        "run": "20261118-c28-c23-config-probe",
        "development_only": True,
        "authorized_by_user": True,
        "c23_corpus_or_gold_read": False,
        "budget": {"cases": 1, "calls": 1, "external_eur": 0, "outer_seconds": TIMEOUT},
        "selection": {
            "source": str(SOURCE_CASES),
            "rule": "longest intention among n=7 cases; ties by lexicographically greatest id",
            "case_id": CASE_ID,
        },
        "randomness": {
            "used": True,
            "generator": "first8hex SHA256(id) modulo 2**32",
            "seed": seed,
        },
        "software": {
            "python": platform.python_version(),
            "llama_cpp": "b12359",
            "model_revision": acquisition["model"]["commit"],
        },
        "sha256": source_hashes,
    }
    with FREEZE.open("x", encoding="utf-8") as handle:
        json.dump(freeze_data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())

    artifacts.append(str(FREEZE))
    contract_data = {
        "claim_id": "C28-C23-CONFIG-VIABILITY",
        "mathematics": {
            "assertion_tested": "One parser-valid complete initial response under the C23 runtime configuration on one n=7 development case",
            "coefficient_domain": "operational viability only; no fidelity score or solver comparison",
            "conventions": "one frozen case and generic instruction; one deterministic initial call; no retry or reference/gold input",
            "inputs": [str(CASE_FILE), str(INSTRUCTIONS)],
            "bounds": {
                "cases": 1,
                "new_calls": 1,
                "context": 6144,
                "max_output_tokens": 1024,
                "max_input_tokens": 5119,
                "gpu_layers_requested": 30,
                "device": "MTL0",
                "cpu_threads": 4,
                "batch": 128,
                "ubatch": 128,
                "flash_attention": "auto (runtime default)",
                "cache_type_k": "f16 (runtime default)",
                "cache_type_v": "f16 (runtime default)",
                "request_seconds": 180,
                "phase_seconds": 1650,
                "outer_group_seconds": TIMEOUT,
            },
            "non_claims": [
                "No population or held-out claim",
                "No memory-margin or speed guarantee",
                "No C23 corpus performance claim",
                "No QPU or external spending",
            ],
        },
        "execution_artifacts": artifacts,
        "software": [
            {"name": "Python", "version": platform.python_version()},
            {"name": "llama.cpp", "version": "b12359"},
            {"name": "Qwen3-8B-GGUF", "version": acquisition["model"]["commit"]},
        ],
        "randomness": freeze_data["randomness"],
    }
    with CONTRACT.open("x", encoding="utf-8") as handle:
        json.dump(contract_data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    freeze_data["contract_sha256"] = digest(CONTRACT)
    FREEZE.write_text(
        json.dumps(freeze_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return artifacts


def execute(artifacts):
    if OUT.exists():
        raise ValueError("C28 has already been attempted; no retry")
    frozen = json_file(FREEZE)
    if digest(CONTRACT) != frozen.get("contract_sha256"):
        raise ValueError("frozen execution contract changed")
    for path, expected in frozen["sha256"].items():
        if digest(path) != expected:
            raise ValueError("frozen source changed: " + path)
    command = [
        sys.executable, str(RUNNER), "--root", str(ROOT),
        "--contract", str(CONTRACT), "--output", str(OUT),
        "--timeout", str(TIMEOUT), "--max-output-bytes", "8388608",
        "--max-threads", "4",
    ]
    for path in artifacts:
        command.extend(["--input", path])
    for result in (
        "raw.jsonl", "generation.json", "form-schema.json", "form-grammar.gbnf",
        "server.stdout.txt", "server.stderr.txt",
        "http/000.template.request.json", "http/000.template.response.json",
        "http/000.prompt.txt", "http/000.request.json", "http/000.response.json",
    ):
        command.extend(["--result", str(OUT / "driver" / result)])
    command.extend(["--", *driver_command()])
    return subprocess.call(command, cwd=ROOT)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--freeze", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    if args.dry_run:
        print(json.dumps({"prospective_only": True, "timeout_seconds": TIMEOUT,
                          "driver_command": driver_command()}, indent=2))
        return 0
    if Path.cwd().resolve() != ROOT:
        raise ValueError("run from project root")
    if args.freeze:
        artifacts = make_freeze()
        print(json.dumps({"frozen": True, "artifacts": len(artifacts),
                          "freeze": str(FREEZE), "contract": str(CONTRACT)}, indent=2))
        return 0
    if not FREEZE.is_file() or not CONTRACT.is_file():
        raise FileNotFoundError("run --freeze before --execute")
    artifacts, _ = checked_artifacts()
    artifacts.append(str(FREEZE))
    return execute(artifacts)


if __name__ == "__main__":
    raise SystemExit(main())
