# C05 — audit indépendant du moteur C01 figé

Question : `verify(problem, model)` est-il une frontière sûre pour des propositions externes, et que certifie exactement son résultat ? Verdict borné : **contre-exemples trouvés à la validation générale des propositions externes**. Le calcul canonique MIS est justifié par un argument uniforme; les contrôles optiques et les huit exemples manuels concordent. Les acceptations malformées ci-dessous ne réfutent pas l'égalité des ensembles d'optima ou des probabilités calculées sur les seules instances C01–C04.

Audit confié à un agent distinct de l'auteur, sans contexte de rédaction hérité. Les lectures obligatoires comprennent les verdicts de l'auteur : la revue n'est donc pas aveugle. Les mathématiques et contre-exemples sont reconstruits depuis le code; aucune indépendance de modèle n'est garantie. La nouvelle frontière C05 n'est pas auditée dans ce rapport.

## Périmètre et provenance

Lecture de `AGENTS.md`, `README.md`, `research/state.md`, `backlog.json`, `claims.json`, `config/policy.json`, `agents/orchestrator.md`, `agents/verifier.md`, des protocoles et résumés récents, de `test_core.py`, du générateur C02 et du CLI. Les verdicts antérieurs ne sont pas utilisés comme preuve.

Exécution locale Python 3.9.6, `macOS-26.2-arm64-arm-64bit`, bibliothèque standard, commit `fee83eb4575198e3e142d41c621300b4d11361d8`, arbre modifié. Aucun appel réseau, QPU, SDK quantique, Codex imbriqué, secret ni dépense. Seuls ce rapport et `audit_cases.json` sont créés par l'auditeur. Aucun ancien fichier hashé n'est modifié.

Empreintes SHA-256 observées avant et après le run, identiques :

| Fichier audité | SHA-256 |
| --- | --- |
| `quantage/core.py` | `35001246743a201d2326a53a586fd50bedca48d8e322f52124f2a3e0c7403be2` |
| `quantage/verification.py` | `c7d070281763bb46ad6244ef1c0bc4734c159bc32d5adca1dfac6e9786f6426f` |

L'artefact `audit_cases.json` conserve 73 cas déterministes sélectionnés, avec requêtes, modifications du problème ou modèle, tolérance, propositions effectivement exécutées, certificats, solutions et exceptions. Le maximum MIS est trois sommets. Les non-finis sont encodés par `{"$float":"nan"}`, `"inf"` ou `"-inf"`, puis décodés explicitement. Les autres cas sont du JSON strict. Le protocole C05 autorise cet audit local; les cas sont des tests adversariaux de développement, pas un échantillon de sorties LLM.

Le même fichier porte la commande, l'environnement, les empreintes avant/après, le code de replay et les sorties brutes intégrées, au format local d'audit. Il ne constitue pas à lui seul un manifeste v2 autonome; la provenance du cycle doit également le référencer par empreinte. Les empreintes internes suivantes utilisent SHA-256 sur `json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()` pour les tableaux, et UTF-8 pour le code :

| Donnée intégrée | SHA-256 |
| --- | --- |
| `cases` | `0ca0d2918edeab20e89532e14c9ed841a7c41448e13f9e1d806d18fffd9adbf9` |
| `recorded_run.results` | `a8f95ea5e007b8ef67864bea1ceea34b67fec3dbc49a317bc594ff92443f3b5c` |
| `replay_source` | `8f008a79363e48d1a97c350dd31d3bf8b931e36aeb36beb1a49670e423da9c25` |

## Reconstruction des garanties

Pour un graphe simple et des poids entiers strictement positifs, le générateur construit l'énergie `-sum(w_i*x_i) + P*sum(x_i*x_j)`, avec `P=max(w)+1`. Toute sélection infaisable possède un sommet sélectionné incident à au moins une arête sélectionnée. Retirer ce sommet change l'énergie de `w_i-P*k<0`, où `k>=1` est son nombre de voisins sélectionnés. Aucun minimiseur n'est donc infaisable. Sur les ensembles indépendants, minimiser l'énergie revient exactement à maximiser le poids. `bitstrings(n)` visite les `2**n` états; les entiers Python préservent l'arithmétique exacte pour les modèles générés. L'oracle par sous-ensembles contrôle toutes les solutions optimales, y compris les ex aequo.

En optique, les conventions du code donnent, depuis le mode d'entrée zéro, les amplitudes `cos(b)*cos(a)-sin(b)*sin(a)*exp(i*phi)` et `sin(b)*cos(a)+cos(b)*sin(a)*exp(i*phi)`. Leur module carré donne exactement l'expression de l'oracle en arithmétique réelle. Les rotations et la phase conservent la norme. L'implémentation reste en virgule flottante : la tolérance `1e-12` est un critère numérique, sans borne uniforme démontrée ici sur tous les angles finis.

Le certificat MIS vérifie uniquement l'égalité de l'ensemble des optimiseurs de l'instance, sans comparer l'énergie, les coefficients ou la validité d'un champ ignoré. Le certificat optique vérifie deux probabilités finies, leur domaine, leur somme et leur écart avec l'oracle de cette instance. Une phase globale, un décalage d'énergie, une échelle positive, l'échange des deux rotations dans ce modèle à deux modes ou le signe de la phase peuvent conserver les sorties. Leur acceptation ne constitue pas en elle-même une erreur. Le certificat n'atteste ni toutes les amplitudes complexes, ni une équivalence physique complète, ni le texte initial, ni l'accès matériel.

## Contre-exemples exécutés

Référence MIS : deux sommets reliés, poids `[1,2]`, optimum unique `[0,1]`. Référence optique : angles `(a,b,phi)=(0.2,0.3,0.4)`, sortie `[0.7788297915597203,0.22117020844027974]`.

