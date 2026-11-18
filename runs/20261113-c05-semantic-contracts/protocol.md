# C05 — contrat explicite des propositions externes

Préenregistrement avant exécution du nouveau test, 2026-11-13. Reprise C04,
commit fee83eb4575198e3e142d41c621300b4d11361d8 avec arbre local modifié.
Les preuves C01–C04 sont réutilisées et leurs fichiers hashés restent figés.
Question backlog agent_learning : quelles validations sont nécessaires avant
d'appliquer un certificat numérique à une proposition d'agent externe ?

Hypothèse : l'acceptation d'une sortie sur une instance ne garantit pas la
validité du schéma ni des domaines numériques. Le vérificateur C01 supposait
des modèles construits par son propre générateur; une frontière explicite est
nécessaire pour les modèles externes.

Audit indépendant confié à independent_audit, sans historique de conversation
hérité, sur les fichiers bruts. Il lit aussi les consignes et états du dépôt :
indépendance d'auteur, pas revue aveugle ni indépendance de modèle garantie.
Son périmètre d'écriture est limité à son rapport et audit_cases.json C05.
Littérature et matériel revus en parallèle dans deux rapports distincts.

Implémentation nouvelle et séparée : schéma de proposition externe, champs
obligatoires, enums, tailles, types numériques finis, indices et unicité des
termes, ordre et convention optiques explicites. Aucun changement silencieux
du sens de minimisation ou d'un champ inconnu. Des transformations valides
préservant les optima/probabilités doivent rester acceptées.

Tester les contre-exemples effectivement fournis par l'audit, des contrôles
valides pour les deux familles, et des variantes malformées pré-déclarées :
sense inconnu, indices négatifs/hors domaine, doublons de termes, NaN/Inf,
booléens au lieu de nombres, ordre/mode/output/coherent inconnus, dimensions
fausses, tolérances non positives/non finies et famille inconnue. Le test
porte sur validation de proposition, pas compréhension du langage naturel.

Comparaison : ancien verify et nouvelle frontière, mêmes cas, avec résultat
valide/invalide fixé par le schéma et les équivalences autorisées. Conserver
les cas, sorties et exceptions dans raw.jsonl. Métriques : fausses acceptations
de schéma, faux rejets des contrôles et erreurs d'exécution. Aucun entraînement
ni données de test LLM. Cas conçus pour audit, pas population naturelle.

Budget Python standard <=60 s, tailles <=4 pour MIS et deux modes/un photon;
pas de hasard pour ces cas. Tests et manifest v2 avec hashes avant/après,
versions et commandes. Aucun QPU, dépense externe ni Codex imbriqué.
Critère de fin : frontière testée et revue séparément, puis passage C06 aux
vraies propositions natives d'agents si quota disponible.
