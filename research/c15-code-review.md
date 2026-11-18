# C15 — revue indépendante du code avant inférence

## Périmètre et statut

Relus : `quantage/repair_model.py`, `quantage/repair_inference.py`,
`quantage/repair_solvers.py`, protocole C15 et `instructions.v1.txt`. Les
annotations du relecteur étaient déjà figées. Aucun gold auteur, générateur
de corpus ni fichier `corpus-provenance.md` lu. Aucun LLM exécuté par cette
revue. Aucun fichier de production, manuscrit, claim ou état modifié.

Le format typé, la sémantique finie F/f, les témoins et les solveurs sont
cohérents avec le protocole dans le domaine contrôlé. Des points de
traçabilité de l'inférence sont à traiter ci-dessous avant de figer celle-ci.
La sélection finale des bras et les scores ne sont pas encore disponibles
dans les fichiers soumis à cette revue ; ils restent à auditer.

## Vérifications et résultats finis

Une implémentation indépendante dans `research/c15-code-audit.py` reconstruit
des ILP **pour l'audit seulement**, à partir des annotations de revue, sans
les transmettre à l'inférence. Ses domaines sont comparés aux domaines déjà
calculés par l'oracle distinct à base d'ensembles. Les deux représentations
coïncident sur les 24 cas.

Puis 234 variantes explicites sont contrôlées : modèles fidèles, suppression
de chaque ligne, objectif erroné, objectif multiplié par deux, ligne nulle
redondante. Les nombres de désaccords de faisabilité et de valeur d'objectif
du vérificateur de production coïncident avec les tables indépendantes sur
chaque cube. Les trois premiers témoins lexicographiques, avec priorité
faisabilité par affectation, sont également identiques. Les 240 propositions
de schéma invalides sont rejetées, incluant booléens, flottants, coefficients
hors borne, arité, ordre de variables, relation non supportée, clé ajoutée,
clé JSON dupliquée, NaN et prose après JSON.

Les 24 ILP d'audit sont réellement résolues par DFS et HiGHS, puis de nouveau
via le portfolio, soit 96 appels solveurs. Statuts, valeurs et solutions
correspondent à l'oracle de revue. Tous les optima DFS sont comparés ; une
solution HiGHS différente mais optimale est admise. Trois cas sont
infaisables, sans optimum inventé. Le choix de solveur est le minimum des
temps effectivement enregistrés, et le coût total contient les deux appels.
Ces timings de contrôles ne sont pas des résultats de performance d'agent.

Provenance : `research/c15-code-audit.contract.json`,
`research/c15-code-audit/manifest.json` et
`research/c15-code-audit/raw.json`. Le manifest v2 a le statut `completed` et
sa validation avec racine passe. Les entrées ont été hashées avant/après ;
Python 3.9.6, SciPy 1.13.1 et NumPy 1.26.4 ont été interrogés localement.
Exécution bornée à 30 s et thread conventionnel 1, sans aléa. Commande exacte
dans le manifest, commençant par
`python3 research/c15-code-audit.py --output research/c15-code-audit/raw.json`.
Tout replay exige une destination neuve.

## Examen mathématique

`verify_model` parcourt réellement tous les éléments de `{0,1}^n` : même
faisabilité **et** mêmes valeurs d'objectif, y compris hors domaine faisable.
Avec des objectifs linéaires sans constante, l'égalité sur tout le cube
impose notamment l'égalité de chaque coefficient par les vecteurs unités.
Une multiplication positive de l'objectif est donc rejetée même si elle
conserve les optima. Les opérations sont entières ; aucun seuil flottant
n'intervient dans ces comparaisons.

Le test est extensionnel sur une instance, comme l'annonce le protocole.
Dans cet audit, 28 suppressions de lignes restent fidèles : contraintes
redondantes, inactives, ou contradiction encore suffisante pour rendre tout
le domaine vide. Cela ne prouve pas que les clauses sont structurellement
bien traduites ni que le modèle sera correct sous d'autres données. Pour
une instance infaisable, tout autre système de contraintes également vide
avec le bon objectif peut passer. La séparation des scores faisables et
infaisables est donc nécessaire.

