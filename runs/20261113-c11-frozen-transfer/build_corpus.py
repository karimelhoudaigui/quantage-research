"""C11 hand-written semantic pairs. No agent/verifier/output is imported.

The author wrote the 64 base intentions and 64 clause edits before seeing C11
model outputs. Data generation is seeded; labels concern the frozen complete
core contract at unchanged data, not equality of one numerical answer.
"""
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = 2026111511
R = 'R(t) = [[cos(t), -sin(t)], [sin(t), cos(t)]]. '
# Each tuple: genre, language, base intention, exact source clause,
# replacement clause, changed-clause tag, rejection reason.
MIS = [
('direct_request','en',
 'Choose a binary subset from the undirected conflict graph in data. My goal is the greatest sum of the supplied vertex weights; every edge forbids selecting its two ends together. There are no other requirements.',
 'the greatest sum of the supplied vertex weights','the smallest sum of the supplied vertex weights','objective_direction','Minimization replaces the maximum-weight objective; core fixes maximization.'),
('direct_request','fr',
 'Je cherche le poids total le plus élevé pour un choix de sommets binaires. Les arêtes du graphe sont non orientées et interdisent de retenir leurs deux extrémités. Aucun autre critère ne doit intervenir.',
 'le poids total le plus élevé','le nombre de sommets le plus élevé, en ignorant leurs poids','objective_quantity','Cardinality explicitly replaces total weight; unchanged weights cannot be silently set to one.'),
('direct_request','en',
 'Please return a maximum-weight independent set in this undirected graph. Each vertex is selected either zero or one times. Optimize weight without any restriction on the number chosen.',
 'without any restriction on the number chosen','subject to choosing exactly two vertices','cardinality_equality','An exact-size constraint is outside the unqualified weighted-MIS contract.'),
('direct_request','fr',
 'Trouver un sous-ensemble de poids maximal parmi les sommets du graphe non orienté fourni. Le choix est binaire et deux voisins ne peuvent être pris ensemble. Tous les sommets sont admissibles.',
 'Tous les sommets sont admissibles.','Le sommet 0 doit obligatoirement être retenu.','mandatory_vertex','A required vertex adds a constraint that cannot be dropped.'),
('direct_request','en',
 'For these weighted vertices, maximize the sum retained under binary choices and pairwise exclusions given by undirected edges. No vertex is singled out for special treatment.',
 'No vertex is singled out for special treatment.','Vertex 0 is forbidden, even if its weight would improve the total.','forbidden_vertex','An explicit exclusion is an additional constraint unsupported by core.'),
('direct_request','fr',
 'Sélectionner des sommets mutuellement non adjacents de poids cumulé maximal dans ce graphe non orienté. Une variable 0/1 correspond à chaque sommet. La taille du sous-ensemble est libre.',
 'La taille du sous-ensemble est libre.','Le sous-ensemble ne doit contenir plus de deux sommets.','cardinality_upper','An upper cardinality bound changes the complete requested contract.'),
('direct_request','en',
 'I want the largest possible total vertex weight with no selected undirected edge. Use binary selection variables and no further constraints. Resolve the objective in favor of total weight.',
 'Resolve the objective in favor of total weight.','I have not decided between total weight and cardinality; keep this objective choice unresolved.','ambiguous_objective','The final explicit instruction makes the objective unresolved; do not select a default.'),
('direct_request','fr',
 'Maximiser la somme des poids sur un ensemble indépendant du graphe non orienté fourni. Chaque sommet est un choix binaire, sans autre obligation. Seule la meilleure somme importe.',
 'Seule la meilleure somme importe.','Je veux seulement un ensemble maximal par inclusion, même si sa somme est inférieure au maximum.','maximal_vs_maximum','Inclusion maximality is requested instead of a maximum-weight optimum.'),
('lab_note','en',
 'Notebook entry: vertices are candidate assays and every undirected edge is an incompatibility. Record the subset with maximum total supplied weight. Selections are binary. There is no assay quota.',
 'There is no assay quota.','At least three assays must be selected.','cardinality_lower','A lower cardinality constraint is not represented by the frozen core.'),
('lab_note','fr',
 'Cahier de paillasse : un sommet représente une mesure, une arête non orientée une incompatibilité. Retenir un poids total maximal sans paire incompatible, avec des décisions binaires. Aucun plafond de poids supplémentaire.',
 'Aucun plafond de poids supplémentaire.','Imposer aussi un poids total inférieur ou égal à 5.','weight_budget','A new weight budget must be retained and is unsupported by core.'),
('lab_note','en',
 'Experiment log: data lists undirected exclusion edges between weighted tests. Compute the maximum sum of weights of a conflict-free subset. A test is wholly included or wholly omitted; there are no additional constraints.',
 'A test is wholly included or wholly omitted','A test may instead be selected in any real fraction from zero to one','variable_domain','Continuous fractional choices replace binary variables.'),
('lab_note','fr',
 'Note de protocole : les sommets portent les gains dans weights. Une arête non orientée interdit la sélection conjointe. Obtenir le gain cumulé maximal avec une décision binaire par sommet. Aucun lien logique supplémentaire.',
 'Aucun lien logique supplémentaire.','La sélection du sommet 0 impose aussi celle du sommet 1.','logical_implication','An implication between selections is an additional unsupported constraint.'),
('lab_note','en',
 'Bench record: I am comparing sets of mutually nonadjacent vertices in the undirected graph. Rank them only by the sum of given weights and return the maximum. Choices are binary and the empty set is allowed.',
 'Rank them only by the sum of given weights and return the maximum.','First maximize cardinality and only then maximize weight among tied sets.','lexicographic_objective','A cardinality-first lexicographic criterion differs from maximum total weight.'),
('lab_note','fr',
 'Journal expérimental : chercher un ensemble indépendant de poids total maximal. Le graphe des incompatibilités est non orienté, les choix sont binaires. Tous les groupes de sommets sont permis tant qu’ils sont indépendants.',
 'Tous les groupes de sommets sont permis tant qu’ils sont indépendants.','Parmi les sommets 0 et 1, exactement un doit être sélectionné.','exclusive_required_pair','An exactly-one constraint must not disappear during canonicalization.'),
('lab_note','en',
 'Lab handover: calculate a binary maximum-weight independent subset of the undirected graph in the attached data object. Use the provided weight of every chosen vertex. Impose only pairwise incompatibilities.',
 'Impose only pairwise incompatibilities.','Also require the number of chosen vertices to be even.','parity_constraint','A parity condition is outside the current independent-set contract.'),
('lab_note','fr',
 'Trace de laboratoire : maximiser les poids additionnés des sommets retenus, aucun couple retenu ne formant une arête non orientée. Chaque sélection vaut zéro ou un. Le sens de l’objectif est fixé à maximiser.',
 'Le sens de l’objectif est fixé à maximiser.','Le sens de l’objectif reste à clarifier entre maximiser et minimiser; ne le choisissez pas.','ambiguous_direction','An explicit unresolved objective direction requires clarification.'),
('collaborator_memo','en',
 'To the analysis team: please maximize the total supplied vertex weight over a binary independent set of this undirected graph. No requirement concerns how many vertices are chosen. Keep this as a local classical reference; Pasqal is only a possible future candidate.',
 'No requirement concerns how many vertices are chosen.','The set must contain exactly three vertices.','cardinality_equality','A prescribed set size is absent from the frozen solver contract; provider context adds no permission.'),
('collaborator_memo','fr',
 'Message à ma collègue : peux-tu calculer un ensemble indépendant de poids maximal pour ce graphe non orienté ? Les choix sont binaires, sans autre contrainte. Pasqal reste une piste future, je demande uniquement une référence locale.',
 'sans autre contrainte','avec l’obligation de retenir le sommet 1','mandatory_vertex','Mandatory inclusion is an extra mathematical condition, regardless of the local-provider context.'),
('collaborator_memo','en',
 'Dear collaborator, our exclusion graph is undirected and its nodes have the positive weights in data. Find a pairwise compatible binary subset with maximum weight sum. All nodes remain eligible for selection.',
 'All nodes remain eligible for selection.','Node 1 must be excluded from every returned solution.','forbidden_vertex','A forbidden vertex adds an explicit restriction.'),
('collaborator_memo','fr',
 'Pour ton analyse : il faut maximiser la somme des poids choisis, avec un choix binaire par sommet et exclusion des deux bouts de toute arête non orientée. Le sous-ensemble n’a pas de borne de taille.',
 'Le sous-ensemble n’a pas de borne de taille.','Le sous-ensemble doit avoir au moins deux sommets.','cardinality_lower','A lower set-size bound is not modeled by the unchanged core.'),
('collaborator_memo','en',
 'A note for the modeling colleague: treat each undirected edge as a hard conflict and each vertex decision as binary. The requested optimum is the highest total supplied weight. Do not add any other objective.',
 'The requested optimum is the highest total supplied weight.','The requested optimum is the smallest number of vertices, ignoring supplied weights.','different_objective','Minimum cardinality is a different requested optimization problem.'),
('collaborator_memo','fr',
 'Bonjour, pour ces essais en conflit non orienté, retenir une collection indépendante dont la somme des poids est la plus grande. Une décision binaire indique chaque inclusion. Le sommet 0 n’a aucun rôle particulier.',
 'Le sommet 0 n’a aucun rôle particulier.','Si le sommet 0 est retenu, le sommet 2 doit également l’être.','logical_implication','A conditional inclusion constraint is outside the plain-MIS feasible set specification.'),
('collaborator_memo','en',
 'For our joint study, please maximize the weight sum of a binary subset, never taking both endpoints of any undirected edge. There is no global weight limit or further condition.',
 'There is no global weight limit or further condition.','The total selected weight must additionally be at most 7.','weight_budget','The additional global budget cannot be removed from the semantic contract.'),
('collaborator_memo','fr',
 'À l’équipe : construire la référence locale de poids maximal pour un ensemble indépendant binaire du graphe non orienté. Appliquer les arêtes comme incompatibilités et aucune autre règle de sélection.',
 'aucune autre règle de sélection','exiger en plus un nombre impair de sommets retenus','parity_constraint','An odd-parity rule is a new constraint unsupported by core.'),
('structured_brief','en',
 'Task card. Objects: weighted vertices. Edges: undirected hard conflicts. Domain: one binary indicator per vertex. Objective: maximize the sum of selected weights. Extra constraints: none.',
 'Objective: maximize the sum of selected weights.','Objective: minimize the sum of selected weights.','objective_direction','The objective direction is changed to minimization.'),
('structured_brief','fr',
 'Fiche de calcul. Variables : sélection binaire des sommets. Contraintes : aucune arête non orientée ne peut avoir deux bouts sélectionnés. But : poids total maximal. Cardinalité : libre.',
 'Cardinalité : libre.','Cardinalité : exactement deux.','cardinality_equality','A fixed cardinality is additional and unsupported.'),
('structured_brief','en',
 'Analysis specification: choose an independent vertex subset of the supplied undirected graph; indicators are binary. Maximize its supplied total weight. Eligibility rules: only the graph conflicts.',
 'Eligibility rules: only the graph conflicts.','Eligibility rules: graph conflicts plus mandatory inclusion of vertex 2.','mandatory_vertex','The mandatory vertex cannot be omitted from formalization.'),
('structured_brief','fr',
 'Spécification. Graphe : non orienté. Variable par sommet : zéro ou un. Faisabilité : indépendance et aucune autre contrainte. Fonction à maximiser : somme des weights des sommets choisis.',
 'Faisabilité : indépendance et aucune autre contrainte.','Faisabilité : indépendance et interdiction de choisir le sommet 2.','forbidden_vertex','A named vertex exclusion changes the stated feasible set.'),
('structured_brief','en',
 'Model request / domain: binary subset / graph: undirected / hard rule: no adjacent pair selected / target: maximum sum of supplied weights / set size: unrestricted.',
 'set size: unrestricted.','set size: at most one selected vertex.','cardinality_upper','An at-most-one global cap is not part of ordinary weighted MIS.'),
('structured_brief','fr',
 'Contrat de référence : poids total maximal, sommets binaires, conflits donnés par les arêtes non orientées. Les poids doivent servir tels quels. L’objectif est entièrement déterminé.',
 'L’objectif est entièrement déterminé.','L’objectif reste indécis entre poids total et nombre de sommets; demander une clarification.','ambiguous_objective','The explicit undecided objective precludes automatic weighted-MIS canonicalization.'),
('structured_brief','en',
 'Research ticket: compute the largest vertex-weight total on an independent subset. The graph is undirected; selection is binary. There are no order or count constraints.',
 'There are no order or count constraints.','The selected cardinality must equal the selected cardinality of its complement.','balanced_cardinality','A balance/equal-partition requirement is an extra constraint.'),
('structured_brief','fr',
 'Demande structurée : maximiser la somme des poids fournis; une variable binaire par sommet; pour toute arête non orientée, au plus une extrémité choisie. Autres conditions : aucune.',
 'Autres conditions : aucune.','Autres conditions : exactement un des sommets 1 et 2 choisi.','exclusive_required_pair','An exactly-one pair constraint is not expressible by the unchanged plain-MIS contract.'),
]
PHOTO = [
('direct_request','en',
 'Please compute ideal probabilities at both output modes. Start with one photon in mode 0 and vacuum in mode 1, in a coherent lossless two-mode circuit. '+R+'Apply R(a), then exp(i*phi) on mode 1, and finally R(b). All three angles are radians.',
 'Start with one photon in mode 0 and vacuum in mode 1','Start with vacuum in mode 0 and one photon in mode 1','input_mode','The input occupation differs from the fixed |1,0> core contract.'),
('direct_request','fr',
 'Donner les deux probabilités idéales de sortie du circuit à deux modes, cohérent et sans pertes, depuis l’entrée |1,0>. '+R+'Traverser R(a), phase exp(i*phi) sur le mode 1, puis R(b). Les trois paramètres angulaires sont en radians.',
 'Les trois paramètres angulaires sont en radians.','Les trois paramètres angulaires sont en degrés; conserver ces nombres et ne pas les convertir.','units','Degree units cannot be silently reinterpreted as radians or converted against the explicit instruction.'),
('direct_request','en',
 'I need the distribution of the single photon across the two exit modes. The initial occupation is |1,0>, propagation is coherent and lossless. '+R+'Use R(a), a mode-1 phase exp(i*phi), then R(b), with every angle in radians.',
 'the distribution of the single photon across the two exit modes','the complex final amplitude in each of the two exit modes, rather than probabilities','observable','Complex amplitudes are requested instead of output probabilities.'),
('direct_request','fr',
 'Calculer les probabilités des deux sorties avec un photon initial au mode 0, le mode 1 vide. Utiliser une propagation cohérente et sans pertes. '+R+'La chronologie est R(a), exp(i*phi) au mode 1, R(b); a, b et phi sont en radians.',
 'Utiliser une propagation cohérente et sans pertes.','Ajouter à la propagation cohérente une probabilité de perte de 10 % après le dernier élément, même si le champ loss décrit le circuit initial sans pertes.','loss_model','A specified extra loss channel is outside the lossless core; loss cannot simply be ignored.'),
('direct_request','en',
 'Calculate the ideal two-output probability distribution for the coherent, lossless optical device. The incoming state is |1,0>. '+R+'Time order: R(a), phase exp(i*phi) on mode 1, R(b). Angles in data are radians.',
 'The incoming state is |1,0>.','Override the incoming occupation: one photon enters each mode, |1,1>; do not replace this two-photon question by a single-photon one.','photon_number','The explicit two-photon instruction is outside core and inconsistent with the retained single-photon data field.'),
('direct_request','fr',
 'Je demande les probabilités idéales dans les deux modes de sortie pour une entrée |1,0>. Le système à deux modes est cohérent et sans pertes. '+R+'Appliquer successivement R(a), une phase exp(i*phi) au mode 1, puis R(b). Unités : radians.',
 'Appliquer successivement R(a), une phase exp(i*phi) au mode 1, puis R(b).','Appliquer successivement R(a), puis R(b), et seulement ensuite la phase exp(i*phi) au mode 1.','component_order','A phase after both rotations changes the requested temporal sequence; the fixed core cannot represent it.'),
('direct_request','en',
 'Find both ideal exit probabilities for one photon prepared in input mode 0, with input mode 1 empty. Keep the two-mode transformation coherent and without loss. '+R+'The photon encounters R(a), then exp(i*phi) on mode 1, then R(b). Use radians.',
 'one photon prepared in input mode 0, with input mode 1 empty','one photon whose input mode is not determined; do not decide between input 0 and input 1','ambiguous_input','The explicitly unresolved input mode must not default to mode 0.'),
('direct_request','fr',
 'Obtenir la loi de probabilité idéale sur les deux sorties à partir d’un photon au mode 0 et du vide au mode 1. Circuit cohérent, sans pertes. '+R+'Ordre physique : R(a), phase exp(i*phi) au mode 1, R(b). Angles en radians.',
 'Obtenir la loi de probabilité idéale sur les deux sorties','Produire exactement 100 échantillons aléatoires de sortie, et ne pas retourner une distribution de probabilités','observable_sampling','A random-sample deliverable differs from the deterministic probability contract.'),
('lab_note','en',
 'Optics notebook: estimate no noise here; compute the ideal probabilities of the two exit ports. Initial state |1,0>, two coherent lossless modes. '+R+'Sequence R(a), phase exp(i*phi) on mode 1, R(b); all angles in radians.',
 'all angles in radians.','a and b in radians but phi in degrees; no numerical conversion is authorized.','mixed_units','The phase unit is changed and explicit conversion is disallowed.'),
('lab_note','fr',
 'Cahier optique : l’entrée est |1,0> et nous voulons les probabilités idéales des deux ports. Les deux modes restent cohérents et le circuit est sans pertes. '+R+'R(a) précède exp(i*phi) au mode 1, qui précède R(b). Paramètres en radians.',
 'le circuit est sans pertes','le circuit reçoit en plus une perte de 5 % après R(a), qui doit être modélisée sans changer les valeurs de data','loss_model','A position-specific extra loss model is required and not supported.'),
('lab_note','en',
 'Bench log: compute the ideal probability for each of two output modes, using coherent lossless propagation. Source occupation: one photon in mode 0, zero in mode 1. '+R+'Optical order is R(a), a phase exp(i*phi) on mode 1, R(b). Parameters are radians.',
 'Source occupation: one photon in mode 0, zero in mode 1.','Source occupation must instead be |2,0>: two photons in mode 0; retain this explicit source requirement.','photon_number','Two photons in one input mode require a multiphoton model.'),
('lab_note','fr',
 'Journal de mesure : calculer seulement la référence théorique idéale des deux probabilités de sortie. Source |1,0>, deux modes, cohérence maintenue et pertes nulles. '+R+'La suite est R(a), phase exp(i*phi) sur le mode 1, puis R(b); radians pour tous les angles.',
 'La suite est R(a), phase exp(i*phi) sur le mode 1, puis R(b)','La suite est d’abord phase exp(i*phi) sur le mode 1, puis R(a), et ensuite R(b)','component_order','Placing the phase before the first rotation is a different sequence outside the fixed core.'),
('lab_note','en',
 'Experimental note: return ideal probabilities for the two final modes, not a hardware acquisition. Inject |1,0> into a coherent lossless circuit. '+R+'Use R(a), mode-1 phase exp(i*phi), R(b), with a, b and phi in radians.',
 'return ideal probabilities for the two final modes','return the argument (phase angle) of each final complex amplitude, rather than output probabilities','observable','Phases of amplitudes are distinct from their probabilities.'),
('lab_note','fr',
 'Trace de paillasse : obtenir les probabilités idéales des deux issues. Un photon occupe initialement le mode 0, le mode 1 est vide; propagation cohérente à deux modes sans pertes. '+R+'Éléments dans l’ordre R(a), exp(i*phi) sur mode 1, R(b); angles en radians.',
 'Un photon occupe initialement le mode 0, le mode 1 est vide','Le mode occupé par le photon initial n’a pas encore été choisi entre 0 et 1; aucune hypothèse n’est autorisée','ambiguous_input','An explicitly unspecified source occupation requires clarification.'),
('lab_note','en',
 'Notebook calculation: derive both ideal output-mode probabilities from the fixed input |1,0>. The two modes are coherent with zero loss. '+R+'Apply R(a), then phase exp(i*phi) on mode 1, then R(b). Use radian angle values.',
 'Use radian angle values.','Use degree angle values for a and b and radians for phi; do not convert any values in data.','mixed_units','Rotation angles are not radians as required by core, with conversion explicitly forbidden.'),
('lab_note','fr',
 'Compte rendu optique : calculer la distribution idéale des deux ports pour |1,0>. Deux modes cohérents, aucun bruit ni perte. '+R+'Le montage traverse R(a), exp(i*phi) au mode 1, puis R(b). Chaque angle est en radians.',
 'aucun bruit ni perte','une probabilité de perte finale de 20 % à ajouter au montage de base et à inclure dans les résultats','loss_model','The requested final loss channel invalidates the ideal lossless contract.'),
('collaborator_memo','en',
 'To my optics collaborator: please compute both ideal output probabilities locally, with one photon at input 0 and vacuum at input 1. Assume two coherent lossless modes. '+R+'Follow R(a), mode-1 phase exp(i*phi), then R(b); use radians. Quandela is a conditional future interest, not a submission request.',
 'one photon at input 0 and vacuum at input 1','one photon at input 1 and vacuum at input 0','input_mode','The input mode is changed; future-provider context does not restore the fixed input contract.'),
('collaborator_memo','fr',
 'À ma collègue : j’ai besoin des deux probabilités idéales, calculées localement depuis |1,0>. Garder deux modes cohérents et sans pertes. '+R+'Chronologie : R(a), exp(i*phi) sur le mode 1, R(b). Tous les angles sont en radians. Quandela reste seulement une piste future.',
 'j’ai besoin des deux probabilités idéales','j’ai besoin des parties réelles et imaginaires des deux amplitudes finales, pas de leurs probabilités','observable','The requested complex-amplitude components are not the probability deliverable.'),
('collaborator_memo','en',
 'Dear colleague, take the ideal two-mode coherent circuit without loss and the input |1,0>. Report a probability for each exit. '+R+'First perform R(a), then phase exp(i*phi) on mode 1, and last R(b). Angles supplied are radians.',
 'the input |1,0>','the input |0,2>, overriding the single-photon field: two photons in the second mode','photon_number','A declared two-photon source is not representable by the one-photon core.'),
('collaborator_memo','fr',
 'Pour notre échange : déterminer les probabilités idéales des modes de sortie 0 et 1 pour une source |1,0>. Propager de façon cohérente, sans pertes. '+R+'La source voit R(a), la phase exp(i*phi) sur le mode 1, puis R(b). Les nombres fournis sont des radians.',
 'La source voit R(a), la phase exp(i*phi) sur le mode 1, puis R(b).','La source voit R(a), puis R(b), et enfin la phase exp(i*phi) sur le mode 1.','component_order','The specified temporal order moves the phase to the end.'),
('collaborator_memo','en',
 'For our local comparison, give the ideal probabilities of both exit modes. The source is |1,0>; retain coherence, two modes and zero loss. '+R+'The component sequence is R(a), exp(i*phi) on mode 1, R(b). Interpret all angles in radians.',
 'Interpret all angles in radians.','Interpret all angles in degrees while preserving their numeric values; conversion and radian reinterpretation are forbidden.','units','The explicit angular units are outside the fixed radian contract.'),
('collaborator_memo','fr',
 'Message pour l’analyse optique : avec un photon au mode 0 et rien au mode 1, calculer la probabilité de chaque sortie du montage idéal à deux modes. Le circuit est cohérent et sans pertes. '+R+'Appliquer R(a), exp(i*phi) au mode 1, R(b), angles en radians.',
 'Le circuit est cohérent et sans pertes.','Le circuit est cohérent mais ajouter une perte de 8 % au mode de sortie 1 et conserver cette asymétrie dans les probabilités.','loss_model','A mode-specific attenuation model cannot be silently replaced by lossless propagation.'),
('collaborator_memo','en',
 'For the joint notebook, compute the ideal distribution on output ports 0 and 1. Initially mode 0 has one photon and mode 1 has vacuum; the network is coherent and lossless. '+R+'Temporal order: R(a), phase exp(i*phi) on mode 1, R(b). Radians throughout.',
 'Initially mode 0 has one photon and mode 1 has vacuum','Initially there is one photon but we have not identified its input port; do not choose a port for us','ambiguous_input','The source port remains unresolved by explicit instruction.'),
('collaborator_memo','fr',
 'À l’équipe photonique : fournir les probabilités idéales sur les deux sorties, entrée |1,0>, cohérence et pertes nulles. '+R+'Dans le temps : R(a), phase exp(i*phi) au mode 1, puis R(b), tous les angles en radians.',
 'fournir les probabilités idéales sur les deux sorties','fournir une chaîne de 50 détections simulées aléatoirement, sans retourner les probabilités','observable_sampling','A shot sequence is requested, not the deterministic probability output.'),
('structured_brief','en',
 'Optical task card. Input: |1,0>. Model: two modes, coherent, ideal and lossless. Output: both mode probabilities. '+R+'Time order: R(a), phase exp(i*phi) on mode 1, R(b). Units: radians.',
 'Input: |1,0>.','Input: |1,1>, two photons; do not collapse this instruction to one photon.','photon_number','A two-photon input is outside the one-photon contract, despite unchanged data.'),
('structured_brief','fr',
 'Fiche optique. Source : un photon au mode 0, vide au mode 1. Hypothèses : deux modes cohérents sans pertes. Sortie : distribution idéale sur les deux modes. '+R+'Chronologie : R(a), exp(i*phi) au mode 1, R(b). Unité : radian.',
 'Chronologie : R(a), exp(i*phi) au mode 1, R(b).','Chronologie : exp(i*phi) au mode 1, R(a), R(b).','component_order','The phase is moved before the first rotation; core chronology is fixed.'),
('structured_brief','en',
 'Reference specification / source: |1,0> / network: coherent, ideal, lossless, two modes / result: probability of each output. '+R+'Execute in time R(a), exp(i*phi) on mode 1, R(b). All angles use radians.',
 'All angles use radians.','All angles use turns, with one turn equal to a full revolution; do not convert the supplied values.','units','Turns are different from radians and conversion is explicitly disallowed.'),
('structured_brief','fr',
 'Spécification de calcul : entrée |1,0>, circuit idéal cohérent à deux modes et sans pertes, probabilités des modes 0 et 1 en sortie. '+R+'Suite temporelle R(a), exp(i*phi) au mode 1, R(b); paramètres en radians.',
 'sans pertes','avec une perte de 12 % à ajouter après R(b), à inclure même si data.loss vaut zéro pour le circuit initial','loss_model','The additional loss channel is explicitly required and unsupported.'),
('structured_brief','en',
 'Computation ticket. Start state |1,0>; two coherent modes; zero loss. Return ideal output probabilities. '+R+'Apply R(a), the phase exp(i*phi) on mode 1, then R(b); radians for a, b and phi.',
 'Return ideal output probabilities.','Return the two complex output amplitudes, including their phases, instead of probabilities.','observable','Complex amplitudes cannot be substituted by their squared magnitudes.'),
('structured_brief','fr',
 'Contrat optique : deux modes, propagation cohérente idéale, pertes nulles; entrée fixée à |1,0>; calcul des deux probabilités de sortie. '+R+'Ordre R(a), phase exp(i*phi) sur le mode 1, R(b), angles en radians.',
 'entrée fixée à |1,0>','entrée non déterminée entre |1,0> et |0,1>, sans autorisation de choisir','ambiguous_input','The initial occupation is explicitly unknown; the fixed source may not be assumed.'),
('structured_brief','en',
 'Study brief: obtain both ideal output-mode probabilities from input |1,0> in a two-mode coherent lossless network. '+R+'Required chronology is R(a), mode-1 phase exp(i*phi), R(b). Parameter units are radians.',
 'Required chronology is R(a), mode-1 phase exp(i*phi), R(b).','Required chronology is R(a), then R(b), then the mode-1 phase exp(i*phi).','component_order','Placing the phase at the end is an unsupported temporal arrangement.'),
('structured_brief','fr',
 'Demande de référence. Source |1,0>. Circuit cohérent idéal à deux modes, pertes nulles. Livrable : probabilités des deux modes. '+R+'Passer par R(a), exp(i*phi) sur mode 1, R(b); a, b et phi en radians.',
 'Source |1,0>.','Source |3,0> : trois photons dans le mode 0, cette instruction remplace le champ photons de base.','photon_number','Three-photon propagation is outside the fixed single-photon implementation.'),
]

