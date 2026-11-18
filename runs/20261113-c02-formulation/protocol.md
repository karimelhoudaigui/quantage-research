# C02 — portée des certificats et mutations contrôlées

Préenregistré après C01, avant C02. Base Git fee83eb, arbre de travail avec
C01; parent de preuve : results/manifest.json de C01. Priorité agent_learning.

Question : contrôler une solution optimale ou la normalisation suffit-il à
garantir la fidélité d'une formulation ? Hypothèse : des erreurs survivent à
ces contrôles faibles. Les transformations équivalentes doivent être conservées.

Entrées C01 de développement : tous les graphes n<=4 (75), 100 graphes pondérés
seed 20261113, grille optique 125 (aucune revendication test indépendant).
MIS, sept mutations fixes : signe des termes linéaires, pénalité zéro,
pénalité égale au poids maximal, suppression première arête, multiplication
globale positive par 3, constante +7, doublement des interactions.
Optique, huit mutations : phase omise, phase négative, demi-angles, mélange
incohérent, amplitudes réelles au lieu de probabilités, phase globale,
ordre inversé des rotations, déplacement de phase sur l'autre mode.

L'effet d'une mutation est défini à l'instance : changement d'ensemble des
optima MIS ou de probabilités >1e-12. Une mutation sans effet n'est pas une
erreur à détecter. Baselines : dimensions seules; une solution retournée
optimale et faisable (MIS) / normalisation et positivité (optique);
égalité syntaxique stricte; vérification de tous les optima ou probabilités.

Rapporter pour chaque famille/mutation nombre effectif, rejets, erreurs
acceptées, transformations équivalentes rejetées. Pas de taux extrapolé aux
sorties LLM : opérateurs synthétiques choisis, oracle disponible par construction.
Conserver propositions et sorties complètes dans raw.jsonl, dont K2 P=1.
L'égalité d'optima n'atteste pas la fidélité de tous les coefficients et ne
détecte pas un changement d'intention AVANT l'oracle normalisé.

Budget local Python <=60 s, pas d'apprentissage; seed héritée de C01.
Commande : python3 -m quantage.faultstudy --output RUN/results.
Versions, commandes, hashes avant/après, commit, durée via manifest v2.
Revue : auto-vérification, délégation bloquée par quota. Arrêt sur exception.
