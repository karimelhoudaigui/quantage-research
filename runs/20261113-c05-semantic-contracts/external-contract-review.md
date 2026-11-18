# C05 — revue indépendante de la nouvelle frontière externe

Verdict : **implémentation et assertion finie vérifiées dans le périmètre testé**. Aucun contre-exemple trouvé à la frontière `verify_external` pour le schéma annoncé. Les 109 cas déterministes concordent avec les attentes de l'auditeur : 67 propositions de l'audit initial et 42 cas discriminants supplémentaires. Ce résultat porte sur le schéma explicite et les sorties de chaque instance, sans estimation d'un taux de détection sur une population de propositions d'agents.

Cette revue est réalisée par l'auditeur distinct de l'auteur de `contracts.py`, après l'audit initial du moteur figé. Il n'est pas établi que les agents utilisent des modèles différents. La revue n'est pas aveugle : les instructions imposent la lecture de l'état du dépôt et `labels.json` a été inspecté. Les labels de l'intégrateur n'ont toutefois pas été utilisés comme oracle : les huit contrôles manuels et les trois transformations admissibles viennent de l'audit initial; les autres attentes sont déduites du domaine annoncé et des résultats mathématiques de l'instance. Aucun code, label ou artefact antérieur n'est modifié.

## Contrat audité

Le problème doit être un objet normalisé de famille MIS pondéré ou optique idéale à deux modes et un photon. La normalisation reconstruit une requête contrôlée et repasse par `understand`. Cela réutilise la validation de taille, poids, graphes simples, nombre de modes, pertes nulles et angles finis; les champs de tâche, l'entrée optique et les champs inconnus sont aussi contrôlés dans `normalize_problem`.

Les QUBO externes admettent uniquement des coefficients et une constante entiers Python, des listes de dimensions correctes, des termes uniques avec `0<=i<j<n`, et les sens explicitement nommés `minimize` ou `maximize`. Les booléens et flottants sont exclus de ce domaine entier. La métadonnée `penalty` est facultative; si présente, elle doit être entière et égale à chaque coefficient quadratique. Ce schéma autorise des QUBO généraux sans métadonnée uniforme. Il n'impose pas une pénalité positive pour un modèle réécrit en maximisation : la négation de l'énergie avec changement du sens reste admissible. Une métadonnée sur une liste de termes vide n'a aucune conséquence énergétique.

L'optique exige des angles réels finis, des modes entiers zéro ou un, un ordre explicitement nommé, un booléen pour `coherent` et `output="probabilities"`. Le choix explicite d'un autre mode ou d'un modèle incohérent peut rester admissible quand il préserve les probabilités de cette instance. La tolérance doit être réelle finie, strictement positive et au plus `1e-6`; elle demeure une tolérance numérique configurable.

Après validation de ces conditions, le module délègue à l'ancien oracle et ajoute `stage="finite_output"`, `scope="this normalized instance only"`. Il ne prétend pas certifier une amplitude complexe ou le comportement sur une autre entrée, ni comprendre le texte initial. La restriction entière empêche l'overflow flottant du contre-exemple MIS initial; les entiers arbitrairement grands restent exacts dans le solveur exhaustif.

## Exécution et cas bruts

Python 3.9.6, `macOS-26.2-arm64-arm-64bit`, bibliothèque standard, commit `fee83eb4575198e3e142d41c621300b4d11361d8`, arbre modifié. Aucun appel réseau, modèle externe, QPU ou Codex imbriqué; aucune lecture de secret ni dépense. Le moteur des 109 cas a pris `0.0024633750000000038` seconde à son premier enregistrement. Les cas sont exploratoires, construits pour discriminer des erreurs précises; pas de seed ni de tirage aléatoire. Les problèmes MIS valides testés ont au plus trois sommets; un cas de taille treize teste le rejet du domaine.

Empreintes SHA-256 avant/après identiques :

| Entrée | SHA-256 |
| --- | --- |
| `quantage/contracts.py` | `652d64ff6051ed0f621b2d9dca1918e89cc9efc8bf2bc10f3702e97226ac28ef` |
| `quantage/core.py` | `35001246743a201d2326a53a586fd50bedca48d8e322f52124f2a3e0c7403be2` |
| `quantage/verification.py` | `c7d070281763bb46ad6244ef1c0bc4734c159bc32d5adca1dfac6e9786f6426f` |
| `audit_cases.json` initial | `24318900c9e929b4284f29e0961e4934466d2d6b5a1ccd1a9a7c194631fd4edd` |

`external-contract-audit.json` contient les problèmes et modèles complets, les tolérances, les attentes établies indépendamment, leur justification, les retours de `normalize_problem`, les sorties et exceptions, le code de replay et un manifeste v2. Les cas initiaux sont lus comme données; leur `replay_source` n'est pas exécuté pour cette nouvelle revue. Le code de replay propre à cette revue a été écrit et inspecté par l'auditeur.

