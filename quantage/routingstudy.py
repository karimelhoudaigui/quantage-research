import argparse
import json
from pathlib import Path
import time
from .routing import review_route


def run(cases_path, policy_path, output):
    cases, policy = json.loads(cases_path.read_text()), json.loads(policy_path.read_text())
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    methods = {k: {"tp": 0, "tn": 0, "fp": 0, "fn": 0} for k in ("name_only", "modality", "guarded")}
    physical_permissions = 0
    with (output/"raw.jsonl").open("w") as raw:
        for case in cases:
            results = {}
            for method, counts in methods.items():
                result = review_route(case["problem"], case["proposal"], policy, method)
                accepted = result["acceptable_recommendation"]
                correct = case["expected_acceptable"]
                counts[("t" if accepted == correct else "f")+("p" if accepted else "n")] += 1
                results[method] = result
            physical_permissions += int(results["guarded"]["execution_permission"] == "allowed_qpu")
            raw.write(json.dumps({"case": case, "results": results}, sort_keys=True)+"\n")
    metrics = {"cases": len(cases), "methods": methods, "physical_permissions": physical_permissions,
               "elapsed_seconds": time.perf_counter()-started,
               "non_claim": "Hand-authored documentary labels, not physical feasibility or agent performance."}
    (output/"metrics.json").write_text(json.dumps(metrics, indent=2)+"\n")
    print(json.dumps(metrics))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.cases, args.policy, args.output)
