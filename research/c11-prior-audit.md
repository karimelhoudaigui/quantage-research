# Audit C01–C10 avant C11

Auteur : /root/c11_audit, 13 novembre 2026. Auteur distinct des implémentations historiques; revue avec accès à l'historique et au code, sans indépendance de modèle démontrée et sans aveuglement. Périmètre autorisé : lecture du dépôt, exécution des vérifications et écriture de ce rapport et du JSON associé. Aucun changement des preuves historiques, aucun réseau, achat, SDK, QPU ou génération LLM.

## Verdict

Les résultats finis annoncés sont cohérents avec les fichiers et les exécutions rejouées. Aucun écart de comptage ou d'intégrité détecté dans cette vérification. L'article n'est pas prêt à soumettre : contribution originale, validation plus large sur données indépendantes, baselines fortes et compatibilité SDK/matériel au niveau revendiqué restent à établir. Le protocole C11 demandé constitue une expérience justifiée.

## Ce qui a été réellement vérifié

Les 24 modules historiques de quantage/ et huit scripts ont été inspectés, ainsi que les protocoles et amendements C01–C10, agrégats, articles et registre. Les poids tiers et bibliothèques optionnelles ne sont pas audités comme code source. Le relevé des fichiers et empreintes figure dans c11-prior-audit.json; il décrit les versions observées lors de cet audit, pas les futures révisions du manuscrit.

Commandes réellement exécutées et sorties intégrales conservées dans le JSON :

- python3 scripts/check.py, avec et sans -O : succès.
- python3 -m unittest discover -s tests -v : 36 tests réussis. Les tests du runner simulent son exécuteur; ils ne lancent aucun Codex réel.
- python3 scripts/audit_results.py : réagrégation et empreintes C01–C04 conformes.
- python3 scripts/replay.py : reproduction effective de toutes les lignes et métriques C01–C04, hors elapsed_seconds.
- python3 scripts/audit_continuation.py : rejeu des 109 cas C05 et vérification des 73 lignes C05 et 32 labels/baselines C06; aucune chaîne replay_source exécutée.
- python3 scripts/audit_local_agents.py : réagrégation des scores, solutions, groupes, tokens, empreintes et résultats primaires conservés.
- Validateur v2 Mathbox sur les 12 manifestes historiques : succès avec empreintes actuelles.

Calcul orthogonal supplémentaire, sans importer les oracles historiques : les 1 199 résultats MIS C01 ont tous leurs optima confirmés par énumération de masques entiers; les 125 probabilités sont confirmées par produit matriciel 2×2 direct, erreur maximale 2.220446049250313e-16. Ce sont deux implémentations de calcul différentes, pas une validation universelle de logiciels quantiques. L'argument mathématique de pénalité stricte P>max(w) est correct dans le domaine annoncé : supprimer un sommet en conflit fait décroître Q de w_i−P d_i<0, puis Q est l'opposé du poids sur les ensembles indépendants.

## Dénominateurs contrôlés

| Étape et méthode | Supportés acceptés | Hors contrat acceptés | Risque parmi acceptations |
|---|---:|---:|---:|
| C08 sans dossier | 5/10 | 2/6 | 2/7 |
| C08 avec dossier | 4/10 | 2/6 | 2/6 |
| C09 sans veto | 7/9 | 3/7 | 3/10 |
| C09 veto fixé | 5/9 | 1/7 | 1/6 |
| C10 v3 développement | 7/9 | 1/7 | 1/8 |
| C10 v4 développement | 7/9 | 0/7 | 0/7 |

Les 48 générations primaires correspondent à 32 requêtes uniques et 16 groupes appariés. Les ensembles de données numériques C08/C09 sont également disjoints dans les fichiers observés. Cette séparation ne démontre ni indépendance statistique ni absence de contamination du pré-entraînement. C08 et C09 changent simultanément de cas et de schéma : pas d'effet causal isolé du schéma. C09 conserve son erreur résiduelle; le zéro C10 est exclusivement une régression après consultation. Aucun nouvel appel au modèle n'a été exécuté par cet auditeur; les trois replays CLI historiques ont été contrôlés comme enregistrements, pas régénérés ici.

