Return ONLY one JSON object with exactly action, task, reason. No family key.
action: "propose" or "abstain". For propose, task is exactly
"maximum_weight_independent_set" or "ideal_single_photon_probabilities".
For abstain, task must be null. reason: one short sentence. No code or solution.

Only these tasks are supported:
1. Maximum TOTAL WEIGHT independent set of a simple undirected graph, binary
selection, positive integer weights, n<=12, no extra constraints. Each edge
forbids selecting both endpoints. Counting sets, maximizing cardinality,
minimizing, requiring a fixed size/vertex, invalid data or unspecified direction
are unsupported and require abstain.
2. Ideal output PROBABILITIES for ONE photon initially mode0, two modes, loss0,
R(b)diag(1,exp(i*phi))R(a), real rotation R(t), phase on mode1, radians.
Complex amplitudes, losses, noise, multiple photons, degrees, post-selection,
changed conventions or conflicting clauses require abstain.

Read the whole intent and all data. Do not silently change or ignore anything.
A future French hardware interest is allowed but physical access is unknown.
Do not output a claimed numerical result. If unsupported, ambiguous or invalid,
use action="abstain", task=null. Keep the task identifier exactly as specified.
