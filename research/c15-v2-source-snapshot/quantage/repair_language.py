"""Compile authored linear constraint strings into the frozen dense ILP schema.

Only algebra is normalized: no problem data, objective weights, reference
contract, missing clause or preferred solver is consulted. The LLM still
supplies every objective coefficient, variable, constraint and bound. Valid
legacy dense proposals retain exactly the frozen parse_model result. String
proposals preserve their original authored_model alongside the compiled model.

Allowed expressions use integer constants, x0/x_0/x[0], addition, subtraction,
unary +/- and multiplication with a variable-free constant expression on at
least one side. A row has one <=, >= or == relation; Unicode <=/>= glyphs and
one bare = are normalized. No eval/exec, calls, powers, division, nonlinear
products, attributes, computed indices or unknown names are supported.
Resource limits: 4096 characters/row, 256 AST nodes, depth 64 and intermediate
integers of at most 512 bits. Frozen validation bounds final integers by 10000.
"""

import ast
import json
import re

from .repair_model import FIELDS, no_duplicates, parse_model, validate_model


MAX_ROW_CHARACTERS = 4096
MAX_AST_NODES = 256
MAX_DEPTH = 64
MAX_INTEGER_BITS = 512
VARIABLE_NAME = re.compile(r"x_?(0|[1-9][0-9]*)\Z")
BARE_EQUAL = re.compile(r"(?<![<>=!])=(?!=)")


def _bounded_integer(value):
    if type(value) is not int or value.bit_length() > MAX_INTEGER_BITS:
        raise ValueError("linear expression requires bounded integer constants")
    return value


def _variable(index, n):
    if type(index) is not int or not 0 <= index < n:
        raise ValueError("variable index is outside the declared domain")
    coefficients = [0] * n
    coefficients[index] = 1
    return coefficients, 0, True


def _linear(node, n, depth=0):
    """Return (integer coefficients, constant, variable syntax present)."""
    if depth > MAX_DEPTH:
        raise ValueError("linear expression exceeds the depth limit")
    if isinstance(node, ast.Constant):
        return [0] * n, _bounded_integer(node.value), False
    if isinstance(node, ast.Name):
        match = VARIABLE_NAME.fullmatch(node.id)
        if match is None:
            raise ValueError("unknown or ambiguous variable name")
        return _variable(int(match.group(1)), n)
    if isinstance(node, ast.Subscript):
        if not isinstance(node.value, ast.Name) or node.value.id != "x":
            raise ValueError("only a literal x[index] variable is allowed")
        index = node.slice
        # Python 3.8 wraps the slice; 3.9+ supplies Constant directly.
        if hasattr(ast, "Index") and isinstance(index, ast.Index):
            index = index.value
        if not isinstance(index, ast.Constant) or type(index.value) is not int:
            raise ValueError("variable subscript must be a literal integer")
        return _variable(index.value, n)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        coefficients, constant, has_variable = _linear(node.operand, n, depth + 1)
        sign = -1 if isinstance(node.op, ast.USub) else 1
        return ([_bounded_integer(sign * value) for value in coefficients],
                _bounded_integer(sign * constant), has_variable)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
        left, left_constant, left_variable = _linear(node.left, n, depth + 1)
        right, right_constant, right_variable = _linear(node.right, n, depth + 1)
        if isinstance(node.op, ast.Mult):
            if left_variable and right_variable:
                raise ValueError("products of variable expressions are nonlinear")
            if left_variable:
                coefficients = [value * right_constant for value in left]
            elif right_variable:
                coefficients = [left_constant * value for value in right]
            else:
                coefficients = [0] * n
            constant = left_constant * right_constant
        else:
            sign = -1 if isinstance(node.op, ast.Sub) else 1
            coefficients = [a + sign * b for a, b in zip(left, right)]
            constant = left_constant + sign * right_constant
        return ([_bounded_integer(value) for value in coefficients],
                _bounded_integer(constant), left_variable or right_variable)
    raise ValueError("unsupported syntax in linear expression")


def compile_constraint(expression, n):
    """Normalize exactly one authored comparison into [coefficients, op, rhs]."""
    if type(n) is not int or not 1 <= n <= 8:
        raise ValueError("finite domain requires 1 <= n <= 8")
    if (not isinstance(expression, str) or not expression.strip()
            or len(expression) > MAX_ROW_CHARACTERS):
        raise ValueError("invalid or overlong linear constraint string")
    if any(character in expression for character in ("#", ";", "\n", "\r")):
        raise ValueError("comments and statement separators are not allowed")
    normalized = BARE_EQUAL.sub("==", expression.replace("≤", "<=").replace("≥", ">=")).strip()
    try:
        tree = ast.parse(normalized, mode="eval")
    except (SyntaxError, RecursionError) as exc:
        raise ValueError("invalid linear comparison syntax") from exc
    if sum(1 for _ in ast.walk(tree)) > MAX_AST_NODES:
        raise ValueError("linear expression exceeds the AST size limit")
    comparison = tree.body
    if (not isinstance(comparison, ast.Compare) or len(comparison.ops) != 1
            or len(comparison.comparators) != 1):
        raise ValueError("one linear comparison is required per string")
    relation = comparison.ops[0]
    if isinstance(relation, ast.LtE):
        operator = "<="
    elif isinstance(relation, ast.GtE):
        operator = ">="
    elif isinstance(relation, ast.Eq):
        operator = "=="
    else:
        raise ValueError("only <=, >= and == comparisons are supported")
    left, left_constant, _ = _linear(comparison.left, n)
    right, right_constant, _ = _linear(comparison.comparators[0], n)
    return [[_bounded_integer(a - b) for a, b in zip(left, right)], operator,
            _bounded_integer(right_constant - left_constant)]


def _reject_constant(_):
    raise ValueError("nonfinite JSON")


def parse_proposal(raw, n):
    """Parse a dense legacy or algebraic-string proposal without semantic repair."""
    try:
        legacy = parse_model(raw, n)
    except (RecursionError, AttributeError) as exc:
        return {"valid": False, "error": str(exc)}
    if legacy["valid"]:
        return legacy
    body = raw.strip()
    fence = chr(96) * 3
    lines = body.split("\n")
    stripped = len(lines) >= 3 and lines[0] in (fence, fence + "json") and lines[-1] == fence
    if stripped:
        body = "\n".join(lines[1:-1])
    try:
        authored = json.loads(body, object_pairs_hook=no_duplicates, parse_constant=_reject_constant)
    except (ValueError, TypeError, RecursionError):
        return legacy
    if (not isinstance(authored, dict) or not isinstance(authored.get("constraints"), list)
            or not any(isinstance(row, str) for row in authored["constraints"])):
        return legacy
    provenance = {"authored_model": authored, "normalization": "linear_constraint_strings_v2"}
    try:
        if type(n) is not int or not 1 <= n <= 8:
            raise ValueError("finite domain requires 1 <= n <= 8")
        if set(authored) != FIELDS:
            raise ValueError("exact fields: formulation,variables,sense,objective,constraints")
        if len(authored["constraints"]) > 32:
            raise ValueError("at most32 explicit linear rows")
        dense = dict(authored)
        dense["constraints"] = [compile_constraint(row, n) if isinstance(row, str) else row
                                for row in authored["constraints"]]
        validate_model(dense, n)
        return dict(provenance, valid=True, model=dense, single_fence_removed=stripped)
    except (ValueError, TypeError, KeyError, RecursionError) as exc:
        return dict(provenance, valid=False, error=str(exc))
