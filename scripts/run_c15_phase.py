"""Run one preregistered C15 phase with a bounded provenance manifest.

No retries or regeneration. Each phase has a fresh output directory.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("initial", "direct", "self", "guided", "feedback", "score"))
    parser.add_argument("--split", choices=("dev", "test"), default="test")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    run = Path("runs/20261114-c15-formulation-repair")
    phase, split = args.phase, args.split
    stem = split + "-" + phase + "-v2"
    output = run / stem
    if output.exists():
        raise SystemExit("Refuse to overwrite " + str(output))
    cases = run / (split + "_cases.json")
    instructions = run / "instructions.v2.txt"
    initial = run / (split + "-initial-v2/raw.jsonl")
    feedback = run / (split + "-feedback-v2/minimal.json")
    inference = phase in ("initial", "direct", "self", "guided")
    artifacts = ["scripts/run_c15_phase.py", "quantage/repair_model.py",
                 "quantage/repair_feedback.py", "quantage/repair_language.py",
                 str(cases), str(instructions), str(run / "protocol.md"),
                 str(run / "amendment-representation-v2.md")]
    if inference:
        artifacts += ["quantage/repair_inference_v2.py",
                      "runs/20261113-c07-public-traces/model-acquisition.json"]
        command = [str(root / ".venv-local-llm/bin/python"), "-m",
                   "quantage.repair_inference_v2", "--cases", str(cases),
                   "--instructions", str(instructions), "--phase", phase,
                   "--output", str(output), "--max-new-tokens", "384"]
        if phase in ("self", "guided"):
            artifacts += [str(initial)]
            command += ["--initial", str(initial)]
        if phase == "guided":
            artifacts += [str(feedback)]
            command += ["--feedback", str(feedback)]
        results = ["raw.jsonl", "generation.json"]
    else:
        artifacts += ["quantage/repair_study_v2.py", str(run / "gold.json"), str(initial)]
        command = [sys.executable, "-m", "quantage.repair_study_v2",
                   phase, "--cases", str(cases), "--gold", str(run / "gold.json"),
                   "--initial", str(initial), "--output", str(output)]
        if phase == "score":
            artifacts += ["quantage/repair_solvers.py"]
            if split == "test":
                for method in ("direct", "self", "guided"):
                    trace = run / ("test-" + method + "-v2/raw.jsonl")
                    artifacts += [str(trace)]
                    command += ["--" + method, str(trace)]
                reports = run / "test-feedback-v2/reports.jsonl"
                artifacts += [str(reports)]
                command += ["--feedback-reports", str(reports)]
            results = ["raw.jsonl", "metrics.json"]
        else:
            results = ["minimal.json", "reports.jsonl"]
    contract = {
        "claim_id": "C15-FORMULATION-REPAIR",
        "mathematics": {
            "assertion_tested": split + " " + phase + ": explicit authored binary ILPs; independent annotated finite-cube fidelity, minimal feedback or actual local inference as applicable",
            "coefficient_domain": "exact integer ILP, float32 CPU inference, float64 HiGHS",
            "conventions": "Qwen2.5-0.5B, T0.2 topk50, fixed per-ID seeds; same initial shared; no gold in inference",
            "inputs": [str(cases)],
            "bounds": {"cases": 8 if split == "dev" else 16, "max_new_tokens": 384,
                       "max_input_tokens": 4096, "n": [4, 7], "witnesses": 3},
            "non_claims": ["No QPU or spending", "No population generalization or novelty proof",
                           "Reference annotations are trusted; no free-text semantic certificate",
                           "Solver choice is ex-post profiling including both solver costs"]
        },
        "execution_artifacts": artifacts,
        "software": [{"name": "Python", "version": "3.9.6"},
                     {"name": "torch", "version": "2.8.0"},
                     {"name": "transformers", "version": "4.45.2"},
                     {"name": "SciPy", "version": "1.13.1"}],
        "randomness": {"used": inference,
                       "generator": "torch per-ID SHA256 first8hex + phase offset" if inference else None,
                       "seed": (0 if phase == "initial" else 1) if inference else None}
    }
    cp = run / ("contract-" + stem + ".json")
    if cp.exists():
        raise SystemExit("Contract already exists " + str(cp))
    cp.write_text(json.dumps(contract, indent=2) + "\n")
    runner = Path("/Users/karimelhoudaigui/.codex/plugins/cache/openai-curated-remote/mathbox/4.0.0/skills/computation-audit/scripts/run_experiment.py")
    argv = [sys.executable, str(runner), "--root", str(root), "--contract", str(cp)]
    for artifact in artifacts:
        argv += ["--input", artifact]
    argv += ["--output", str(output)]
    for result in results:
        argv += ["--result", str(output / result)]
    argv += ["--timeout", "1800", "--max-output-bytes", "4194304",
             "--max-threads", "4", "--"] + command
    raise SystemExit(subprocess.call(argv, cwd=str(root)))


if __name__ == "__main__":
    main()
