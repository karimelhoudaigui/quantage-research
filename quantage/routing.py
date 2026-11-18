"""Conservative proposal review, distinct from execution authorization.

This registry records the scope of THIS project's documented candidates. It is
not a vendor capability catalogue and never emits hardware_readiness=verified.
"""
KNOWN = {"pasqal_analog": ("mis", "Pasqal"), "quandela_linear": ("photon", "Quandela"),
         "exhaustive_qubo": ("mis", "local"), "single_photon_amplitudes": ("photon", "local")}


def review_route(problem, proposal, policy, level="guarded"):
    solver, provider = proposal.get("solver"), proposal.get("provider")
    kind, claim = proposal.get("execution_kind"), proposal.get("claim")
    family = problem.get("family")
    naive = provider == "local" or provider in policy["qpu_providers"] or proposal.get("host_country") == "France"
    reasons = []
    if not naive:
        reasons.append("provider provenance not admitted")
    acceptable = naive
    if level != "name_only":
        if solver not in KNOWN or KNOWN[solver] != (family, provider):
            acceptable = False
            reasons.append("unsupported project solver/modality/provider combination")
        if solver == "single_photon_amplitudes" and problem.get("photons", 1) != 1:
            acceptable = False
            reasons.append("local implementation supports one photon only")
        if solver == "exhaustive_qubo" and (type(problem.get("n")) is not int or not 1 <= problem["n"] <= 12):
            acceptable = False
            reasons.append("exact local enumeration cap")
    if level == "guarded":
        local_claim = {"exhaustive_qubo": "exact_instance_optima", "single_photon_amplitudes": "ideal_probabilities"}
        if provider == "local":
            scoped = kind == "local" and claim == local_claim.get(solver)
        else:
            scoped = kind == "candidate" and claim == "conditional_candidate"
        if not scoped:
            acceptable = False
            reasons.append("execution type or claim exceeds verified scope")
    # No network-backed executor exists. Even a future policy edit must not
    # turn this documentation checker into authorization to run a QPU.
    permission = "allowed_local" if acceptable and provider == "local" and kind == "local" else "not_authorized"
    return {"acceptable_recommendation": acceptable, "execution_permission": permission,
            "hardware_readiness": "unverified" if provider != "local" else "not_applicable",
            "qpu_submission_implemented": False, "reasons": reasons,
            "policy_qpu_submission_enabled": policy["qpu_submission_enabled"]}
