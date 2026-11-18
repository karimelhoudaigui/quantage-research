"""Literal, atomic model edits; inputs are patch text, initial text and n only.

No data, annotation, verifier, filesystem or solver is consulted. Diagnostics
are unverified text. Every changed coefficient, index and row is LLM-authored.
"""
import copy
import hashlib
import json

from .repair_language import compile_constraint, parse_proposal
from .repair_model import FIELDS, no_duplicates

INTERPRETATION = "literal_sequential_patch_v1_then_linear_constraint_strings_v2"
MAX_OPERATIONS = 32
MAX_DIAGNOSIS = 256
MAX_PATCH_CHARACTERS = 262144
OPERATIONS = {
    "add_constraint": {"op", "row"},
    "replace_constraint": {"op", "index", "row"},
    "delete_constraint": {"op", "index"},
    "set_objective": {"op", "values"},
    "set_variables": {"op", "values"},
    "replace_model": {"op", "model"},
}


def _integers(maximum=10000, minimum=-10000, count=8):
    return {"type": "array", "maxItems": count,
            "items": {"type": "integer", "minimum": minimum, "maximum": maximum}}


MODEL_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["formulation", "variables", "sense", "objective", "constraints"],
    "properties": {"formulation": {"const": "binary_ilp"}, "variables": _integers(7, 0),
                   "sense": {"const": "max"}, "objective": _integers(),
                   "constraints": {"type": "array", "maxItems": 32,
                                   "items": {"type": "string", "maxLength": 4096}}},
}
EDIT_SCHEMAS = []
for _op, _fields in OPERATIONS.items():
    _properties = {"op": {"const": _op}}
    if "index" in _fields:
        _properties["index"] = {"type": "integer", "minimum": 0, "maximum": 31}
    if "row" in _fields:
        _properties["row"] = {"type": "string", "maxLength": 4096}
    if "values" in _fields:
        _properties["values"] = _integers(7, 0) if _op == "set_variables" else _integers()
    if "model" in _fields:
        _properties["model"] = MODEL_SCHEMA
    EDIT_SCHEMAS.append({"type": "object", "additionalProperties": False,
                         "required": sorted(_fields), "properties": _properties})

PATCH_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["diagnosis", "edits"],
    "properties": {"diagnosis": {"type": "string", "maxLength": 256,
                                 "pattern": "^[ -~]*$"},
                   "edits": {"type": "array", "maxItems": 32,
                             "items": {"oneOf": EDIT_SCHEMAS}}},
}

# Generic constants only: this grammar never uses a case, n or any gold field.
# Diagnosis contains printable ASCII, with only quote/backslash JSON escapes.
PATCH_GRAMMAR = r'''
root ::= "{" ws "\"diagnosis\"" ws ":" ws diagnosis "," ws "\"edits\"" ws ":" ws edits "}" ws
diagnosis ::= "\"" ([\x20-\x21\x23-\x5B\x5D-\x7E] | "\\" ["\\]){0,256} "\"" ws
edits ::= "[" ws (edit ("," ws edit){0,31})? "]" ws
edit ::= add | replace | delete | objective | variables | model
add ::= "{" ws "\"op\"" ws ":" ws "\"add_constraint\"" ws "," ws "\"row\"" ws ":" ws linear "}" ws
replace ::= "{" ws "\"op\"" ws ":" ws "\"replace_constraint\"" ws "," ws "\"index\"" ws ":" ws index "," ws "\"row\"" ws ":" ws linear "}" ws
delete ::= "{" ws "\"op\"" ws ":" ws "\"delete_constraint\"" ws "," ws "\"index\"" ws ":" ws index "}" ws
objective ::= "{" ws "\"op\"" ws ":" ws "\"set_objective\"" ws "," ws "\"values\"" ws ":" ws integers "}" ws
variables ::= "{" ws "\"op\"" ws ":" ws "\"set_variables\"" ws "," ws "\"values\"" ws ":" ws indices "}" ws
model ::= "{" ws "\"op\"" ws ":" ws "\"replace_model\"" ws "," ws "\"model\"" ws ":" ws complete "}" ws
complete ::= "{" ws "\"formulation\"" ws ":" ws "\"binary_ilp\"" ws "," ws "\"variables\"" ws ":" ws indices "," ws "\"sense\"" ws ":" ws "\"max\"" ws "," ws "\"objective\"" ws ":" ws integers "," ws "\"constraints\"" ws ":" ws rows "}" ws
indices ::= "[" ws ([0-7] ws ("," ws [0-7] ws){0,7})? "]" ws
index ::= ([0-9] | [12] [0-9] | "3" [01]) ws
integers ::= "[" ws (integer ("," ws integer){0,7})? "]" ws
integer ::= "-"? uint ws
sign ::= "+" | "-"
uint ::= "10000" | [0-9] | [1-9] [0-9]{0,3}
variable ::= "x" [0-7]
atom ::= variable | uint ("*" variable)?
expression ::= sign? atom (s ("+" | "-") s atom){0,31}
relation ::= "<=" | ">=" | "=="
linear ::= "\"" s expression s relation s sign? uint s "\"" ws
rows ::= "[" ws (linear ("," ws linear){0,31})? "]" ws
s ::= [ ]{0,8}
ws ::= [ \t\n\r]{0,20}
'''


