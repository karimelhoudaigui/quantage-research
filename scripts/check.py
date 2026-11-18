"""Validate evidence structure and completed-cycle handoffs, not scientific truth."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def local_file(root, name):
    require(isinstance(name, str), "evidence path must be text")
    path = (root/name).resolve()
    require(path.is_relative_to(root.resolve()) and path.is_file(), "missing or outside evidence: "+name)


def validate_completion(path):
    result = json.loads(path.read_text())
    require(isinstance(result, dict), "completion must be an object")
    require(result.get("status") in ("complete", "blocked"), "invalid completion status")
    for key in ("question", "next_action"):
        require(isinstance(result.get(key), str) and bool(result[key].strip()), "missing completion "+key)
    require(path.with_name("summary.md").is_file(), "missing cycle summary")
    return result


def check(root=ROOT):
    root = Path(root)
    claims = json.loads((root/"research/claims.json").read_text())
    require(isinstance(claims, list), "claims must be a list")
    seen = set()
    for claim in claims:
        require(isinstance(claim, dict), "claim must be an object")
        cid = claim.get("id")
        require(isinstance(cid, str) and cid and cid not in seen, "duplicate or absent claim id")
        seen.add(cid)
        require(claim.get("status") in ("hypothesis", "verified", "refuted", "inconclusive"), "invalid claim status")
        require(isinstance(claim.get("statement"), str) and bool(claim["statement"].strip()), "empty statement")
        require(isinstance(claim.get("limitations"), str) and bool(claim["limitations"].strip()), "missing limitations")
        evidence = claim.get("evidence")
        require(isinstance(evidence, list), "evidence must be a list")
        if claim["status"] == "verified":
            require(bool(evidence) and bool(claim.get("verification_report")), "verified claim needs evidence and review")
        for name in evidence + ([claim["verification_report"]] if claim.get("verification_report") else []):
            local_file(root, name)
    cycles = 0
    for path in sorted((root/"runs").glob("*/completion.json")):
        validate_completion(path)
        cycles += 1
    print("OK: %d claims; %d completed/blocked handoffs; truth requires scientific review." % (len(claims), cycles))
    return len(claims), cycles


if __name__ == "__main__":
    check()
