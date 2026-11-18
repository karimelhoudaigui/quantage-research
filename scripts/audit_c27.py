"""Replay and exactly score the single C27 development repair."""

import datetime
import hashlib
import json
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scipy

from quantage.repair_language import parse_proposal
from quantage.repair_model import verify_model
from quantage.repair_patch_tool_language import parse_patch
from quantage.repair_solvers import portfolio


CASE_ID = "417127d82203"
INITIAL_PATH = ROOT / "runs/20261115-c19-instruct-repair/test-initial-v2/driver/raw.jsonl"
FIRST_PATCH_PATH = ROOT / "runs/20261115-c22-model-capacity/probe-remaining-v3/driver/raw.jsonl"
GOLD_PATH = ROOT / "runs/20261115-c19-instruct-repair/gold.json"
STATE_PATH = ROOT / "runs/20261116-c24-second-repair/states.json"
PUBLIC_PATH = ROOT / "runs/20261116-c24-second-repair/public_case.json"
C27_PATH = ROOT / "runs/20261117-c27-quantized-kv-v2/guided-round2-v1/driver/raw.jsonl"
OUTPUT_PATH = ROOT / "runs/20261117-c27-quantized-kv-v2/verification.json"
EXECUTION_PATHS = [
    ROOT / "runs/20261117-c27-quantized-kv-v2/protocol.md",
    ROOT / "runs/20261117-c27-quantized-kv-v2/freeze-round2-v1.json",
    ROOT / "runs/20261117-c27-quantized-kv-v2/guided-round2-v1/manifest.json",
    ROOT / "runs/20261117-c27-quantized-kv-v2/guided-round2-v1/driver/generation.json",
]
SOURCE_PATHS = [
    Path(__file__).resolve(),
    ROOT / "quantage/repair_language.py",
    ROOT / "quantage/repair_model.py",
    ROOT / "quantage/repair_patch_tool_language.py",
    ROOT / "quantage/repair_solvers.py",
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonl_record(path, identifier):
    matches = []
    for line in path.read_text().splitlines():
        record = json.loads(line)
        if record.get("id") == identifier:
            matches.append(record)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {identifier} record in {path}")
    return matches[0]


def main():
    if OUTPUT_PATH.exists():
        raise FileExistsError(f"refuse to overwrite {OUTPUT_PATH}")
    started_at = datetime.datetime.now(datetime.timezone.utc)

    state_rows = json.loads(STATE_PATH.read_text())
    if not isinstance(state_rows, list) or len(state_rows) != 1 or state_rows[0].get("id") != CASE_ID:
        raise ValueError("unexpected frozen C24 state matrix")
    state = state_rows[0]
    public_rows = json.loads(PUBLIC_PATH.read_text())
    if not isinstance(public_rows, list) or len(public_rows) != 1 or public_rows[0].get("id") != CASE_ID:
        raise ValueError("unexpected public case matrix")
    case = public_rows[0]

    initial = jsonl_record(INITIAL_PATH, CASE_ID)
    first_patch = jsonl_record(FIRST_PATCH_PATH, CASE_ID)
    second_patch = jsonl_record(C27_PATH, CASE_ID)
    gold_rows = json.loads(GOLD_PATH.read_text())
    gold_matches = [row for row in gold_rows if row.get("id") == CASE_ID]
    if len(gold_matches) != 1:
        raise ValueError("expected exactly one C19 reference record")
    gold = gold_matches[0]

    initial_raw = initial["raw_response"]
    first_patch_raw = first_patch["raw_response"]
    second_patch_raw = second_patch["raw_response"]
    lineage = state["lineage"]
    if hashlib.sha256(initial_raw.encode()).hexdigest() != lineage["original_initial_raw_sha256"]:
        raise ValueError("recorded C19 initial response differs from the C24 lineage")
    if hashlib.sha256(first_patch_raw.encode()).hexdigest() != lineage["previous_patch_raw_sha256"]:
        raise ValueError("recorded C22 patch differs from the C24 lineage")
    if hashlib.sha256(state["raw_response"].encode()).hexdigest() != lineage["current_state_sha256"]:
        raise ValueError("materialized state differs from the C24 lineage")

    n = case["data"]["n"]
    parsed_initial = parse_proposal(initial_raw, n)
    parsed_first = parse_patch(first_patch_raw, n, initial_raw)
    if not parsed_first["valid"]:
        raise ValueError("recorded first patch does not replay")
    materialized = json.dumps(parsed_first["authored_model"], ensure_ascii=False,
                              sort_keys=True, separators=(",", ":"), allow_nan=False)
    if materialized != state["raw_response"]:
        raise ValueError("C24 state is not the literal materialization of the C19/C22 records")

    parsed_c27 = parse_patch(second_patch_raw, n, state["raw_response"])
    if not parsed_c27["valid"] or not second_patch["parsed"]["valid"]:
        raise ValueError("C27 patch failed the frozen literal patch contract")
    if parsed_c27["authored_model"] != second_patch["parsed"]["authored_model"]:
        raise ValueError("C27 stored model differs from replayed literal patch")

    states = {
        "initial_4b": parsed_initial,
        "after_first_8b_patch": parsed_first,
        "before_c27": parse_proposal(state["raw_response"], n),
        "after_c27": parsed_c27,
    }
    verification = {
        name: verify_model(case["data"], gold["constraints"], parsed)
        for name, parsed in states.items()
    }
    solvers = portfolio(parsed_c27["model"])
    if not solvers["concordance"]:
        raise RuntimeError("final candidate solver portfolio did not concord")

    inputs = [INITIAL_PATH, FIRST_PATCH_PATH, GOLD_PATH, STATE_PATH,
              PUBLIC_PATH, C27_PATH, *EXECUTION_PATHS]
    result = {
        "status": "verified",
        "claim_id": "C27-Q8-KV-DEVELOPMENT-SECOND-REPAIR",
        "scope": "one posthoc development case; not held-out evidence or a population estimate",
        "case_id": CASE_ID,
        "lineage": {
            "initial_source": str(INITIAL_PATH.relative_to(ROOT)),
            "first_patch_source": str(FIRST_PATCH_PATH.relative_to(ROOT)),
            "current_state_source": str(STATE_PATH.relative_to(ROOT)),
            "new_patch_source": str(C27_PATH.relative_to(ROOT)),
            "exact_literal_replay": True,
            "new_initial_sampled": False,
        },
        "verification": verification,
        "final_solver_portfolio": solvers,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "scipy": scipy.__version__,
            "command": "python scripts/audit_c27.py",
            "started_at_utc": started_at.isoformat(),
            "model_invocations": 0,
            "network_requests": 0,
        },
        "input_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in inputs},
        "source_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in SOURCE_PATHS},
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    print(json.dumps({
        "status": result["status"],
        "faithful_before_c27": verification["before_c27"]["faithful"],
        "faithful_after_c27": verification["after_c27"]["faithful"],
        "feasibility_mismatches_after_c27": verification["after_c27"]["feasibility_mismatches"],
        "objective_mismatches_after_c27": verification["after_c27"]["objective_mismatches"],
        "solver_concordance": solvers["concordance"],
        "selected_solver": solvers["selected_solver"],
        "verification_file": str(OUTPUT_PATH),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
