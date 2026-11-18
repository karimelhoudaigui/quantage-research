"""Execute a bounded binary ILP proposed by an LLM, without canonical data.

The portfolio profiles both solvers sequentially. Its selected solver is an
after-the-fact timing diagnostic; total_portfolio_seconds includes both runs
and their comparison. Individual timings include validation and lazy imports.
The MILP time limit applies to HiGHS itself, not Python startup/imports.
"""

import math
import time

from .repair_model import model_feasible, objective_value, validate_model


MAX_VARIABLES = 7
INTEGER_TOLERANCE = 1e-7


def _validated_model(model):
    if not isinstance(model, dict) or not isinstance(model.get("variables"), list):
        raise ValueError("model.variables must be a list")
    n = len(model["variables"])
    if not 1 <= n <= MAX_VARIABLES:
        raise ValueError("solver domain is 1 <= n <= 7")
    return validate_model(model, n)


def _result(solver, started, status, **fields):
    result = {
        "solver": solver,
        "status": status,
        "objective": None,
        "solution": None,
    }
    result.update(fields)
    result["seconds"] = time.perf_counter() - started
    return result


def enumeration_dfs(model):
    """Return every optimizer of the proposed ILP by an unpruned binary DFS."""
    started = time.perf_counter()
    solver = "enumeration_dfs"
    try:
        model = _validated_model(model)
        n = len(model["variables"])
        best = None
        optima = []
        visited = 0

        def visit(prefix):
            nonlocal best, optima, visited
            if len(prefix) == n:
                visited += 1
                if model_feasible(model, prefix):
                    value = objective_value(model, prefix)
                    if best is None or value > best:
                        best = value
                        optima = [prefix[:]]
                    elif value == best:
                        optima.append(prefix[:])
                return
            for bit in (0, 1):
                prefix.append(bit)
                visit(prefix)
                prefix.pop()

        visit([])
        if best is None:
            return _result(solver, started, "infeasible", all_optima=[],
                           visited_leaves=visited)
        return _result(solver, started, "optimal", objective=best,
                       solution=optima[0], all_optima=optima,
                       visited_leaves=visited)
    except Exception as exc:
        return _result(solver, started, "error", error=str(exc))


def _checked_primal(model, values):
    """Validate a floating point incumbent against the exact proposed ILP."""
    n = len(model["variables"])
    if values is None or len(values) != n:
        raise ValueError("solver did not return a complete solution")
    bits = []
    for value in values:
        value = float(value)
        if not math.isfinite(value):
            raise ValueError("solver returned a non-finite variable")
        bit = int(round(value))
        if bit not in (0, 1) or abs(value - bit) > INTEGER_TOLERANCE:
            raise ValueError("solver variable is not within 1e-7 of a binary value")
        bits.append(bit)
    if not model_feasible(model, bits):
        raise ValueError("rounded solver solution violates an exact constraint")
    return bits, objective_value(model, bits)


def scipy_highs_milp(model, time_limit=2.0):
    """Execute SciPy's HiGHS MILP adapter on the proposed binary ILP only."""
    started = time.perf_counter()
    solver = "scipy_highs_milp"
    try:
        model = _validated_model(model)
        if (isinstance(time_limit, bool) or not isinstance(time_limit, (int, float))
                or not math.isfinite(time_limit) or time_limit <= 0):
            raise ValueError("time_limit must be positive and finite")

        import numpy as np
        from scipy.optimize import Bounds, LinearConstraint, milp

        n = len(model["variables"])
        rows = []
        lower = []
        upper = []
        for coefficients, relation, rhs in model["constraints"]:
            rows.append(coefficients)
            lower.append(rhs if relation in (">=", "==") else -np.inf)
            upper.append(rhs if relation in ("<=", "==") else np.inf)
        constraints = (LinearConstraint(np.asarray(rows, dtype=float), lower, upper)
                       if rows else None)
        result = milp(
            c=-np.asarray(model["objective"], dtype=float),
            integrality=np.ones(n, dtype=int),
            bounds=Bounds(np.zeros(n), np.ones(n)),
            constraints=constraints,
            options={"time_limit": float(time_limit), "mip_rel_gap": 0.0},
        )
        raw_objective = float(result.fun) if result.fun is not None else None
        metadata = {
            "raw_status": int(result.status),
            "message": str(result.message),
            "time_limit_seconds": float(time_limit),
            "raw_min_objective": (raw_objective if raw_objective is not None
                                  and math.isfinite(raw_objective) else None),
        }
        if result.status == 2:
            return _result(solver, started, "infeasible", **metadata)
        if result.status not in (0, 1):
            return _result(solver, started, "error", **metadata)

        status = "optimal" if result.status == 0 else "time_limit"
        if result.x is None:
            if status == "optimal":
                return _result(solver, started, "error",
                               error="optimal status without a solution", **metadata)
            return _result(solver, started, status, **metadata)
        try:
            bits, objective = _checked_primal(model, result.x)
            if (result.fun is None or not math.isfinite(float(result.fun))
                    or abs(-float(result.fun) - objective) > INTEGER_TOLERANCE):
                raise ValueError("reported objective disagrees with exact evaluation")
        except ValueError as exc:
            return _result(solver, started,
                           "error" if status == "optimal" else status,
                           error=str(exc), **metadata)
        return _result(solver, started, status, solution=bits,
                       objective=objective, **metadata)
    except Exception as exc:
        return _result(solver, started, "error", error=str(exc))


def portfolio(model):
    """Profile both real solvers, compare candidate optima, then select by time.

    No original request, canonical model, label, or gold optimum is consulted.
    Distinct optimal vectors are allowed. A limit/error/disagreement produces
    no selected solver, rather than silently selecting with canonical data.
    """
    started = time.perf_counter()
    results = [enumeration_dfs(model), scipy_highs_milp(model, time_limit=2.0)]
    concordance = False
    comparison_error = None
    try:
        statuses = [result["status"] for result in results]
        if statuses == ["infeasible", "infeasible"]:
            concordance = True
        elif statuses == ["optimal", "optimal"]:
            checked = [_checked_primal(model, result["solution"])
                       for result in results]
            concordance = (
                checked[0][1] == checked[1][1]
                and all(value == result["objective"]
                        for (_, value), result in zip(checked, results))
            )
        if not concordance:
            comparison_error = "solver statuses or exact candidate objectives disagree"
    except Exception as exc:
        comparison_error = str(exc)
    selected = min(results, key=lambda result: result["seconds"]) if concordance else None
    return {
        "concordance": concordance,
        "selected_solver": selected["solver"] if selected else None,
        "selected_solver_seconds": selected["seconds"] if selected else None,
        "objective": selected["objective"] if selected else None,
        "solution": selected["solution"] if selected else None,
        "solvers": results,
        "comparison_error": comparison_error,
        "total_portfolio_seconds": time.perf_counter() - started,
    }
