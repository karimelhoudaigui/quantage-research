"""Literal state lineage for two authored repairs; never read data or gold."""
import hashlib
import json

from .repair_language import parse_proposal
from .repair_patch_tool_language import parse_patch


def sha(text):
    if type(text) is not str:
        raise ValueError("raw model/patch text must be a string")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def initial_context(initial_raw, n):
    parsed = parse_proposal(initial_raw, n)
    state = parsed.get("authored_model", parsed.get("model")) if parsed["valid"] else None
    return {"parsed": parsed, "base_raw": initial_raw, "state": state,
            "base_kind": "initial_llm_response", "selected_state_source": "initial",
            "initial_raw_sha256": sha(initial_raw), "previous_patch_sha256": None,
            "state_raw_sha256": sha(initial_raw), "materialization_is_model_generation": False}


def round_two_context(initial_raw, previous_patch_raw, n):
    """Replay the first actual patch; take it iff valid, else a valid initial.

    No semantic verifier participates in selection. A completely unusable
    history has state=None and retains the actual initial raw text as parser
    base, so the next model must explicitly author replace_model.
    """
    initial = initial_context(initial_raw, n)
    previous = parse_patch(previous_patch_raw, n, initial_raw)
    if previous["valid"]:
        state = previous["authored_model"]
        source = "round1_patch"
    elif initial["parsed"]["valid"]:
        state = initial["state"]
        source = "initial_syntax_fallback"
    else:
        state = None
        source = "no_valid_model"
    if state is None:
        base_raw = initial_raw
        parsed = initial["parsed"]
        kind = "unusable_initial_raw"
    else:
        # Field-key serialization is normalized; list/row order is unchanged.
        base_raw = json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                              allow_nan=False)
        parsed = parse_proposal(base_raw, n)
        if not parsed["valid"]:
            raise ValueError("literal latest-valid state failed its own proposal contract")
        kind = "materialized_state"
    return {"parsed": parsed, "previous_patch_parsed": previous, "base_raw": base_raw,
            "state": state, "base_kind": kind, "selected_state_source": source,
            "initial_raw_sha256": sha(initial_raw), "previous_patch_sha256": sha(previous_patch_raw),
            "state_raw_sha256": sha(base_raw), "materialization_is_model_generation": False}


def public_state_payload(context):
    """The user's own state/provenance; contains no reference values."""
    return {"current_model_state": context["state"],
            "state_provenance": {key: context[key] for key in (
                "base_kind", "selected_state_source", "initial_raw_sha256",
                "previous_patch_sha256", "state_raw_sha256", "materialization_is_model_generation")}}


def apply_current_patch(raw, n, context):
    """Literal parser plus the explicit round2 no-valid-state policy.

    The frozen parser may repair an invalid but complete five-field object
    locally. Round1 retains that behavior. For a round2 state declared absent,
    require an actual first replace_model edit rather than exposing an
    unadvertised partially usable base. No reference/model values are filled.
    """
    parsed = parse_patch(raw, n, context["base_raw"])
    if context["base_kind"] == "unusable_initial_raw":
        patch = parsed.get("authored_patch")
        edits = patch.get("edits") if isinstance(patch, dict) else None
        replaces_first = (isinstance(edits, list) and bool(edits)
                          and isinstance(edits[0], dict) and edits[0].get("op") == "replace_model")
        if not replaces_first:
            parsed = dict(parsed)
            parsed.update(valid=False, error="round2 without a valid materialized state requires explicit replace_model first",
                          iterative_state_policy="absent_state_requires_first_replace_model")
            parsed.pop("model", None)
            parsed.pop("authored_model", None)
    return parsed
