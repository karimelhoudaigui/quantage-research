# C04 — auto-vérification du transfert à code figé

24 requêtes : 6 canoniques, 6 paraphrases équivalentes, 6 intentions changées,
6 entrées invalides. Les cas MIS valides ont n=7,8,8, au-delà des tailles C01;
les cas optiques utilisent trois triplets tirés avec seed 20261114. Les paires
de langage partagent ces mêmes données. Aucun apprentissage, test aveugle ou
représentativité de population. Corpus écrit en connaissant le parseur.

Le moteur strict accepte les 6 canoniques, refuse les 6 paraphrases et les
12 cas hors contrat. Couverture 6/12, fausses acceptations 0/12, faux refus 6.
La règle mots-clés accepte les 12 contrats équivalents et les 6 intentions
changées; elle refuse les 6 entrées invalides. Couverture 12/12, fausses
acceptations 6/12. Les 18 sorties acceptées ont un certificat numérique valide,
y compris les 6 mauvaises interprétations. «Confiance» et calibration ne sont
pas mesurées : les deux méthodes ne produisent aucun score probabiliste.

Les labels portent sur la tâche complète. Exemple : «Count all independent
sets» ne demande pas un maximum de poids. Les descriptions avec pertes/bruit
contredisent les données idéales; elles exigent abstention plutôt qu'une
interprétation silencieuse. Un optimum du problème normalisé ne certifie pas
que le texte a été correctement normalisé. Les résultats réfutent une
prétention de généralisation linguistique du socle strict, pas celle d'un LLM.

Contrôle de gel : core.py, verification.py et benchmark.py ont les mêmes
SHA-256 dans les manifests C01 et C04. Cases.json a été écrit avant exécution;
generation-command.txt documente sa génération. L'évaluation lit ce fichier
figé et n'utilise pas de hasard supplémentaire.
Commandes, version et hashes avant/après dans results/manifest.json.
Revue indépendante bloquée par quota. Métriques à réagréger à partir des lignes
brutes avec scripts/audit_results.py dans la vérification finale.
