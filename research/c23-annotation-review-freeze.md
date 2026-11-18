# C23 — annotations indépendantes figées depuis le seul public

Le seul fichier C23 ouvert avant gel est
`runs/20261115-c23-compositional-repair/test_cases.json`, SHA-256
`fd8442be1df42c65bda00fb97a6d4627c638e69fea7211e0a8f3c8c9f8ae0ea1`.
Les vingt contrats sont enregistrés dans `private_gold.review.json`, format
`{cases:[...]}`, avec les six champs, langue, familles et justification.
Leur SHA-256 et la date de gel figurent dans
`research/c23-annotation-review-freeze.json`.

Aucun gold auteur, générateur, plan/protocole, provenance ou statut privé
C23 n'a été lu. Aucun prompt ou réponse C23 n'a été ouvert. Aucun modèle,
serveur, oracle ou calcul de faisabilité n'a été exécuté pour cette étape.

Les implications sont extraites séparément, dans le sens énoncé. En anglais,
«selection of A is conditional on selection of B» impose A vers B. Les
clauses réciproques sont conservées comme deux arcs et les cycles comme
leurs trois arcs explicites ; aucune fermeture transitive, interdiction ou
obligation dérivée n'est ajoutée. Les budgets absents restent `null`, même
si des coûts sont fournis. Chaque texte énonce trois implications distinctes,
soit soixante clauses dans les annotations ; dix textes sont français et dix
anglais. Aucune essentialité, faisabilité ou qualité de performance n'est
revendiquée par ce comptage.

Cette relecture relève d'un rôle LLM distinct, sans preuve d'annotation
humaine aveugle ou d'indépendance de modèle. Les labels sont figés avant
comparaison par l'intégrateur et ne seront pas réécrits silencieusement en
cas de désaccord. Le contrôle fini attend une autorisation et des références
séparées après ce gel.
