# C15 — provenance du corpus, auteur

Document privé de conception, à ne jamais fournir au LLM évalué. `build_corpus.py`
contient aussi les annotations : seuls `dev_cases.json` et `test_cases.json` sont
des requêtes publiques. Aucun résultat de génération n'a été consulté pour les
concevoir. Date de création : 2026-11-14 ; commit Git de départ : `fee83eb4575198e3e142d41c621300b4d11361d8`.
L'arbre initial était déjà modifié ; aucun commit ni push n'est effectué ici.

Question soutenue : formuler puis réparer de véritables problèmes de sélection
pondérée, et non refuser toute extension d'un MIS. Ce corpus construit par
convenance n'est ni une distribution naturelle ni une preuve de nouveauté.

Les 24 textes ont été écrits individuellement en français ou en anglais par le
rôle d'auteur de cette session agentique, sans appel d'inférence au modèle
évalué, traduction de requêtes appariées ou lecture des corpus C11/C14. Le rôle
d'auteur a néanmoins lu les fichiers de reprise et connaît les résultats agrégés
C01–C14 et les limites de v4. Cette connaissance doit rester déclarée. Le rôle
de relecteur devra être distinct ; l'indépendance de famille de modèles ou une
annotation humaine aveugle ne sont pas établies. Aucun quota d'outil ou de
modèle n'a été rencontré par l'auteur dans cette mission.

Chaque requête définit x_i binaire, avec 1 pour la sélection de l'indice i
(indices commençant à 0), le maximum de la somme des poids sélectionnés, et les
exclusions de `edges`. Les poids et coûts sont des entiers strictement positifs,
sans unité physique revendiquée ; le budget utilise la même unité abstraite que
`costs`. Toutes les bornes sont inclusives. Une implication (i,j) signifie
x_i <= x_j et n'impose pas la réciproque. Aucune contrainte absente du texte ne
doit être ajoutée : le gold utilise null pour les trois bornes absentes, et []
pour les ensembles ou implications absents. Les paires `edges` sont non orientées.
Les textes ne promettent pas la faisabilité : une formulation infaisable demeure
une réponse correcte si elle préserve toutes les contraintes de la requête.

Développement : 8 cas, 4 FR / 4 EN, 2 par taille n=4,5,6,7. Les six familles
B (budget), L (minimum de cardinalité), U (maximum de cardinalité), M (inclusion
obligatoire), F (interdiction), I (implication) apparaissent séparément, puis
seulement deux combinaisons simples BL et UF. Tous ces cas sont faisables.
Test : 16 cas, 8 FR / 8 EN, 4 par taille, 16 signatures distinctes comportant
3 à 6 familles. Aucune signature test n'est vue au développement. Il s'agit
d'un transfert de combinaisons de clauses, pas d'un transfert de familles
mathématiques, et l'absence de signature commune n'implique pas l'indépendance
statistique. Les données et les textes des 24 requêtes sont distincts, les
identifiants opaques n'encodent ni famille ni faisabilité. Ils ne constituent
pas des traductions appariées.

Trois cas test sont volontairement infaisables : `6e3a08f5` exige 0 puis 2,
dont les coûts 5+4 dépassent 7 ; `a063c8f2` exige au moins trois éléments alors
que son obligation, ses interdictions et exclusions n'en permettent que deux ; `ce1964a7`
impose une chaîne 1 -> 3 -> 4 alors que 4 est interdit. Ils sont conservés,
sans réparation de leur intention. Le nombre de cas faisables ne sert pas
à une stratification ou une sélection après génération.

