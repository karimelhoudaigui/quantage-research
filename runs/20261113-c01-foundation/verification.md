# Vérification C01 — auto-revue, non indépendante

Contrat fini : 1099 graphes simples étiquetés non pondérés n=1..5, 100 graphes
pondérés seed 20261113, 125 triplets optiques déclarés. Le générateur parcourt
1+2+8+64+1024=1099 graphes; l'échantillon pondéré n'est pas exhaustif.

Résultats lus dans results/raw.jsonl et metrics.json : 1199 MIS, 125 optiques,
zéro rejet/divergence; 36346 états binaires vérifiés au total. Erreur maximale
optique 2.220446049250313e-16 (tolérance 1e-12). Le glouton est sous-optimal
sur 4 MIS avec écart absolu maximum 2. Pas de comparaison d'avantage quantique.

Le solveur QUBO énumère des bitstrings et l'oracle des sous-ensembles faisables,
sans pénalité; l'optique propage les amplitudes contre une expression développée.
Ce sont deux algorithmes écrits par la même personne, pas deux équipes.
Le vérificateur certifie les optima sur une instance, pas chaque coefficient
ni l'équivalence universelle d'un générateur. C02 éprouvera cette distinction.

Tests : python3 -m unittest discover -s tests -v : 5 tests réussis avant le run.
K2 avec pénalité égale au poids révèle explicitement le minimiseur infaisable
ex æquo; test de poids contre cardinalité; interférence contre mélange;
phase globale invariante; entrées invalides et absence de faux accès matériel.
Manifest v2 validé par validate_manifest.py --root .; run.status=completed,
empreintes d'entrées observées avant/après identiques. Commande exacte,
version Python, machine, durée et commit de départ dans results/manifest.json.

Limites : registre auto-vérifié; absence de relecteur indépendant due au quota
des trois sous-agents. Aucun entraînement/test LLM, appel LLM, SDK ou QPU.
Les temps sont ceux du calcul local; le coût de cette session de rédaction
et de raisonnement n'est pas mesuré et n'est pas égal à zéro.

Addendum de clôture, réagrégation sans toucher aux résultats : 5 répétitions
parmi les MIS pondérés/canoniques; 1199 évaluations MIS pour 1194 requêtes
distinctes, plus 125 requêtes optiques distinctes. Les 1099 graphes exhaustifs
non pondérés sont distincts. Aucune indépendance statistique entre répétitions.
