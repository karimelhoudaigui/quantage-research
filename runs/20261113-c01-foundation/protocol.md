# C01 — chaîne déterministe et oracles finis

Préenregistrement local, 2026-11-13, avant toute exécution du benchmark.
Base Git : fee83eb (arbre initial propre). Priorité backlog : agent_learning,
avec optimization et photonics comme deux bancs d'essai d'une même question.

Question : une chaîne structurée peut-elle préserver les solutions d'un MIS
pondéré et les probabilités d'un interféromètre idéal dans un petit domaine
entièrement vérifiable ? Hypothèse : aucune divergence sur ce domaine déclaré.
Ce cycle établit un socle déterministe, aucune performance de LLM.

Entrée : intention en langage contrôlé + données JSON. Sortie : problème
normalisé, formulation, vérification, solveur local et candidat matériel
conditionnel. Aucun interprète universel de langue naturelle.

MIS : graphe simple non orienté, poids entiers positifs, x_i dans {0,1};
maximiser somme w_i x_i sous x_i+x_j<=1 sur chaque arête.
Q(x)=-somme w_i x_i+P somme_(i,j) x_i x_j, P=1+max w_i.
Comparer TOUS les minimiseurs à l'ensemble des optima du problème contraint.
Tous les graphes étiquetés de n=1..5, poids unitaires; 20 graphes pondérés
par n=2..6, poids 1..5, seed 20261113, Random Python. Énumération exacte
comme référence forte à ces tailles; glouton déterministe comme heuristique.

Photonique : un photon en mode 0, deux modes, réseau sans pertes
U=R(b) diag(1,exp(i phi)) R(a), R(t)=[[cos t,-sin t],[sin t,cos t]].
Probabilités |U_j0|^2; comparaison à une expression trigonométrique développée.
Grille a,b dans {0,pi/8,pi/4,3pi/8,pi/2}, phi dans {0,pi/3,pi/2,pi,2pi}
(125 cas); pas de bruit, shots, SDK ou QPU. Tolérance absolue 1e-12.

Métriques : ensemble des optima identique, validité de chaque minimiseur,
erreur absolue des probabilités, normalisation, écart glouton/optimum,
temps local et nombre d'états évalués. Pas d'intervalle statistique sur une
population naturelle : recensement synthétique et échantillon de convenance.
Pas d'entraînement; C01 sert de développement, pas de test de généralisation.

Budget : Python standard local, maximum 60 s pour benchmark, arrêt à la première
exception; zéro dépense externe, aucun appel LLM/QPU. Versions observées dans
manifest.json; Python 3.9.6 disponible. Revue indépendante tentée mais bloquée
par quota des sous-agents; auto-revue explicitement signalée.

Commande prévue : python3 -m quantage.benchmark foundation --output RUN/results
avec RUN=runs/20261113-c01-foundation, via runner de provenance Mathbox.
Autres livrables : audit reprise, sources primaires, carte des huit axes.
