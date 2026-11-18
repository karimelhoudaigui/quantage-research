# C16 — annotations indépendantes et références finies

Les 8 intentions publiques de développement et les 16 intentions publiques
réservées ont été lues sans ouvrir le gold auteur, son générateur, sa
provenance, ni les prompts ou réponses C16. Les clauses ont été extraites
manuellement depuis le texte uniquement. Les données de coûts ne créent
aucun budget implicite ; une implication est à sens unique et ses clauses
explicites ne sont pas remplacées par leurs conséquences.

Le fichier demandé est
`runs/20261115-c16-quantized-repair/private_gold.review.json`, objet
`{cases:[...]}` avec identifiant, split, contraintes et justification. Il a
été figé avant comparaison par l'intégrateur ; SHA-256
`5c6faeb1d54dc989e789cbc64d7a45d14e6dc9e97208c7dcb1147f0c6cb6f135`.
Les deux publics et les labels sont identifiés dans
`research/c16-annotation-review-freeze.json`. Rôle LLM distinct, sans preuve
d'indépendance de modèle ni relecture humaine aveugle.

Le calcul `research/c16-annotation-oracle.py` est indépendant du code de
production et du gold auteur. Il énumère chaque sous-ensemble avec des
ensembles et des sommes entières, conserve tous les domaines et tous les
optima. Six contrôles calculables à la main vérifient indexation, coût
distinct du poids, sens d'implication, exclusion, contradiction de
cardinalité et ex æquo. Aucun modèle canonique de cet audit n'est transmis
à un processus d'inférence.

Trois domaines sont vides :

- `79769e445d63` : 1 est obligatoire et impose 2, alors qu'au plus une
  entrée est autorisée.
- `38289dce9fa8` : 3 est interdit ; 1 imposerait 3, donc ne peut être pris.
  Les seuls indices restants 0 et 2 sont incompatibles, alors qu'au moins
  deux entrées sont demandées.
- `192394ff7b7a` : 0 obligatoire impose 3. Les exclusions avec ces indices
  interdisent 1, 2 et 4, laissant seulement deux entrées pour un minimum de
  trois.

Les autres 21 domaines sont non vides. Le retrait séparé de chaque famille
énoncée — budget, minimum, maximum, obligation, interdiction ou implication —
a été contrôlé dans 70 cas de retrait. Chaque retrait agrandit effectivement
le domaine ; un masque témoin est conservé. Cette propriété est finie et
relative aux données présentes, sans garantie paramétrique.

Les signatures des 16 cas réservés, dérivées des seules annotations de revue,
sont distinctes entre elles et disjointes des signatures de mes 24
annotations C15 figées. Cela vérifie une séparation de combinaisons dans
ces deux corpus ; ce n'est ni une preuve de nouveauté scientifique, ni une
preuve de non-contamination du pré-entraînement ou de représentativité.

Provenance : `research/c16-annotation-oracle.contract.json` et
`research/c16-annotation-oracle/{raw.json,manifest.json}`. Le manifest v2 a le
statut `completed` et sa validation avec racine passe. Python 3.9.6,
arithmétique entière exacte, sans aléa, limite 30 s et thread conventionnel 1.
Les commandes complètes, sources et empreintes avant/après sont conservées.
Commande enfant :

```bash
python3 research/c16-annotation-oracle.py --output research/c16-annotation-oracle/raw.json
```

La destination existante est immuable et tout replay doit utiliser une
nouvelle destination. Aucun LLM, serveur d'inférence, QPU ou dépense externe
n'a été exécuté pour cette annotation et son contrôle fini. Statut :
références indépendantes prêtes pour l'audit ultérieur des réponses réelles.
