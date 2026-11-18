"""Separate algorithms for finite validation; same author, NOT independent review."""
import itertools
import math


def independent_set_oracle(problem):
    # Subset enumeration, with feasibility before objective (no QUBO penalties).
    n = problem["n"]
    candidates = []
    for size in range(n+1):
        for subset in itertools.combinations(range(n), size):
            if all(not (i in subset and j in subset) for i, j in problem["edges"]):
                candidates.append((sum(problem["weights"][i] for i in subset), subset))
    optimum = max(v for v, subset in candidates)
    solutions = {tuple(int(i in subset) for i in range(n)) for v, subset in candidates if v == optimum}
    return optimum, solutions


def optical_oracle(problem):
    # Expanded analytic probability, no complex propagation.
    a, b, phi = problem["a"], problem["b"], problem["phi"]
    c1, s1, c2, s2 = math.cos(a), math.sin(a), math.cos(b), math.sin(b)
    cross = 2*c1*s1*c2*s2*math.cos(phi)
    return [c1*c1*c2*c2+s1*s1*s2*s2-cross,
            c1*c1*s2*s2+s1*s1*c2*c2+cross]


def greedy_independent_set(problem):
    remaining = set(range(problem["n"]))
    selected = []
    while remaining:
        degree = {i: sum(i in edge and all(j in remaining for j in edge) for edge in problem["edges"]) for i in remaining}
        vertex = max(remaining, key=lambda i: (problem["weights"][i]/(degree[i]+1), -i))
        selected.append(vertex)
        removed = {vertex}
        for i, j in problem["edges"]:
            if i == vertex: removed.add(j)
            if j == vertex: removed.add(i)
        remaining -= removed
    return sum(problem["weights"][i] for i in selected)


def verify(problem, model, tolerance=1e-12):
    from .core import solve_qubo, optical_probabilities
    try:
        if problem["family"] == "mis":
            if model["kind"] != "qubo" or len(model["linear"]) != problem["n"]:
                return {"valid": False, "reason": "dimension/kind"}
            result = solve_qubo(model)
            optimum, expected = independent_set_oracle(problem)
            actual = {tuple(x) for x in result["solutions"]}
            return {"valid": actual == expected, "reason": "all optimal states compared",
                    "oracle_value": optimum, "states_checked": 2**problem["n"]}
        if model["kind"] != "linear_optics":
            return {"valid": False, "reason": "kind"}
        actual, expected = optical_probabilities(model), optical_oracle(problem)
        error = max(abs(a-b) for a, b in zip(actual, expected))
        valid = (len(actual) == 2 and all(math.isfinite(x) and -tolerance <= x <= 1+tolerance for x in actual)
                 and abs(sum(actual)-1) <= tolerance and error <= tolerance)
        return {"valid": valid, "max_abs_error": error, "reason": "analytic probabilities and normalization"}
    except (KeyError, TypeError, ValueError, IndexError, OverflowError):
        return {"valid": False, "reason": "malformed formulation"}