## Faiblesses scientifiques prioritaires

1. **Validation indépendante de v4 absente.** C01–C10 sont développement pour les versions futures; le nouveau corpus doit être figé, annoté séparément et protégé pendant génération. La revue distincte C05 porte sur la frontière numérique, pas sur le nouveau veto.
2. **Formulation du LLM non évaluée dans les bras compacts.** Les modèles produisent action/tâche/raison; les coefficients sont construits par formulate. Une ablation du vérificateur numérique peut donc être nulle par construction. Il faut conserver ce bras comme compréhension hybride, et définir séparément toute expérience de formulation complète.
3. **Veto sémantique heuristique incomplet.** Un contre-exemple de contrainte de parité est exécuté ci-dessous. Il ne provient pas d'un LLM et n'est pas un résultat C11. Il doit rester développement et ne pas être utilisé pour modifier v4 pendant le nouveau test.
4. **Matériel documentaire uniquement.** Les routes conservent correctement hardware_readiness=unverified et qpu_submitted=false. C01–C10 n'établissent pas qu'un programme est accepté par Pulser/Perceval ni compatible avec un dispositif. Une expérience SDK gratuite avec oracle et cas de rejet est nécessaire avant ces revendications.
5. **Originalité et force des comparateurs.** La revue présente est sans réseau et ne conclut pas à la nouveauté. Les baselines exactes à deux phrases et mots-clés, avec un seul petit modèle, suffisent à un pilote de défaillances; elles ne démontrent pas une supériorité sur les approches proches. Une matrice primaire et des hypothèses falsifiables doivent précéder l'extension.

## Contre-exemple auditeur exécuté : contrainte omise

Demande : «Select a maximum weight independent set with an even number of vertices.» Données : trois sommets sans arête, poids [1,1,1]. Une proposition compacte propose le MIS; v4 accepte et retourne [1,1,1], poids 3, avec certificat numérique valide. Le nombre de sommets est impair; le problème demandé a un optimum de poids 2. Le certificat atteste le problème normalisé sans parité, ce qui confirme la portée limitée déjà annoncée. Le champ provenance générique du résultat ne prouve pas l'origine LLM : l'origine de ce probe est explicitement logicielle.

Reproduction locale du probe (aucune inférence) :

~~~bash
python3 - <<'PYPROBE'
import json
from quantage.compact_v2 import parse_v2
from quantage.compact_v4 import execute_v4
request = {'intent': 'Select a maximum weight independent set with an even number of vertices.',
           'data': {'n': 3, 'edges': [], 'weights': [1, 1, 1]}}
parsed = parse_v2(json.dumps({'action': 'propose', 'task': 'maximum_weight_independent_set',
                             'reason': 'Auditor software probe; no LLM generation'}))
print(json.dumps(execute_v4(request, parsed, True), indent=2))
PYPROBE
~~~

## Implications pour C11 et l'article

Figer v4 sans ajustement sur ce probe; constituer de nouveaux groupes plutôt que recycler C09. Comparer les mêmes propositions sous ablations numériques et sémantiques, en explicitant ce qui varie réellement. Annoter objectifs, contraintes, unités, entrée et observable sans utiliser le veto comme oracle. Compter les refus du contrôleur séparément des abstentions du modèle. Les taux hors contrat et risques parmi acceptations doivent garder leurs dénominateurs distincts. Quantifier l'incertitude seulement sous un schéma d'échantillonnage justifié.

Le manuscrit devrait être structuré par question, définition des contrats, architecture, hypothèses, protocole, résultats, ablations et limites; garder la chronologie détaillée dans le dépôt ou les annexes. Ses claims actuels sont prudents et leurs identifiants figurent dans les deux sources. Aucun PDF n'est compilé dans cet audit. La prochaine action est la double annotation du corpus inédit, puis la revue indépendante du scorer et des conclusions C11.
