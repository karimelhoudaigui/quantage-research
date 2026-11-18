"""Mutation experiment: synthetic propositions, never simulated LLM responses."""
import argparse
import copy
import json
import math
from pathlib import Path
import time
from .benchmark import foundation_cases
from .core import formulate, understand, solve_qubo, optical_probabilities
from .verification import independent_set_oracle, optical_oracle, verify


def mutations(problem, base):
    names = (["linear_sign", "zero_penalty", "boundary_penalty", "drop_edge",
              "positive_scaling", "constant_shift", "double_penalty"] if problem["family"] == "mis" else
             ["omit_phase", "negate_phase", "half_angles", "incoherent", "amplitude_output",
              "global_phase", "reverse_order", "phase_other_mode"])
    for name in names:
        m = copy.deepcopy(base)
        if name == "linear_sign": m["linear"] = [-x for x in m["linear"]]
        elif name in ("zero_penalty", "boundary_penalty", "double_penalty"):
            value = {"zero_penalty": 0, "boundary_penalty": max(problem["weights"]),
                     "double_penalty": 2*base["penalty"]}[name]
            m["quadratic"] = [[i, j, value] for i, j, _ in m["quadratic"]]
            m["penalty"] = value
        elif name == "drop_edge": m["quadratic"] = m["quadratic"][1:]
        elif name == "positive_scaling":
            m["linear"] = [3*x for x in m["linear"]]
            m["quadratic"] = [[i, j, 3*v] for i, j, v in m["quadratic"]]
            m["penalty"] *= 3
        elif name == "constant_shift": m["constant"] += 7
        elif name == "omit_phase": m["phi"] = 0
        elif name == "negate_phase": m["phi"] *= -1
        elif name == "half_angles":
            m["a"] /= 2
            m["b"] /= 2
        elif name == "incoherent": m["coherent"] = False
        elif name == "amplitude_output": m["output"] = "real_amplitudes"
        elif name == "global_phase": m["global_phase"] = 1.234
        elif name == "reverse_order": m["order"] = "R_a P R_b"
        elif name == "phase_other_mode": m["phase_mode"] = 0
        yield name, m


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    summary = {}
    started = time.perf_counter()
    with (output/"raw.jsonl").open("w") as raw:
        for case_id, request in foundation_cases():
            if case_id.startswith("all_graphs_n5_"):
                continue
            p = understand(request)
            base = formulate(p)
            for name, m in mutations(p, base):
                if p["family"] == "mis":
                    result = solve_qubo(m)
                    optimum, target = independent_set_oracle(p)
                    actual = {tuple(x) for x in result["solutions"]}
                    equivalent = actual == target
                    first = result["solutions"][0]
                    single_solution_check = (all(not (first[i] and first[j]) for i, j in p["edges"])
                                             and sum(w*x for w, x in zip(p["weights"], first)) == optimum)
                else:
                    actual = optical_probabilities(m)
                    target = optical_oracle(p)
                    equivalent = max(abs(a-b) for a, b in zip(actual, target)) <= 1e-12
                    single_solution_check = (abs(sum(actual)-1) <= 1e-12 and all(0 <= x <= 1 for x in actual))
                    result = {"probabilities": actual}
                checks = {"shape_only": True, "one_solution_or_normalization": single_solution_check,
                          "syntax_identity": m == base, "full_oracle": verify(p, m)["valid"]}
                key = p["family"]+"/"+name
                group = summary.setdefault(key, {"cases": 0, "effective": 0,
                    "methods": {k: {"false_accept": 0, "false_reject": 0, "rejected": 0} for k in checks}})
                group["cases"] += 1
                group["effective"] += int(not equivalent)
                for k, accepted in checks.items():
                    group["methods"][k]["false_accept"] += int(accepted and not equivalent)
                    group["methods"][k]["false_reject"] += int(not accepted and equivalent)
                    group["methods"][k]["rejected"] += int(not accepted)
                raw.write(json.dumps({"id": case_id, "request": request, "mutation": name,
                                      "proposal": m, "output": result, "equivalent_on_instance": equivalent,
                                      "accepted": checks}, sort_keys=True)+"\n")
    metrics = {"groups": summary, "elapsed_seconds": time.perf_counter()-started,
               "interpretation": "synthetic mutation study on development cases; oracle-defined equivalence"}
    (output/"metrics.json").write_text(json.dumps(metrics, indent=2)+"\n")
    print(json.dumps({"cases": sum(x["cases"] for x in summary.values()),
                      "effective": sum(x["effective"] for x in summary.values()),
                      "false_accept_weak": sum(x["methods"]["one_solution_or_normalization"]["false_accept"] for x in summary.values()),
                      "false_accept_full": sum(x["methods"]["full_oracle"]["false_accept"] for x in summary.values())}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    run(parser.parse_args().output)
