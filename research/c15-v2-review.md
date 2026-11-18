# C15 — audit indépendant du frontend, du contrôleur et du scorer v2

## Verdict et portée

Après l'annonce `FROZEN`, les contrôles indépendants ont été exécutés avec
empreintes avant/après. Aucun défaut bloquant n'a été trouvé pour la matrice
comparative préenregistrée sur les 16 cas réservés. Cela autorise un
verdict sur le logiciel dans les contrôles indiqués, **aucun résultat H15**.
Le relecteur n'a exécuté aucun LLM ni lu/scoré ses réponses réservées pour ce
rapport. Les limites des traces externes sont conservées ci-dessous.

Les sources exactes sont archivées dans
`research/c15-v2-source-snapshot/quantage/`. Leur SHA-256, la date de gel et
les manifestes sont dans `research/c15-v2-review-freeze.json`. Sont concernés
`repair_model.py`, `repair_feedback.py`, `repair_solvers.py`,
`repair_language.py`, `repair_loop.py`, `repair_inference_v2.py` et
`repair_study_v2.py`. Les rapports et manifestes antérieurs ne sont pas
réécrits. Les instructions v2 et l'amendement de représentation ont été lus.

## Analyse statique de l'algèbre et de la conservation

Le compilateur reçoit seulement la proposition et le nombre de variables.
Il ne lit aucun texte d'intention, poids/coût public ou contrat annoté pour
compléter une ligne. L'objectif et la liste de variables restent fournis
explicitement par l'agent. Chaque ligne est réarrangée en
`(a_left-a_right)*x relation (c_right-c_left)`, avec la même relation.
L'arithmétique est entière et exacte.

La liste des formes autorisées se limite aux entiers, variables déclarées,
addition/soustraction, signes unaires et multiplication quand au moins un
côté est syntaxiquement dépourvu de variable. Les alias `x0`, `x_0` et
`x[0]` se rapportent au même indice borné. Il n'y a ni `eval`, ni `exec`, ni
appel de fonction ou d'attribut dans le compilateur. Les produits qui
pourraient se simplifier en zéro mais contiennent des variables des deux
côtés sont refusés conservativement : l'audit ne leur attribue aucune
acceptation par simplification implicite.

Les bornes sont 4096 caractères par ligne, 256 nœuds AST, profondeur de
descente 64 et intermédiaires entiers de 512 bits. Les bornes finales et le
schéma dense restent ceux du cœur figé : au plus 32 lignes et valeurs
absolues au plus 10000. Les constantes présentes des deux côtés sont
déplacées exactement ; aucune pénalité, clause ou borne manquante n'est
ajoutée. `authored_model` conserve la structure soumise, même lorsqu'une
compilation algébrique échoue. Les propositions denses historiques valides
gardent exactement le résultat du parseur v1.

## Contrôles exécutés sur les expressions et domaines

`research/c15-language-loop-audit.py` a construit 375 comparaisons affines
à partir de coefficients fixés indépendamment. Les résultats de compilation
ont été comparés aux coefficients attendus, puis à 10 125 évaluations
entières directes sur une grille comportant aussi des valeurs non binaires.
Sept expressions calculables à la main couvrent les signes, constantes des
deux côtés, multiplication par constante, alias et notations de relations.
Trente-huit expressions interdites sont rejetées, dont appels, attributs,
indices calculés, booléens/flottants/complexes, produits non linéaires,
division/puissances, comparaisons chaînées et dépassements de ressources.

Les contrôles vérifient également le refus des valeurs finales hors borne,
la conservation exacte des champs et lignes mixtes chaîne/dense et quatre
résultats historiques inchangés. Les 24 modèles de référence **construits
pour l'audit seulement depuis le gold de revue figé** ont ensuite été écrits
en chaînes, compilés et comparés aux domaines indépendants déjà énumérés.
Les 24 cubes et tous leurs domaines restent identiques. Ces modèles
d'audit n'ont jamais été transmis à l'inférence.

Provenance : `research/c15-language-loop-audit.contract.json` et
`research/c15-language-loop-audit/{raw.json,manifest.json}`, statut
`completed`, validation avec racine passée. Python 3.9.6, SciPy 1.13.1,
NumPy 1.26.4 ; limite 30 s, thread conventionnel 1, sans aléa. Commande
enfant :

```bash
python3 research/c15-language-loop-audit.py --output research/c15-language-loop-audit
```

Le contrat, la commande complète du runner et toutes les empreintes sont
dans le manifest. Un replay exige une nouvelle destination.

## Contrôleur réutilisable et séparation du protocole