Empreintes internes, calculées comme dans le rapport initial (`json.dumps` trié, séparateurs compacts, JSON strict; UTF-8 pour le code) :

| Contenu intégré | SHA-256 |
| --- | --- |
| `cases` | `e05a1b3212bfbf07d3b782feb682a585dc9060b5d7cb27aa65a4c14468aa4360` |
| `recorded_run.results` | `47267c1db97a15b3892dc9d8d3f757d22a7f5e80448035e54e2caa8cf4197385` |
| `replay_source` | `3459535351118e96b338ff9c5f9d698ca8503d30b1a547993b8919392f86eb1c` |

Le manifeste référence les fichiers exécutés et le rapport par empreinte. Les cas supplémentaires et la source de replay résident dans le manifeste lui-même; les empreintes intégrées ci-dessus évitent une dépendance d'empreinte récursive et permettent de contrôler ces données. La provenance centrale du cycle doit également conserver l'empreinte du fichier JSON complet.

## Résultats et cas discriminants

| Groupe | Rejet au schéma | Rejet après comparaison des sorties | Acceptation attendue | Divergence/exception imprévue |
| --- | ---: | ---: | ---: | ---: |
| 67 propositions initiales | 54 | 2 | 11 | 0 |
| 42 cas supplémentaires | 27 | 2 | 13 | 0 |

Les six requêtes `pipeline_boundary` de l'audit initial sont exclues de cette comparaison de propositions. Les 11 contrôles initiaux admis sont les huit cas calculables à la main, le décalage de constante, l'échelle entière positive et la phase globale. Les deux modèles initiaux rejetés après validation du schéma sont le mélange incohérent sur le cas interférent et le changement d'angle à tolérance par défaut. Aucun cas malformé initial n'est accepté par la nouvelle frontière.

Les cas supplémentaires contrôlent des conséquences sémantiques utiles, et pas seulement la présence de branches de validation :

- La négation de tous les termes QUBO avec le sens `maximize` et une métadonnée négative cohérente conserve l'optimum; elle est acceptée. Un facteur entier `10**400`, un grand décalage de constante et des poids du même ordre sont également acceptés avec arithmétique exacte.
- La métadonnée absente reste admissible, y compris pour une autre interaction positive suffisante. Une métadonnée contradictoire ou flottante est rejetée. Des termes doublons, inversés ou diagonaux sont rejetés par le schéma annoncé.
- L'omission de l'arête d'un K2 pondéré et la pénalité frontière égale à un sur le K2 non pondéré sont des QUBO syntaxiquement admissibles mais introduisent un optimum incorrect ou infaisable ex aequo. Ils sont rejetés à l'étape des sorties.
- La normalisation accepte une arête retournée `[1,0]` en la canonicalisant. Elle rejette objectifs, contraintes, familles ou champs inconnus, booléens dans les tailles et poids, arêtes dupliquées et taille hors domaine. En optique, les booléens dans l'entrée, les modes, les pertes et les angles sont rejetés; une autre entrée normalisée ou un observable d'amplitudes est rejeté.
- L'ordre inversé, la phase opposée, la phase sur l'autre mode et une très grande phase globale restent acceptés quand les probabilités sont conservées. Un mode d'entrée un sur un circuit équilibré et un modèle incohérent après une première rotation nulle sont explicitement valides et conservés.
- Les tolérances zéro, booléenne, excessive, textuelle ou nulle sont rejetées au schéma. La borne autorisée `1e-6` est acceptée. Aucune tolérance infinie n'atteint le vérificateur numérique.

## Reproduction et limites

Depuis la racine du dépôt :

```bash
python3 -m unittest discover -s tests -p test_contracts.py -v
python3 -c 'import json; from pathlib import Path; exec(json.loads(Path("runs/20261113-c05-semantic-contracts/external-contract-audit.json").read_text())["replay_source"])'
```

Les cinq tests existants de la nouvelle frontière passent. Le replay indépendant des 109 lignes donne les mêmes sorties, normalisations et empreintes, après exclusion du seul temps d'exécution. Le manifeste porte `run.status="completed"`; le statut d'exécution ne remplace pas les contrôles de sortie.

La revue n'est pas une preuve universelle de robustesse Python ni une analyse des objets personnalisés non JSON. Aucune borne uniforme d'erreur flottante, compatibilité physique, fidélité linguistique ou performance LLM n'est établie. Le domaine QUBO choisi exclut volontairement les coefficients flottants; les normalisations et ordres de termes admis sont ceux de ce schéma. L'égalité de sorties peut toujours masquer une différence physique sur une autre instance ou observable. Une nouvelle version du module ou un élargissement de schéma exige un nouvel audit.

Action suivante : intégrer cette preuve finie dans la provenance C05, puis employer cette frontière explicite pour de futures propositions natives d'agents, avec annotations indépendantes de leurs contrats sémantiques. Conserver séparément taux de conformité du schéma, fidélité du problème normalisé et validité matérielle.
