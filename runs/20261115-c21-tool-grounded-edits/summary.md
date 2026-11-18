# C21 — pilote de développement terminé

Deux anciennes erreurs C19, deux nouvelles réparations LLM : deux patches valides, une formulation fidèle. Le modèle ajoute lui-même `x5 - x4 <= 0` au cas 29507bb778cc ; sur les 64 affectations, domaine et valeurs d’objectif concordent ensuite. Le cas 417127d82203 conserve une implication inversée et des exclusions inventées. Le code applique seulement les éditions littérales.

Le feedback évalue les propres lignes candidates aux témoins, avec un gloss des verdicts. Le diagnostic passe à 768 caractères et la sortie à 1024 tokens. Ces changements sont conjoints : aucun effet causal isolé de l’outil n’est démontré. Les deux cas sont du développement sélectionné après C19, pas un test réservé.

La revue distincte du scorer mais non indépendante de l’auteur confirme 655 contrôles et 19 évaluations de lignes, sans nouvelle génération. Quatre sorties enregistrées DFS/HiGHS concordent sur les candidats ; seul le premier candidat est fidèle au contrat d’origine. Coûts des deux nouveaux appels : 3383 tokens d’entrée, 471 de sortie, 33,809 s de réponses ; phase 56,283 s. Les initiales historiques restent attribuées, le nettoyage est séparé et l’énergie demeure inconnue.

Suite : tester une capacité plus grande et une seconde réparation, puis figer une comparaison à trois appels par bras sur un nouveau corpus. Références : research/c21-observed-review.md/json, probe-score-v1/metrics.json.
