"""Reproducible development experiment. One JSONL row per mathematical input."""
import argparse
import itertools
import json
import math
from pathlib import Path
import random
import time

from .core import MIS_INTENT, PHOTO_INTENT, pipeline
from .verification import greedy_independent_set


def mis_request(n, edges, weights=None):
    return {"intent": MIS_INTENT, "data": {"n": n, "edges": edges, "weights": weights or [1]*n}}


def photon_request(a, b, phi):
    return {"intent": PHOTO_INTENT, "data": {"a": a, "b": b, "phi": phi, "photons": 1, "modes": 2, "loss": 0}}


def foundation_cases():
    for n in range(1, 6):
        possible = list(itertools.combinations(range(n), 2))
        for mask in range(2**len(possible)):
            yield "all_graphs_n%d_mask%d" % (n, mask), mis_request(n, [list(e) for j, e in enumerate(possible) if mask >> j & 1])
    rng = random.Random(20261113)
    for n in range(2, 7):
        for k in range(20):
            edges = [list(e) for e in itertools.combinations(range(n), 2) if rng.random() < .5]
            yield "weighted_n%d_k%d" % (n, k), mis_request(n, edges, [rng.randint(1, 5) for _ in range(n)])
    for i, (a, b, phi) in enumerate(itertools.product([0, math.pi/8, math.pi/4, 3*math.pi/8, math.pi/2],
                                                   [0, math.pi/8, math.pi/4, 3*math.pi/8, math.pi/2],
                                                   [0, math.pi/3, math.pi/2, math.pi, 2*math.pi])):
        yield "photon_grid_%d" % i, photon_request(a, b, phi)


def foundation(output):
    output.mkdir(parents=True, exist_ok=True)
    totals = {"mis": 0, "photon": 0, "failed": 0, "max_probability_error": 0,
              "greedy_suboptimal": 0, "max_greedy_absolute_gap": 0, "states_checked": 0,
              "llm_calls": 0, "qpu_jobs": 0, "external_spend_eur": 0}
    started = time.perf_counter()
    with (output/"raw.jsonl").open("w") as raw:
        for case_id, request in foundation_cases():
            t0 = time.perf_counter()
            result = pipeline(request)
            row = {"id": case_id, "request": request, "result": result, "elapsed_seconds": time.perf_counter()-t0}
            if result["status"] != "solved":
                totals["failed"] += 1
                raise AssertionError(row)
            family = result["problem"]["family"]
            totals[family] += 1
            if family == "mis":
                greedy = greedy_independent_set(result["problem"])
                gap = result["verification"]["oracle_value"] - greedy
                row.update(greedy_value=greedy, greedy_absolute_gap=gap)
                totals["greedy_suboptimal"] += int(gap > 0)
                totals["max_greedy_absolute_gap"] = max(totals["max_greedy_absolute_gap"], gap)
                totals["states_checked"] += result["verification"]["states_checked"]
            else:
                totals["max_probability_error"] = max(totals["max_probability_error"], result["verification"]["max_abs_error"])
            raw.write(json.dumps(row, sort_keys=True, allow_nan=False)+"\n")
    totals["elapsed_seconds"] = time.perf_counter()-started
    (output/"metrics.json").write_text(json.dumps(totals, indent=2)+"\n")
    print(json.dumps(totals, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment", choices=["foundation"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    foundation(args.output)


if __name__ == "__main__":
    main()