def _json(text):
    if type(text) is not str or len(text) > MAX_PATCH_CHARACTERS:
        raise ValueError("bounded raw JSON text required")
    lines = text.strip().split("\n")
    fenced = len(lines) >= 3 and lines[0] in ("```", "```json") and lines[-1] == "```"
    body = "\n".join(lines[1:-1]) if fenced else text.strip()
    def reject(_):
        raise ValueError("nonfinite JSON")
    return json.loads(body, object_pairs_hook=no_duplicates, parse_constant=reject), fenced


def _values(values, variables=False):
    if (type(values) is not list or len(values) > 8
            or any(type(x) is not int or not (0 <= x <= 7 if variables else abs(x) <= 10000)
                   for x in values)):
        raise ValueError("bounded integer values required")


def _row(row, n):
    if type(row) is not str:
        raise ValueError("edited row must be an authored linear string")
    dense = compile_constraint(row, n)
    if any(abs(x) > 10000 for x in dense[0]) or abs(dense[2]) > 10000:
        raise ValueError("edited row exceeds final integer bounds")


def parse_patch(raw, n, initial_raw):
    """Apply edits in list order, index into the current list; reject atomically.

The base is decoded from the initial LLM text, never rebuilt from data. An
unusable base requires an explicit replace_model before any other operation.
Every intermediate edited list is bounded by 32 rows. Final arities/variables
and all rows must satisfy the existing proposal contract. No partial fallback.
"""
    result = {"valid": False, "normalization": INTERPRETATION,
              "diagnosis_scope": "unverified LLM text; never interpreted as an edit",
              "atomic_application": True}
    try:
        if (type(n) is not int or not 1 <= n <= 8 or type(initial_raw) is not str
                or len(initial_raw) > MAX_PATCH_CHARACTERS):
            raise ValueError("raw initial text and finite n required")
        result["initial_raw_sha256"] = hashlib.sha256(initial_raw.encode()).hexdigest()
        patch, fenced = _json(raw)
        if type(patch) is not dict or set(patch) != {"diagnosis", "edits"}:
            raise ValueError("exact patch fields: diagnosis,edits")
        result.update(authored_patch=patch, single_fence_removed=fenced)
        diagnosis, edits = patch["diagnosis"], patch["edits"]
        if (type(diagnosis) is not str or len(diagnosis) > MAX_DIAGNOSIS
                or any(not 32 <= ord(c) <= 126 for c in diagnosis)):
            raise ValueError("diagnosis must contain at most256 printable ASCII characters")
        if type(edits) is not list or len(edits) > MAX_OPERATIONS:
            raise ValueError("at most32 explicit edits")
        result.update(diagnosis=diagnosis, edit_count=len(edits))
        try:
            base, _ = _json(initial_raw)
        except (ValueError, TypeError, RecursionError):
            base = None
        if type(base) is not dict or set(base) != FIELDS:
            base = None
        base = copy.deepcopy(base)
        result["initial_schema_valid"] = parse_proposal(initial_raw, n)["valid"]
        for edit in edits:
            if (type(edit) is not dict or type(edit.get("op")) is not str
                    or edit["op"] not in OPERATIONS or set(edit) != OPERATIONS[edit["op"]]):
                raise ValueError("unknown edit or unexpected edit fields")
            op = edit["op"]
            if op == "replace_model":
                replacement = edit["model"]
                if (type(replacement) is not dict or set(replacement) != FIELDS
                        or type(replacement.get("constraints")) is not list
                        or any(type(row) is not str for row in replacement["constraints"])):
                    raise ValueError("replacement must contain the complete five fields and string rows")
                _values(replacement["variables"], variables=True)
                _values(replacement["objective"])
                if not parse_proposal(json.dumps(replacement), n)["valid"]:
                    raise ValueError("invalid explicit replacement model")
                base = copy.deepcopy(replacement)
                continue
            if base is None:
                raise ValueError("unusable initial JSON requires explicit replace_model first")
            if op in ("set_objective", "set_variables"):
                _values(edit["values"], variables=op == "set_variables")
                base["objective" if op == "set_objective" else "variables"] = edit["values"][:]
                continue
            rows = base.get("constraints")
            if type(rows) is not list or len(rows) > 32:
                raise ValueError("initial constraints must be a list of at most32 rows")
            if "row" in edit:
                _row(edit["row"], n)
            if op == "add_constraint":
                if len(rows) >= 32:
                    raise ValueError("intermediate constraint list exceeds32 rows")
                rows.append(edit["row"])
            else:
                index = edit["index"]
                if type(index) is not int or not 0 <= index < len(rows) or index > 31:
                    raise ValueError("edit index outside current constraint list")
                if op == "replace_constraint":
                    rows[index] = edit["row"]
                else:
                    del rows[index]
        if base is None:
            raise ValueError("no explicit complete model available")
        parsed = parse_proposal(json.dumps(base), n)
        if not parsed["valid"]:
            raise ValueError("edited model is invalid: " + parsed["error"])
        result.update(valid=True, model=parsed["model"], authored_model=base)
    except (ValueError, TypeError, KeyError, RecursionError) as exc:
        result["error"] = str(exc)
    return result
