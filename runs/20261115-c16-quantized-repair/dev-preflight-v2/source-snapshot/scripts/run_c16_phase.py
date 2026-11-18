"""One bounded, pinned C16 phase; no retry, no overwrite, no external inference."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("preflight", "remaining", "initial", "direct",
                                          "self", "guided", "feedback", "score"))
    parser.add_argument("--split", choices=("dev", "test"), default="test")
    parser.add_argument("--attempt", type=int, default=1)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    run = Path("runs/20261115-c16-quantized-repair")
    phase = args.phase
    split = "dev" if phase in ("preflight", "remaining") else args.split
    if args.attempt < 1:
        raise SystemExit("positive attempt required")
    suffix = "-v" + str(args.attempt)
    output = run / (split + "-" + phase + suffix)
    if output.exists():
        raise SystemExit("refuse overwrite " + str(output))
    actual_phase = "initial" if phase in ("preflight", "remaining") else phase
    case_file = {"preflight": "dev_preflight_cases.json",
                 "remaining": "dev_remaining_cases.json"}.get(phase, split + "_cases.json")
    cases = run / case_file
    instructions = run / ("instructions.v1.txt" if split == "dev" else "instructions.frozen.txt")
    initial = run / (split + "-initial-v1/driver/raw.jsonl")
    feedback = run / (split + "-feedback-v1/minimal.json")
    inference = actual_phase in ("initial", "direct", "self", "guided")
    artifacts = ["scripts/run_c16_phase.py", "quantage/repair_model.py",
                 "quantage/repair_feedback.py", "quantage/repair_language.py",
                 str(cases), str(instructions), str(run / "protocol.md")]
    if inference:
        acquisition_path = run / "acquisition.json"
        acquisition = json.loads(acquisition_path.read_text())
        runtime = Path("research/external/c16-public/runtime")
        binary = runtime / "llama-b12359/llama-server"
        model = Path("research/external/c16-public/models") / acquisition["model"]["file"]
        artifacts += ["quantage/repair_llama_inference.py", str(acquisition_path),
                      str(model)] + [str(runtime / row["path"])
                                     for row in acquisition["runtime_extraction"]["files"]]
        command = [sys.executable, "-m", "quantage.repair_llama_inference",
                   "--cases", str(cases), "--instructions", str(instructions),
                   "--phase", actual_phase, "--output", str(output / "driver"),
                   "--server-binary", str(binary), "--model", str(model),
                   "--acquisition", str(acquisition_path), "--execute"]
        if actual_phase in ("self", "guided"):
            artifacts += [str(initial)]
            command += ["--initial", str(initial)]
        if actual_phase == "guided":
            artifacts += [str(feedback)]
            command += ["--feedback", str(feedback)]
        results = ["driver/raw.jsonl", "driver/generation.json",
                   "driver/server.stdout.txt", "driver/server.stderr.txt"]
    else:
        artifacts += ["quantage/repair_study_c16.py", str(run / "gold.json"), str(initial)]
        command = [sys.executable, "-m", "quantage.repair_study_c16", phase,
                   "--cases", str(cases), "--gold", str(run / "gold.json"),
                   "--initial", str(initial), "--output", str(output)]
        if phase == "score":
            artifacts += ["quantage/repair_solvers.py"]
            if split == "test":
                for method in ("direct", "self", "guided"):
                    trace = run / ("test-" + method + "-v1/driver/raw.jsonl")
                    artifacts += [str(trace)]
                    command += ["--" + method, str(trace)]
                reports = run / "test-feedback-v1/reports.jsonl"
                artifacts += [str(reports)]
                command += ["--feedback-reports", str(reports)]
            results = ["raw.jsonl", "metrics.json"]
        else:
            results = ["minimal.json", "reports.jsonl"]
    contract = {
        "claim_id": "C16-QUANTIZED-REPAIR",
        "mathematics": {
            "assertion_tested": split + " " + phase + ": actual authored multi-constraint binary ILPs, oracle feedback or finite scoring as applicable",
            "coefficient_domain": "exact integer ILP; quantized Q4_K_M LLM; float64 HiGHS",
            "conventions": "same shape schema, known primitive clauses, per-ID SHA256 seeds+round; trusted annotated oracle; no gold in inference",
            "inputs": [str(cases)],
            "bounds": {"cases": 2 if phase == "preflight" else 6 if phase == "remaining" else 8 if split == "dev" else 16,
                       "max_new_tokens": 384, "context_tokens": 2048, "n": [4, 7],
                       "max_completion_seconds": 180},
            "non_claims": ["No QPU, spending or free-text semantic guarantee",
                           "No isolated quantization/grammar causal effect",
                           "No population confidence interval or general novelty",
                           "Direct token probability is a pinned-API selection heuristic",
                           "Solver choice is ex-post profiling, cost of both included"]
        },
        "execution_artifacts": artifacts,
        "software": [{"name": "Python", "version": "3.9.6"},
                     {"name": "llama.cpp", "version": "1.0.0-dev build12359 b1b770d90"},
                     {"name": "SciPy", "version": "1.13.1"}],
        "randomness": {"used": inference,
                       "generator": "llama.cpp per-ID SHA256 first8hex + round offset" if inference else None,
                       "seed": (0 if actual_phase == "initial" else 1) if inference else None}
    }
    cp = run / ("contract-" + split + "-" + phase + suffix + ".json")
    if cp.exists():
        raise SystemExit("contract already exists " + str(cp))
    cp.write_text(json.dumps(contract, indent=2) + "\n")
    runner = "/Users/karimelhoudaigui/.codex/plugins/cache/openai-curated-remote/mathbox/4.0.0/skills/computation-audit/scripts/run_experiment.py"
    argv = [sys.executable, runner, "--root", str(root), "--contract", str(cp)]
    for artifact in artifacts:
        argv += ["--input", artifact]
    argv += ["--output", str(output)]
    for result in results:
        argv += ["--result", str(output / result)]
    argv += ["--timeout", "480" if phase == "preflight" else "1800",
             "--max-output-bytes", "4194304", "--max-threads", "4", "--"] + command
    raise SystemExit(subprocess.call(argv, cwd=str(root)))


if __name__ == "__main__":
    main()
