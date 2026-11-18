"""Structured contracts and two deliberately small, auditable formulations.

No LLM, SDK, credentials, or network access. A candidate provider is a
documentation lead, never evidence that the user's job can run on hardware.
"""
import cmath
import itertools
import math


class Unsupported(ValueError):
    pass


MIS_INTENT = "Maximize the weight of an independent set."
PHOTO_INTENT = "Compute ideal single-photon output probabilities."


def understand(request):
    """Accept an exact controlled-language contract; reject all unknown fields."""
    if not isinstance(request, dict) or set(request) != {"intent", "data"}:
        raise Unsupported("expected exactly intent and data")
    data = request["data"]
    if not isinstance(data, dict):
        raise Unsupported("data must be an object")
    if request["intent"] == MIS_INTENT:
        if set(data) != {"n", "edges", "weights"}:
            raise Unsupported("MIS fields: n, edges, weights only")
        n = data["n"]
        if type(n) is not int or not 1 <= n <= 12:
            raise Unsupported("MIS local exact cap: 1<=n<=12")
        w = data["weights"]
        if not isinstance(w, list) or len(w) != n or any(type(x) is not int or x <= 0 for x in w):
            raise Unsupported("positive integer weights required")
        if not isinstance(data["edges"], list):
            raise Unsupported("edges must be a list")
        edges = []
        for edge in data["edges"]:
            if not isinstance(edge, (list, tuple)) or len(edge) != 2:
                raise Unsupported("each edge has two endpoints")
            i, j = edge
            if any(type(x) is not int or not 0 <= x < n for x in edge) or i == j:
                raise Unsupported("invalid endpoint or self loop")
            pair = sorted([i, j])
            if pair in edges:
                raise Unsupported("duplicate undirected edge")
            edges.append(pair)
        return {"family": "mis", "n": n, "edges": sorted(edges), "weights": list(w),
                "objective": "maximize_weight", "domain": "binary", "constraints": "independent"}
    if request["intent"] == PHOTO_INTENT:
        if set(data) != {"a", "b", "phi", "photons", "modes", "loss"}:
            raise Unsupported("optical schema mismatch")
        if type(data["photons"]) is not int or data["photons"] != 1 or type(data["modes"]) is not int or data["modes"] != 2:
            raise Unsupported("only one photon, two modes")
        if type(data["loss"]) not in (int, float) or data["loss"] != 0:
            raise Unsupported("only ideal lossless model")
        for key in ("a", "b", "phi"):
            if type(data[key]) not in (int, float) or not math.isfinite(data[key]):
                raise Unsupported("finite real angles in radians required")
        return {"family": "photon", "a": data["a"], "b": data["b"], "phi": data["phi"],
                "input": [1, 0], "modes": 2, "loss": 0, "observable": "probabilities"}
    raise Unsupported("unrecognized controlled-language intention")


def formulate(problem):
    if problem["family"] == "mis":
        penalty = max(problem["weights"]) + 1
        return {"kind": "qubo", "linear": [-w for w in problem["weights"]],
                "quadratic": [[i, j, penalty] for i, j in problem["edges"]],
                "constant": 0, "sense": "minimize", "penalty": penalty}
    return {"kind": "linear_optics", "a": problem["a"], "b": problem["b"],
            "phi": problem["phi"], "phase_mode": 1, "input_mode": 0,
            "order": "R_b P R_a", "global_phase": 0, "coherent": True,
            "output": "probabilities"}


def bitstrings(n):
    return itertools.product((0, 1), repeat=n)


def energy(model, bits):
    return (model["constant"] + sum(v*x for v, x in zip(model["linear"], bits))
            + sum(v*bits[i]*bits[j] for i, j, v in model["quadratic"]))


def solve_qubo(model):
    states = [(energy(model, x), x) for x in bitstrings(len(model["linear"]))]
    optimum = (min if model["sense"] == "minimize" else max)(v for v, x in states)
    return {"energy": optimum, "solutions": [list(x) for v, x in states if v == optimum],
            "states_evaluated": len(states)}


def optical_probabilities(model):
    """Propagate amplitudes component by component, unlike the scalar oracle."""
    a, b, phi = model["a"], model["b"], model["phi"]
    if model["order"] == "R_a P R_b":
        a, b = b, a
    v = [1+0j, 0j] if model["input_mode"] == 0 else [0j, 1+0j]
    def rotate(v, angle):
        c, s = math.cos(angle), math.sin(angle)
        return [c*v[0]-s*v[1], s*v[0]+c*v[1]]
    v = rotate(v, a)
    if not model["coherent"]:
        # Deliberately available as an experimental mutation, never default.
        p = [abs(x)**2 for x in v]
        return [math.cos(b)**2*p[0]+math.sin(b)**2*p[1],
                math.sin(b)**2*p[0]+math.cos(b)**2*p[1]]
    v[model["phase_mode"]] *= cmath.exp(1j*phi)
    v = [x*cmath.exp(1j*model["global_phase"]) for x in rotate(v, b)]
    if model["output"] == "real_amplitudes":
        return [x.real for x in v]
    return [abs(x)**2 for x in v]


def choose_solver(problem):
    mis = problem["family"] == "mis"
    return {"solver": "exhaustive_qubo" if mis else "single_photon_amplitudes",
            "execution": "local_classical_exact" if mis else "local_ideal_float_simulation",
            "quantum_candidate": "Pasqal" if mis else "Quandela",
            "hardware_readiness": "unverified", "qpu_submitted": False,
            "conditions": (["geometric embedding", "interaction errors and controls", "device and account access"]
                           if mis else ["component convention translation", "platform constraints and access", "shots and imperfections"])}


def pipeline(request):
    from .verification import verify
    try:
        problem = understand(request)
        model = formulate(problem)
        report = verify(problem, model)
        if not report["valid"]:
            return {"status": "abstain", "reason": "formulation rejected", "verification": report}
        route = choose_solver(problem)
        solution = solve_qubo(model) if problem["family"] == "mis" else {"probabilities": optical_probabilities(model)}
        return {"status": "solved", "problem": problem, "formulation": model,
                "verification": report, "route": route, "solution": solution}
    except (Unsupported, TypeError, KeyError, ValueError, OverflowError) as exc:
        return {"status": "abstain", "reason": str(exc)}