| Cas brut | Résultat observé | Cause et portée |
| --- | --- | --- |
| `mis_unknown_sense` : linéaires `[1,2]`, interaction `[[0,1,-3]]`, sens `"banana"` | `valid=true`, énergie `2`, solution `[0,1]` | `solve_qubo`, ligne 88, maximise pour toute valeur différente de `"minimize"`. Le sens inconnu devient une convention silencieuse. |
| `mis_negative_index`, `mis_bool_index` : interaction `[[0,-1,3]]` ou `[[0,true,3]]` | `valid=true`, énergie `-2`, solution `[0,1]` | Les indices suivent les conventions Python; `-1` référence le dernier bit et `True` le bit un. Les indices hors portée et flottants testés sont rejetés par exception. |
| `mis_extra_semantics` : champ supplémentaire `extra_constraint="select vertex 0"` | `valid=true`, solution `[0,1]` | Le champ est ignoré. Il ne devient jamais une contrainte, même si sa lecture humaine contredit la solution. |
| `mis_penalty_nan`, `mis_penalty_inf`, `mis_penalty_-inf`, `mis_unused_penalty` | `valid=true` | La métadonnée `penalty` n'intervient pas dans l'énergie; aucun type ou domaine n'est contrôlé. |
| `photon_unknown_order`, `photon_unknown_output`, `photon_string_coherent` | `valid=true`, erreur `0` | Tout ordre autre que le seul cas inversé suit l'ordre par défaut; tout output autre que `real_amplitudes` devient des probabilités; la chaîne `"false"` est vraie en Python. |
| `photon_negative_phase_index`, `photon_bool_phase_index`, `photon_bool_input_mode` | `valid=true`, erreur `0` | Les indices négatifs et booléens sont acceptés selon la sémantique Python. |
| `photon_unknown_input_on_balanced` : entrée `666`, avec `a=pi/4,b=0` | `valid=true`, écart `2.220446049250313e-16` | Toute entrée autre que zéro devient le mode un. Les deux distributions sont ici équilibrées, masquant le champ inconnu. Le même champ est rejeté numériquement pour les angles génériques. |
| `photon_coherent_nan`, `photon_coherent_inf`, `photon_coherent_-inf` | `valid=true`, erreur `0` | Ces flottants non finis sont utilisés comme valeurs vraies, sans validation de type booléen. |
| `photon_unknown_normalized_family` | `valid=true` | Toute famille autre que `mis` entre dans la branche optique si les champs nécessaires sont présents. Le vérificateur suppose le problème déjà normalisé. |
| `mis_finite_inputs_infinite_energy` : un sommet de poids un, constante et linéaire `1e308`, sens `maximize` | `valid=true`, solution `[1]`, énergie `Infinity` | Les seules solutions sont comparées; aucune énergie finie n'est exigée. L'optimum sélectionné reste correct sur cette instance. La sérialisation JSON stricte de la solution échouerait. |
| `photon_changed_angle_tolerance_{'$float': 'inf'}` : modèle `a=1.1` au lieu de `0.2`, tolérance infinie | `valid=true`, écart `0.7319226834603982` | Le paramètre d'appel n'est pas validé; tous les seuils deviennent infinis. À tolérance par défaut, ce cas est rejeté. Ce n'est pas un champ de proposition. |

Sur les cas sélectionnés, NaN et les deux infinis dans les coefficients MIS opérants sont rejetés; les valeurs non finies dans `a`, `b`, `phi` et `global_phase` sont également rejetées. Il ne faut donc pas résumer ces résultats par « tous les NaN passent ». Les `kind` inconnus testés sont rejetés dans les deux familles. Les tolérances NaN et négative testées sont rejetées par les comparaisons; leur domaine n'est pas contrôlé explicitement.

La frontière stricte du **pipeline existant** appelle `understand`, puis son propre `formulate`; elle n'accepte pas de modèle externe. Les six requêtes malformées testées à cette frontière donnent toutes `abstain`. Les contre-exemples concernent une utilisation directe de `verify` pour des propositions externes et ne prouvent pas une faille d'injection de modèle dans le CLI existant.

## Commandes et contrôles

Depuis la racine du dépôt :

```bash
python3 -m unittest discover -s tests -p test_core.py -v
python3 -c 'import json; from pathlib import Path; exec(json.loads(Path("runs/20261113-c05-semantic-contracts/audit_cases.json").read_text())["replay_source"])'
```

Les cinq tests existants passent. Le replay des 73 cas est identique au résultat enregistré après exclusion du seul temps d'exécution (`0.0019980420000000054` seconde pour le premier enregistrement du moteur de cas). Les huit contrôles à résultat calculable à la main passent : MIS K2 pondéré, K2 avec ex aequo et étoile pondérée; optique identité, échange de mode et trois phases de l'interféromètre équilibré. L'écart maximal des probabilités avec les cibles manuelles est `1.1102230246251565e-16`. Ces nombres ne constituent ni un taux populationnel, ni une réévaluation exhaustive des chiffres C01–C04.

Le run est `completed` : le programme d'audit s'est terminé et a trouvé les contre-exemples annoncés; cela ne signifie pas que le vérificateur externe est validé. Les sources de replay et les cas sont intégrés au même document que les sorties; les trois empreintes internes ci-dessus permettent de contrôler leur contenu sans empreinte récursive du document lui-même.

Action suivante : imposer un schéma explicite avant toute exécution de proposition externe, valider problème et tolérance, conserver les transformations admissibles et rejouer ces mêmes cas contre la nouvelle frontière. Faire relire séparément cette nouvelle implémentation. Les appels de modèle, la fidélité linguistique, les bornes uniformes d'erreur flottante, les performances physiques et l'avantage quantique restent hors de cet audit.