Le contrôleur filtre le public en `{id,intention,data}` et ne transmet ni
gold ni métadonnées incidentes au générateur. Le sous-processus d'inférence
est une commande fixe ; le texte proposé n'est jamais exécuté. Le feedback
vient exclusivement du helper fermé, et le modèle dense final seul va au
portfolio. La limite globale est vérifiée autour des générations et de la
vérification ; les sous-processus ont un timeout égal au temps restant.

Une séquence logicielle injectée, explicitement étiquetée
`injected_software_fixture`, a produit un modèle faux puis un modèle fidèle.
Le contrôleur a transmis des témoins réels, arrêté après deux appels et
retrouvé l'optimum exact attendu par les deux solveurs. Aucun LLM n'est
simulé dans les résultats scientifiques : ce sont uniquement des contrôles
de branchements et de flux de données.

La boucle réutilisable arrête dès qu'un certificat est obtenu et admet
jusqu'à trois réparations. Elle est donc distincte de l'expérience comparative
qui exécute une seconde proposition dans tous les bras, même après une
initiale fidèle, afin de mesurer les régressions. La démonstration CLI
éventuelle sur développement ne doit pas être mélangée aux comptes H15.

Limite caractérisée : la validation d'une trace initiale réutilisée contrôle
la requête et les instructions mais accepte encore une trace marquée
`guided`, avec contexte additionnel et 385 tokens. Ce cas artificiel a été
reproduit et est enregistré dans le brut. Il n'est pas une trace réelle.
Pour la démonstration prévue, l'intégrateur doit contrôler séparément phase
initiale, deux messages et caps réels ; un durcissement futur de cette API
doit être versionné. Aucune authentification fournisseur n'est établie par
la seule lecture d'un fichier JSONL.

## Scorer v2, budgets, feedbacks et coûts

Le scorer v2 utilise le même frontend que les quatre phases. Les règles
de sélection sont identiques au prototype vérifié : direct par schéma puis
moyenne log-probabilité après température/top-k, égalité à la première ; auto
et guidée par seconde valide sinon première valide. Aucun gold ne choisit
une proposition ou un solveur. Les strates faisables/infaisables utilisent
le domaine de référence, même si le modèle initial n'est pas parsable.

Les vérifications supplémentaires contrôlent phase, 384 nouveaux tokens,
contexte jusqu'à 4096, nombres d'IDs et scores, moyenne des scores,
terminaison, requête publique, absence de contexte supplémentaire dans les
générations indépendantes et parse sauvegardée. Les doublons de gold sont
refusés et les métadonnées de familles sont dérivées/validées depuis le
contrat plutôt que supposées présentes.

Un second audit à quatre cas artificiels vérifie les sélections, réparation
de format/mathématique, régression, strates, distinction de l'équivalence
d'optima, H15 non soutenue dans ces fixtures, mode initial seul et séparation
du coût physique et attribué. Onze variantes de traces corrompues sont
refusées. Les métadonnées de chargement/processus/wrapper, le coût du feedback
et le total des portfolios sont aussi contrôlés. Les valeurs de tokens et
temps de ces fixtures sont artificielles, fixées pour le test de comptabilité,
et ne sont aucune mesure de performance LLM.

Provenance séparée : `research/c15-study-audit-v2.py`, son contrat et
`research/c15-study-audit-v2/{raw.json,manifest.json}`, statut `completed`,
validation avec racine passée. Même environnement et limite que ci-dessus.
Commande enfant :

```bash
python3 research/c15-study-audit-v2.py --output research/c15-study-audit-v2
```

Limite caractérisée du lecteur de traces : un `mean_generated_log_probability`
NaN est encore accepté quand les scores individuels sont finis, car la
comparaison `abs(moyenne-NaN)>tolérance` est fausse. L'exporteur d'inférence
calcule la moyenne depuis des scores finis et sérialise avec
`allow_nan=False`, ce qui exclut cette valeur des générations prévues.
L'audit indépendant des bruts devra néanmoins exiger explicitement sa
finitude et son égalité aux scores individuels. Cette limite sur fichier
corrompu ne constitue pas une observation de NaN dans une génération v2.

Les sommes de lignes restent des temps de requêtes avec post-traitement ;
les temps de chargement/processus/wrapper sont désormais rapportés à part.
Il faut éviter de les additionner sans tenir compte de leurs inclusions.
Les portfolios exécutent les deux solveurs avant de choisir après coup :
aucun gain d'un routage préalable n'est établi. Coût d'annotation, énergie,
développement et coût complet de session restent distincts ou inconnus.

## Obligations après exécution

Auditer les quatre matrices complètes, tokens/terminaisons/seeds, égalité des
instructions et des requêtes, contextes self/guided, feedback minimal exact,
sélections sans gold, certificats par tables indépendantes, strates et
comptabilité. Les résultats partiels ne seront pas imputés. Tout résultat
H15 devra provenir des bruts réservés ; le présent rapport valide des
contrôles de logiciel et de mathématique finie uniquement.