L'auto-contrôle auteur énumère les 2^n vecteurs binaires pour chaque cas, vérifie
schémas, positivité, indices, duplications de données, langues, tailles,
signatures et faisabilité prévue. Chaque graphe a entre 1 et 4 arêtes. Le contrôle
vérifie aussi que retirer chacune des familles présentes ajoute au moins une
sélection faisable, y compris pour les trois cas infaisables ; les comptes et
un témoin par famille sont privés dans `author_check.family_drop_checks`. Il
ne s'agit pas d'exiger une forme syntaxique particulière d'une formulation :
des contraintes ou lignes redondantes dans une réponse peuvent être équivalentes.
Cette qualité des instances a été ajustée avant gel et avant tout appel au modèle,
à partir des seuls ensembles faisables exacts d'auteur ; aucun filtrage selon
des résultats de LLM n'a eu lieu. Les cas faisables et infaisables doivent être
rapportés séparément lors de l'évaluation. Les optima ci-dessous sont des contrôles
exacts d'auteur, pas des performances de LLM. Une relecture indépendante doit
réextraire les clauses du texte et recalculer les ensembles faisables sans
importer ce script. Aucun vérificateur C15 futur ni sortie d'inférence n'est lu.
Sources : conception synthétique locale, sans source documentaire externe.

Commande exécutée à la racine du workspace :
`python3 runs/20261114-c15-formulation-repair/build_corpus.py`.
La génération des fichiers est déterministe, sans aléa ni seed caché. Une
réexécution identique les contrôle ; une divergence refuse de les écraser.
Les fichiers publics, le gold et le script sont figés par les empreintes
ci-dessous, avant tout appel au LLM. Le script doit rester privé même s'il est
conservé pour reproduction. Ces contrôles ne remplacent pas la revue distincte.

| ID | split | langue | n | familles privées | sélections faisables | optimum |
| --- | --- | --- | --- | --- | --- | --- |
| 9e2a4c71 | dev | fr | 4 | B | 7 | 14 |
| 31d8b6f0 | dev | en | 5 | L | 9 | 17 |
| a7f03d2c | dev | fr | 6 | U | 19 | 20 |
| 68c1e9b4 | dev | en | 7 | M | 6 | 32 |
| c2b7460d | dev | en | 4 | F | 6 | 13 |
| f40a8e53 | dev | fr | 5 | I | 11 | 24 |
| 0b5d97a2 | dev | en | 6 | BL | 13 | 21 |
| 7d139ac8 | dev | fr | 7 | UF | 14 | 18 |
| e84b2f19 | test | fr | 4 | BLU | 8 | 16 |
| 4a6d90c3 | test | en | 5 | BLM | 4 | 17 |
| b91c5e72 | test | fr | 6 | BLF | 3 | 18 |
| 23e8a6d0 | test | en | 7 | BLI | 10 | 29 |
| d062f4b9 | test | fr | 5 | BUM | 3 | 14 |
| 5fc7a138 | test | en | 4 | BUF | 3 | 9 |
| 8b2e6c40 | test | fr | 7 | BUI | 20 | 25 |
| 1c94d7a6 | test | en | 6 | BMF | 5 | 20 |
| 6e3a08f5 | test | fr | 4 | BMI | 0 | None |
| f7a1d269 | test | en | 5 | BFI | 5 | 13 |
| 3d5b9e01 | test | fr | 6 | LUM | 12 | 23 |
| a063c8f2 | test | en | 7 | LMF | 0 | None |
| 74f20b8d | test | fr | 4 | LUI | 6 | 16 |
| ce1964a7 | test | en | 5 | MFI | 0 | None |
| 2f8c05e1 | test | fr | 6 | BLUMF | 2 | 14 |
| 905e3b6a | test | en | 7 | BLUMFI | 2 | 25 |

Empreintes SHA-256 :

- `build_corpus.py`: `2a16a7005391cb3e6bc97e0befb92d746a6b94830e573298cbd5530d5c923b25`
- `dev_cases.json`: `22afc76c2318d180331693129189a814020ff4e785d17fb8b19eaacfc6c6337b`
- `private_gold.author.json`: `fdead29381317c638d30a961aa0472a38f32f48a6f79d80b65a40a1f9acd9166`
- `test_cases.json`: `f48e5bbe5b16554719e0abd535bd943eee2074c212300f6b76a1ecaaee92b89f`
