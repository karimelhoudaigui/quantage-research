"""Score the 15 completely paired cases; bound the missing sixteenth result.

The interrupted sixth guided call is never regenerated or imputed. This is an
integrator self-analysis after ENOSPC, not a newly preregistered complete test.
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))
from quantage.repair_study_c16 import score, choose_direct, choose_revision
from quantage.repair_model import verify_model


def read_rows(path):
    return [json.loads(x) for x in path.read_text().splitlines()]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    output = p.parse_args().output
    run = Path("runs/20261115-c16-quantized-repair")
    cases = json.loads((run / "test_cases.json").read_text())
    public = {x["id"]: x for x in cases}
    gold = {x["id"]: x for x in json.loads((run / "gold.json").read_text())}
    sources = {name: [run / ("test-" + name + "-v1/driver/raw.jsonl")]
               for name in ("initial", "direct", "self", "guided")}
    sources["guided"].append(run / "test-guided-continuation-v1/driver/raw.jsonl")
    all_rows = {name: [row for path in paths for row in read_rows(path)]
                for name, paths in sources.items()}
    indexed = {name: {x["id"]: x for x in rows} for name, rows in all_rows.items()}
    assert [len(all_rows[k]) for k in ("initial", "direct", "self", "guided")] == [16, 16, 16, 15]
    assert all(len(rows) == len(indexed[k]) for k, rows in all_rows.items())
    missing = set(public) - set(indexed["guided"])
    assert missing == {"54969ba6bb41"}
    fixture = output / "observed-subset"
    fixture.mkdir()
    subset = [x for x in cases if x["id"] not in missing]
    cases_path = fixture / "cases.json"
    cases_path.write_text(json.dumps(subset, ensure_ascii=False, indent=2) + "\n")
    paths = {}
    for name, rows in all_rows.items():
        folder = fixture / name
        folder.mkdir()
        paths[name] = folder / "raw.jsonl"
        paths[name].write_text("".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n"
                                      for row in rows if row["id"] not in missing))
        (folder / "provenance.json").write_text(json.dumps(
            {"sources": [str(path) for path in sources[name]], "kind": "filtered actual observations; no generation",
             "generation_metadata": "original whole-batch metadata kept at source; no per-subset loading/CPU allocated"}, indent=2) + "\n")
    score(cases_path, run / "gold.json", paths["initial"], paths["direct"], paths["self"],
          paths["guided"], output / "paired-results")
    def faithful(identity, selected):
        return verify_model(public[identity]["data"], gold[identity]["constraints"], selected["parsed"])["faithful"]
    full = {}
    for name in ("initial", "direct", "self", "guided"):
        count = 0
        for identity in indexed[name]:
            first = indexed["initial"][identity]
            selected = first if name == "initial" else (
                choose_direct(first, indexed[name][identity])[0] if name == "direct"
                else choose_revision(first, indexed[name][identity])[0])
            count += faithful(identity, selected)
        full[name] = {"observed": len(indexed[name]), "faithful": count}
    observed_guided = full["guided"]["faithful"]
    self_count = full["self"]["faithful"]
    gain = [observed_guided - self_count, observed_guided + len(missing) - self_count]
    outcome = "not_supported_for_any_missing_response" if gain[1] < 3 else "inconclusive"
    metrics = {"full_test_planned": 16, "paired_complete": 15, "physical_attempted_calls": 64,
               "completed_response_records": 63, "unknown_guided_ids": sorted(missing),
               "full_methods": full, "guided_faithful_bounds": [observed_guided, observed_guided + 1],
               "guided_minus_self_bounds": gain, "H16": outcome,
               "missing_values_imputed": False,
               "scope": "finite bounds over unknown outcome, not a confidence interval; paired15 analysis descriptive after infrastructure failure",
               "observed_physical_cost": {field: sum(row[field] for rows in all_rows.values() for row in rows)
                                          for field in ("input_tokens", "output_tokens", "wall_seconds", "cpu_seconds")},
               "cost_limits": "63 response sums; interrupted call/load/server CPU not fully recorded; row CPU is client only",
               "independence": "integrator self-analysis using previously independent reference annotations"}
    (output / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics))


if __name__ == "__main__":
    main()
