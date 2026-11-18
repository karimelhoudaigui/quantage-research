# C20 — pilote de développement par éditions explicites

15 novembre 2026, avant toute génération C20. Statut de ce fichier : protocole de pilote, pas résultat. Root autorise l'implémentation et décidera séparément de l'exécution locale après revue. Aucun serveur, GPU ou modèle n'est lancé par l'auteur de ce code.

## Question et sélection de développement

Après C19, plusieurs révisions guidées reproduisent une initiale erronée. Le pilote examine si demander un diagnostic court puis des éditions explicites produit une modification justifiée, plutôt qu'une simple recopie du modèle. Cette motivation et le choix du format sont postérieurs aux résultats C19 : aucune évaluation confirmatoire ni nouveauté n'en découle.

Deux anciens cas de TEST C19 deviennent explicitement DÉVELOPPEMENT C20 : `29507bb778cc` (FR, n=6) et `417127d82203` (EN, n=4), les deux premiers ID triés parmi les sept initiales C19 infidèles. Le premier omet une implication; le second inverse une implication et invente des exclusions. Les deux objets publics sont copiés à l'identique dans probe_cases.json. Aucun nouveau corpus test n'est construit et aucune variante numérique n'est sélectionnée selon des générations C20.

L'initiale est réutilisée littéralement depuis `runs/20261115-c19-instruct-repair/test-initial-v2/driver/raw.jsonl`. Elle n'est jamais régénérée. Ses consignes d'origine sont authentifiées via `--initial-instructions runs/20261115-c19-instruct-repair/instructions.frozen.txt`. Les nouvelles consignes instructions.txt ne contiennent ni label, ni modèle corrigé, ni correction propre à ces cas. Les feedbacks minimaux existants sont lus séparément pour la phase guidée; aucun gold n'entre dans le driver. L'auteur a connaissance des résultats C19 : ce pilote n'est pas aveugle.

## Intervention générique

La sortie LLM est `{diagnosis,edits}`. Le diagnostic contient au plus 256 caractères ASCII imprimables, n'est pas interprété et ne constitue pas un certificat. Au plus 32 opérations sont autorisées : add_constraint(row), replace_constraint(index,row), delete_constraint(index), set_objective(values), set_variables(values), replace_model(model complet cinq champs). La grammaire est identique pour toutes les requêtes; elle ne lit ni données ni référence. Ses indices, constantes et bornes sont génériques comme C19.

L'appliqueur reçoit seulement le texte initial, le texte patch et n. Il décode le modèle LLM initial, applique dans l'ordre les éditions littérales, puis normalise les chaînes linéaires avec le compilateur existant. Les indices désignent la liste courante, après les opérations précédentes. Aucun coefficient, clause ou objectif n'est complété depuis les données. Une opération invalide rejette atomiquement le patch entier; pas de résultat partiellement appliqué ni de fallback canonique. Un patch vide conserve le modèle initial. Un texte initial inutilisable exige un replace_model explicite avant toute autre opération. L'objectif reste éditable et les régressions restent possibles.

Le driver est une copie séparée de repair_llama_linear.py, dont la source reste immuable. Seules les phases self/guided sont admises. Le contexte et les paramètres d'inférence ne changent pas : Qwen3-4B-Instruct-2507 Q4_K_M et acquisition C19 épinglée, llama.cpp b12359, Metal MTL0 et quatre threads CPU, contexte4096, maximum512 nouveaux tokens, T0.7/top-p0.8/top-k20, seed SHA(ID)+1. Les probabilités de tokens sont des scores API traités, pas des vraisemblances globales conditionnelles. Métadonnées et traces distinguent patch, diagnostic, modèle matérialisé et initiale réutilisée.

## Exécution ultérieure autorisée par root

Plan de capacité borné : **deux nouveaux appels guidés au total**, un par probe, aucun retry d'un appel commencé. Le pilote ne présuppose pas leur succès. Une auto-révision est prise en charge pour un éventuel contrôle ultérieur, mais ne fait pas partie de ces deux appels. Un seul serveur GPU à la fois; destinations neuves, refus d'écrasement, 180s par complétion, 1650s internes et watchdog externe1800s, réserve disque3GiB avant démarrage et1GiB avant appel. Stop sur erreur ou ressource insuffisante, conserver absents et partiels, aucune imputation.

Exemple d'argv pour root, à envelopper dans son runner et à exécuter seulement après revue :

~~~text
python3 -B -m quantage.repair_patch_inference --cases runs/20261115-c20-grounded-edits/probe_cases.json --instructions runs/20261115-c20-grounded-edits/instructions.txt --initial-instructions runs/20261115-c19-instruct-repair/instructions.frozen.txt --initial runs/20261115-c19-instruct-repair/test-initial-v2/driver/raw.jsonl --feedback runs/20261115-c19-instruct-repair/test-feedback-v2/minimal.json --phase guided --output runs/20261115-c20-grounded-edits/probe-guided-v1/driver --server-binary research/external/c16-public/runtime/llama-b12359/llama-server --model research/external/c19-public/models/Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf --acquisition runs/20261115-c19-instruct-repair/acquisition.json --execute
~~~

Root créera le runner/manifeste et gèlera les entrées avant ces appels; ces sorties ne sont pas créées par le présent lot d'implémentation. Le scorer C19 original attend une réponse fullmodel et ne doit pas être appliqué directement au texte patch. Toute évaluation doit rejouer parse_patch(raw,n,initial_raw), conserver les erreurs sans fallback, puis contrôler le modèle matérialisé avec l'oracle séparé et comptabiliser ce nouveau post-traitement.

## Mesures, coûts et limites

Rapporter chaque diagnostic et opération, validité du patch, changement littéral ou patch vide, fidélité finale exacte, faisabilité/objectifs, contre-exemples résiduels, régression éventuelle et coûts. Une édition peut être syntaxiquement correcte mais injustifiée. Le diagnostic n'est ni preuve de raisonnement ni résultat validé. Pas d'agrégat de généralisation sur n=2 choisis après observation.

Les 512 tokens incluent diagnostic et edits; la représentation et le prompt changent par rapport à la révision complète C19. Leur plafond égal n'implique pas effort, longueur ou coût égal et ne sépare pas causalement le diagnostic du patch. Les initiales historiques et leurs coûts sont référencés, jamais prétendus gratuits dans un système déployé; distinguer coût physique marginal C20 et coût attribuable initial+révision. Compter chargements, appels, post-traitement, vérification et éventuels solveurs; signaler CPU parent/housekeeping, énergie, annotation et coût session non mesurés. Aucun avantage quantique, run QPU, dépense externe ou publication.

Une future évaluation avec au moins trois implications par cas est seulement proposée; le corpus, le protocole et les seuils ne sont pas encore définis. Les anciens C19 comportaient au plus deux implications. Les probes C20 et leurs sorties seront du développement, sans réemploi comme test réservé. Aucun article, state, claims ou fichier C19 n'est modifié par ce lot.
