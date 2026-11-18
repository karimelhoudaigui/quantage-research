"""Frozen-engine challenge set. Keywords are a baseline, never a mock LLM."""
import argparse
import copy
import itertools
import json
import math
from pathlib import Path
import random
import time
from .benchmark import mis_request, photon_request
from .core import MIS_INTENT, PHOTO_INTENT, pipeline


def build_cases():
    rng = random.Random(20261114)
    canonical = []
    for n in (7, 8, 8):
        edges = [list(e) for e in itertools.combinations(range(n), 2) if rng.random() < .4]
        canonical.append(mis_request(n, edges, [rng.randint(1, 5) for _ in range(n)]))
    for _ in range(3):
        canonical.append(photon_request(*(rng.uniform(0, math.pi) for _ in range(3))))
    cases = []
    def add(group, i, request, equivalent, reason):
        cases.append({"id":group+"_"+str(i), "group":group, "request":request,
                      "contract_equivalent":equivalent, "label_reason":reason})
    for i, req in enumerate(canonical):
        add("canonical", i, req, True, "Supported contract, new sizes or angles")
    paraphrases = ["Maximiser le poids d'un ensemble indépendant.",
                   "Find a maximum-weight independent set.",
                   "Select nonadjacent vertices of maximum total weight.",
                   "Calculate ideal one-photon detection probabilities.",
                   "Calculer les probabilités de sortie idéales pour un photon.",
                   "Evaluate lossless single-photon output probabilities."]
    changed = ["Minimize the weight of an independent set.",
               "Find a minimum-weight maximal independent set.",
               "Count all independent sets.",
               "Compute complex single-photon output amplitudes.",
               "Compute lossy single-photon output probabilities with loss 0.1.",
               "Compute noisy single-photon output probabilities."]
    for i, text in enumerate(paraphrases):
        req = copy.deepcopy(canonical[i]); req["intent"] = text
        add("paraphrase", i, req, True, "Equivalent meaning with the same paired numerical input")
    for i, text in enumerate(changed):
        req = copy.deepcopy(canonical[i]); req["intent"] = text
        add("changed_intent", i, req, False, "Changed objective, task or observable; inconsistent noise/loss assumptions require abstention")
    invalid = copy.deepcopy(canonical)
    invalid[0]["data"]["required_vertices"] = [0]
    invalid[1]["data"]["edges"] = [[0, 1], [1, 0]]
    invalid[2]["data"]["weights"][0] = -1
    invalid[3]["data"]["photons"] = 2
    invalid[4]["data"]["loss"] = .1
    invalid[5]["data"]["a"] = "nan"
    for i, req in enumerate(invalid):
        add("invalid_data", i, req, False, "Schema, physical sector, loss or numeric domain outside contract")
    return cases


def keyword_pipeline(request):
    req = copy.deepcopy(request)
    text = req["intent"].casefold()
    if any(word in text for word in ("independent", "indépendant", "nonadjacent")):
        req["intent"] = MIS_INTENT
    elif "photon" in text:
        req["intent"] = PHOTO_INTENT
    return pipeline(req)


def run(cases_path, output):
    cases = json.loads(cases_path.read_text())
    output.mkdir(parents=True, exist_ok=True)
    counts = {method: {"groups": {}, "correct_accepts": 0, "false_accepts": 0,
                       "false_abstentions": 0, "correct_abstentions": 0,
                       "accepted_with_numerical_certificate": 0} for method in ("strict", "keywords")}
    started = time.perf_counter()
    with (output/"raw.jsonl").open("w") as raw:
        for case in cases:
            results = {}
            for name, method in (("strict", pipeline), ("keywords", keyword_pipeline)):
                t0 = time.perf_counter()
                result = method(case["request"])
                result["elapsed_seconds"] = time.perf_counter()-t0
                accepted = result["status"] == "solved"
                good = case["contract_equivalent"]
                metric = ("correct_accepts" if good else "false_accepts") if accepted else ("false_abstentions" if good else "correct_abstentions")
                counts[name][metric] += 1
                group = counts[name]["groups"].setdefault(case["group"], {"cases":0,"accepted":0})
                group["cases"] += 1; group["accepted"] += int(accepted)
                counts[name]["accepted_with_numerical_certificate"] += int(accepted and result["verification"]["valid"])
                results[name] = result
            raw.write(json.dumps({"case":case, "results":results}, sort_keys=True, allow_nan=False)+"\n")
    metrics = {"cases":len(cases), "methods":counts, "elapsed_seconds":time.perf_counter()-started,
               "dataset_seed":20261114, "llm_calls":0, "qpu_jobs":0,
               "split_limitation":"Author-designed challenge with paired data; no blind test or trained model."}
    (output/"metrics.json").write_text(json.dumps(metrics, indent=2)+"\n")
    print(json.dumps(metrics))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", type=Path)
    parser.add_argument("--cases", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.generate:
        args.generate.write_text(json.dumps(build_cases(),indent=2,ensure_ascii=False)+"\n")
    elif args.cases and args.output:
        run(args.cases, args.output)
    else:
        parser.error("--generate PATH, or --cases PATH --output PATH required")