Le vérificateur n'est pas une certification du texte libre ; la référence
structurée est une annotation externe. La borne du parseur est `n<=8`,
celle des solveurs `n<=7`, alors que le protocole et le corpus se limitent
bien à 4–7. Cette différence ne touche pas les présents cas et doit rester
explicite si l'API est réutilisée.

## Retour au modèle et confidentialité

La sortie `verify_model(...)[feedback]` contient une erreur de schéma à
message fixe, ou trois affectations au plus avec booléens/valeurs, ou
`no_counterexample`. Elle ne contient aucun nom de clause, coefficient de
référence, budget, ensemble d'obligations ou modèle réparé. Les totaux et
comptes détaillés du vérificateur sont dans l'enveloppe externe et ne doivent
jamais être transmis comme feedback. Les valeurs d'objectif attendues
révèlent un scalaire évalué, ce qui est autorisé par le protocole.

L'inférence lit explicitement le public, les instructions, les observations
initiales si demandées, un feedback guidé si demandé, l'acquisition C07 et
les fichiers du checkpoint. Aucun chemin de gold n'est codé dans ce module.
Les générations sont locales, `local_files_only=True`, sans code distant,
Safetensors, mode hors ligne et token implicite désactivé. Les propositions
ne sont jamais exécutées. Il s'agit d'une séparation des entrées par code,
pas d'une interdiction OS de lire le reste du workspace. Les arguments et
artefacts effectivement utilisés devront être vérifiés dans les manifestes.

**À durcir avant test :** dans la version relue,
`feedback[case['id']]` est sérialisé directement dans le prompt sans schéma
intermédiaire. Le producteur actuel fournit un objet minimal, mais la
frontière d'inférence n'empêche pas un mauvais fichier d'y ajouter un modèle,
des paramètres ou des comptes. Recommandation : valider exactement les trois
variantes admises et leurs champs, types, tailles et vecteurs binaires avant
de créer les messages. Vérifier les prompts enregistrés après génération.

## Probabilités et sélection directe

`model.generate` utilise sampling, température 0.2, top-k 50 et top-p 1.
`log_softmax(generated.scores[t])` calcule la probabilité du token choisi
**après** les processeurs/warpers appliqués pendant la génération. La moyenne
inclut EOS, quand EOS termine la réponse, bien que le décodage masque les
tokens spéciaux. Le champ `log_probability_scope` décrit correctement cette
distribution de génération, distincte de la log-vraisemblance brute du
modèle, d'une probabilité de justesse ou d'une calibration. Les scores des
tokens choisis sont contrôlés finis.

La version relue ne conserve que la moyenne. Recommandation de traçabilité :
conserver aussi les IDs des tokens générés et leurs log-probabilités, déjà
calculées, afin de vérifier compte, moyenne et EOS sans réinférence. La
règle future best-of-two doit être auditée séparément : schéma d'abord,
moyenne ensuite, égalité à la première, aucun certificat ni label.

La phase `direct` ne place jamais la première réponse dans les messages,
mais charge actuellement le fichier des observations initiales et exige sa
complétude. Pour éviter une formulation trop forte dans le protocole, écrire
« le modèle ne voit pas la première réponse dans son prompt », ou supprimer
cette lecture pour la génération directe. Auto et guidée partagent la seed
de seconde phase ; la génération initiale a une seed distincte. Aucun retry
interne n'est implémenté.

## Limites et suite

La limite interne de 1650 s est vérifiée entre les requêtes ; le runner
externe doit imposer la limite dure de phase. Un échec durant un appel
laisse une matrice partielle ; il faut conserver les absents sans les
imputer. Les éventuels échecs précédant le `try` d'inférence peuvent ne pas
avoir de `generation.json`, et doivent rester observables par le runner.

Revue avant test terminée pour les fichiers présents. Restent : vérification
des éventuels changements du module d'inférence ; scorer et règles de
sélection ; feedbacks effectifs ; audit indépendant des sorties, métriques
et coûts. Aucun gain de réparation, taux de fidélité LLM ou résultat H15
n'est établi par ces contrôles.

## Complément après corrections de l'intégrateur, toujours avant test