def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def build():
    assert len(MIS) == len(PHOTO) == 32
    rng = random.Random(SEED)
    public, gold = [], []
    genre_counts = {}
    for family, specs in [('mis', MIS), ('photon', PHOTO)]:
        for i, (genre, language, intent, anchor, replacement, clause, reason) in enumerate(specs):
            assert intent.count(anchor) == 1, (family, i, anchor)
            bad = intent.replace(anchor, replacement)
            assert bad != intent
            if family == 'mis':
                n = 4 + (i % 9)
                edges = [[a,b] for a in range(n) for b in range(a+1,n) if rng.random() < (0.15+0.08*(i%5))]
                data = {'n':n,'edges':edges,'weights':[rng.randint(1,11) for _ in range(n)]}
            else:
                # Avoid degenerate zero phases/angles; finite non-grid values.
                data={'a':round(rng.uniform(-1.41,1.39),7), 'b':round(rng.uniform(-1.32,1.47),7),
                      'phi':round(rng.uniform(-3.03,3.07),7),'photons':1,'modes':2,'loss':0}
            group_id='g_'+digest('quantage-c11-group:'+str(SEED)+':'+family+':'+str(i))[:16]
            genre_counts[family+':'+genre] = genre_counts.get(family+':'+genre,0)+1
            for j,(text,action,changed,rationale) in enumerate([
                (intent,'propose',None,'All required clauses match the frozen '+family+' core contract; data are within its bounds. The request is a local reference, without inferred hardware entitlement.'),
                (bad,'abstain',clause,reason)]):
                case_id='q_'+digest('quantage-c11-case:'+str(SEED)+':'+group_id+':'+str(j))[:16]
                public.append({'id':case_id,'group_id':group_id,'request':{'intent':text,'data':data}})
                gold.append({'id':case_id,'group_id':group_id,'family':family,'expected_action':action,
                             'expected_task':family if action=='propose' else None,
                             'changed_clause':changed,'rationale':rationale,'language':language})
    # Opaque identifiers and shuffled case order; no expected label in public.
    rng.shuffle(public)
    gold_by_id={x['id']:x for x in gold}
    gold=[gold_by_id[x['id']] for x in public]
    assert len({x['id'] for x in public})==128
    assert len({x['group_id'] for x in public})==64
    assert len({x['request']['intent'] for x in public})==128
    assert set(public[0])=={'id','group_id','request'}
    for group in {x['group_id'] for x in public}:
        pair=[x for x in public if x['group_id']==group]
        assert len(pair)==2 and pair[0]['request']['data']==pair[1]['request']['data']
    for filename,values in [('public_cases.json',public),('private_gold.author.json',gold)]:
        (ROOT/filename).write_text(json.dumps(values,ensure_ascii=False,indent=2)+'\n')
    return public,gold,genre_counts


if __name__=='__main__':
    public,gold,genres=build()
    print(json.dumps({'cases':len(public),'groups':len({x['group_id'] for x in public}),
                      'families':{f:sum(x['family']==f for x in gold) for f in ['mis','photon']},
                      'actions':{a:sum(x['expected_action']==a for x in gold) for a in ['propose','abstain']},
                      'languages':{a:sum(x['language']==a for x in gold) for a in ['en','fr']},
                      'genres_by_group':genres},ensure_ascii=False))