Les trois changements suivants ont ensuite été relus : `direct` refuse
`--initial` et ne charge donc plus la première réponse ; les identifiants de
tokens et log-probabilités sont conservés ; `validate_feedback` impose les
champs exacts, les tailles, les types binaires et des points distincts pour
les témoins. Les objets `no_counterexample` sont fixés à un message constant.
Ces changements répondent aux observations correspondantes ci-dessus.
Réserve résiduelle : `schema.detail` reste une chaîne arbitraire de longueur
au plus 400, donc la forme seule n'exclut pas des coefficients ou noms de
clauses à l'intérieur. Le producteur actuel donne des messages de parseur
génériques ; un code d'erreur normalisé dans le prompt serait une frontière
plus stricte, tout en conservant le détail complet hors prompt.

Les nouveaux champs `optimizer_set_equal` et
`finite_optimization_equivalent` ont été vérifiés par comparaison aux
ensembles d'optima de tables indépendantes, dans les 234 variantes. Les
feedbacks produits passent leur nouveau validateur ; huit objets de feedback
mal formés sont rejetés. Le nouveau calcul est conservé séparément dans
`research/c15-code-audit-v2/{raw.json,manifest.json}`, statut `completed`,
validation avec racine passée. Les 24 cas, 240 invalides de parseur et 96
appels solveurs sont de nouveau contrôlés. Ce replay est justifié par les
changements de code ; le premier répertoire conserve les empreintes de sa
version historique et ne doit pas être pris pour une validation des sources
modifiées ultérieurement.

La réparation du manuscrit a aussi été relue indépendamment sans écriture
dans `paper/` : `research/c15-manuscript-recheck.json` conserve les empreintes
des sources réparées et les assertions. Les cinq displays Markdown sont
identiques aux cinq corps TeX ; les commandes attendues et `d_i\geq1` sont
présentes, aucun contrôle C0 non autorisé ni `\$\$` littéral ne subsiste.
Trois sondes de caractères de contrôle (U+000C, U+000D, U+000B) sont rejetées
par `latex()`. Cela vérifie les sources et la conversion ; aucun PDF compilé
n'est produit ni déclaré validé.

## Gel final v3 avant génération de test

Le cœur `repair_model.py` a été restauré exactement à son SHA-256 du premier
audit, `e022473093267ca7d32fa52bd21a75618fc4cec3888479d655ef4cbcec5a0745`.
Les diagnostics d'optima et la validation du feedback sont maintenant dans
`repair_feedback.py`. `feedback_for_model` remplace systématiquement toute
erreur de schéma par un message fixe, sans transmettre le détail. Le
validateur guidé n'admet pour ce cas que `{kind,message}` et ce message
constant. La réserve sur `schema.detail` est donc levée dans la version
finalement relue.

Le calcul v3 utilise un nouveau script distinct
`research/c15-code-audit-v3.py` et un nouveau contrat. Ses résultats et
manifest sont dans `research/c15-code-audit-v3/`, statut `completed`,
validation avec racine passée. Il contrôle les mêmes 234 variantes, 240
schémas invalides et 96 appels solveurs, les diagnostics d'optima désormais
séparés et 11 feedbacks invalides. Un faux détail contenant des paramètres
de référence est normalisé en message constant ; ses paramètres ne passent
pas dans le feedback exposé.

Les empreintes du code actuel et la date de revue avant test sont figées
dans `research/c15-code-review-freeze-v3.json`. Aucun problème bloquant ne
reste dans les quatre modules relus pour le domaine préenregistré. Le scorer,
ses règles de sélection et les résultats réels restent hors de ce verdict
avant exécution.

Les preuves historiques sont conservées sans réécriture des manifestes : le
script original `research/c15-code-audit.py` a été restauré exactement au
SHA-256 du premier audit, `6de88f9b...`, et son manifest revalide avec la
racine actuelle. Le script v2 exact est archivé dans
`research/c15-code-audit-source-v2.py`, SHA-256 `d4ef992b...`. Le manifest v2
décrit ses anciennes entrées, dont l'ancien cœur v2 ; il exige une racine
historique correspondante pour une validation de contenu, et ne certifie pas
le cœur v3 par simple réutilisation de son statut.

Les trois tests de régression du rendu mathématique ont été relus. Ils
contrôlent le rejet avant découpage, les cinq corps mathématiques conservés
et les commandes attendues jusqu'au dernier terme de l'Hamiltonien. Leur
exécution par l'intégrateur est séparée des sondes indépendantes de ce
rapport. Aucun nouvel appel LLM ou nouvel essai de quota n'est effectué ici.
