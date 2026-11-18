# C05 — contrat sémantique et références primaires

Rôle littérature, 13 novembre 2026. Travail effectué par un sous-agent distinct
de l'auteur de C01–C04; la mission contient leur constat sur la sémantique et
la revue n'est donc pas aveugle. Ce rapport n'est pas une nouvelle mesure de
performance et n'évalue aucune sortie LLM. Accès web disponible pendant cette
reprise; aucune limite d'utilisation rencontrée sur cette tâche.

## Périmètre et réemploi

Lecture de `research/state.md`, `research/sources/index.json`,
`runs/20261113-c01-foundation/literature.md`, `research/next-experiment.md`,
`quantage/core.py`, `quantage/verification.py` et du protocole C04. Les sources
déjà indexées sont réutilisées; aucun deuxième index ni copie intégrale de
texte sous copyright n'est créé. Les trois textes primaires ci-dessous ont été
rouverts, au-delà de leurs résumés. Nouvelle question : quelles annotations
indépendantes relient le texte initial au problème soumis au vérificateur ?

## Vérification des définitions dans les sources

**NL4Opt.** Rindranirina Ramamonjison, Timothy T. Yu, Raymond Li, Haley Li,
Giuseppe Carenini, Bissan Ghaddar, Shiqi He, Mahdi Mostajabdaveh,
Amin Banitalebi-Dehkordi, Zirui Zhou et Yong Zhang,
*NL4Opt Competition: Formulating Optimization Problems Based on Their Natural
Language Descriptions*. PMLR 220:189–203, année imprimée 2023, compétition
NeurIPS 2022. [PDF primaire](https://proceedings.mlr.press/v220/ramamonjison23a/ramamonjison23a.pdf),
§2 et §2.1, pages imprimées 191–193, consultés le 13 novembre 2026.
Les entités couvrent directions et limites de contraintes, direction et nom
d'objectif, paramètres et variables. La deuxième tâche reçoit les entités
de référence; elle ne mesure donc pas toute la chaîne depuis le texte seul.
L'évaluation de génération compare les déclarations dans une représentation
canonique, avec faux positifs et faux négatifs. Cette définition justifie de
mesurer les clauses séparément de l'issue numérique. Elle ne fournit pas un
théorème d'équivalence pour nos graphes pondérés ou nos circuits optiques.
Authentification et extraction : vérifiées; application au choix de notre
annotation : analogue méthodologique, pas transfert de résultat expérimental.

**OptiMUS-0.3.** Ali AhmadiTeshnizi, Wenzhi Gao, Herman Brunborg, Shayan Talaei,
Connor Lawless et Madeleine Udell, *OptiMUS-0.3: Using large language models
to model and solve optimization problems at scale*.
[arXiv:2407.19633v4](https://arxiv.org/html/2407.19633v4), 26 juin 2026;
§3, §4 (définitions et étapes), §5.1 (métriques) et §5.3 (erreurs),
rouverts le 13 novembre 2026. Le texte distingue variables, contraintes,
objectif, paramètres numériques et clauses; il suppose la description
suffisante et identifie l'ambiguïté comme une limite. L'évaluation combine
exécution, valeur optimale et solutions lorsque les références existent;
certaines données ne permettent qu'une comparaison des valeurs. Les auteurs
signalent que des paramétrisations valides différentes peuvent être pénalisées.
Conséquence pour QuantAge : déclarer l'équivalence acceptée et la disponibilité
de la vérité terrain à chaque niveau. Aucun chiffre du papier n'est reproduit
ici; notre vérification de contrat ne doit pas être présentée comme le score
OptiMUS. Authentification et définitions : vérifiées; application à notre
protocole : choix motivé, pas validation des performances de nos agents.

**Perceval.** Nicolas Heurtel et al., *Perceval: A Software Platform for Discrete
Variable Photonic Quantum Computing*, Quantum 7:931 (2023),
[arXiv:2204.00602v3](https://arxiv.org/html/2204.00602), 20 février 2023.
§3.2.3–3.2.4, §3.2.7 et §4.2.1 rouverts le 13 novembre 2026. Le texte
distingue échantillonnage, amplitude, probabilité et distribution complète.
Source, circuit, détecteurs et post-sélection appartiennent au modèle du
processeur. Les distributions de comptage multiphotoniques comportent la
normalisation factorielle des occupations. Cette source motive d'annoter
l'observable, l'entrée, les conventions et le conditionnement séparément.
Elle ne prouve ni accès Quandela actuel ni validité matérielle du circuit
QuantAge. Authentification et extraction : vérifiées; réduction à un photon
idéalisé : conditionnelle aux hypothèses de notre contrat. Aucun SDK exécuté.

## Annotation indépendante proposée — conception QuantAge

Les champs ci-dessous constituent notre proposition de protocole, non une
citation des trois sources. Ils doivent être annotés depuis l'intention et ses
données, avant de lire une proposition d'agent ou son résultat numérique.
Le parseur, le formulateur et leur propre vérificateur ne peuvent créer seuls
leur vérité terrain sémantique.

Pour chaque cas, conserver `case_id`, `base_intention_id`, version du texte,
langue, données structurées et hash, extraits précis justifiant les clauses,
identité/version de l'annotateur et désaccords. Une clause possède un état
`explicit`, `entailed`, `ambiguous`, `missing` ou `contradicted`, une portée
et, s'il y a lieu, la question de clarification. Ne pas remplir un champ
manquant par la valeur par défaut du moteur puis traiter cette valeur comme
une annotation indépendante. Une condition supplémentaire explicite ne doit
pas disparaître dans la normalisation.

| Élément | MIS pondéré | Probabilités optiques à un photon |
|---|---|---|
| Objets et index | sommets étiquetés, graphes simples non orientés, sens des arêtes de conflit | modes étiquetés, ordre entrée/sortie, mode initial et occupation |
| Variables et domaine | indicatrice binaire d'inclusion par sommet | amplitudes complexes, un photon et deux modes pour le moteur actuel |
| Critère demandé | maximiser la somme des poids; distinguer cardinalité, maximalité et minimisation | distribution ordonnée de probabilités; distinguer amplitudes, échantillons et observable scalaire |
| Contraintes | aucune paire adjacente sélectionnée; compter aussi cardinalité imposée, sommet obligatoire, budget, etc. | circuit et ordre des composants; phase appliquée à quel mode; cohérence, pertes et autres imperfections |
| Données et unités | poids positifs entiers pour le moteur actuel; association poids–sommet et unités si présentes | angles finis en radians; convention de rotation, signes et demi-angle; unités à convertir seulement si explicites |
| Sortie et équivalence | valeur, une solution ou toutes; correspondance des sommets obligatoire | étiquetage des sorties, probabilité conditionnelle ou non, événement de post-sélection et sa probabilité |
| Portée matérielle | référence mathématique locale; géométrie et accès Pasqal non déduits du QUBO | modèle idéal local; accès, bruit et acquisition Quandela non déduits du circuit |

Dans le moteur C01, la photonique fixe l'entrée à `[1,0]`, deux modes,
pertes nulles et la séquence `R_b P R_a`. Un texte qui ne détermine pas ces
éléments ne devrait pas être déclaré équivalent automatiquement. Une demande
de maximisation de poids avec des poids négatifs est compréhensible, mais
sort du domaine positif du moteur; séparer «compris mais non supporté»
de «sens indéterminé». Une nouvelle famille nécessite son propre contrat.

## Critère de fidélité et limites des certificats

Deux niveaux sont à conserver : (1) fidélité des clauses et de la portée du
contrat proposé au texte annoté; (2) validité de la formulation ou du résultat
dans ce contrat. Un succès au second niveau n'implique pas le premier.
`verification.py` reçoit le problème déjà normalisé : il ne lit pas l'intention
originale et ne certifie donc pas cette flèche.

Pour MIS, des sommes et ordres de sommets différents peuvent être équivalents
si une bijection déclarée et le décodage préservent les poids et les conflits.
Une QUBO avec constante ou facteur positif différent peut préserver les
minimiseurs tout en changeant l'énergie numérique; la valeur reconstruite de
l'objectif initial doit être rapportée séparément. Ne pas exiger l'égalité
brute des coefficients pour juger la sémantique. Inversement, un optimum
partagé sur une instance ne prouve pas la fidélité de l'ensemble des clauses.

Pour la tâche «probabilités», une phase globale ne modifie pas la réponse;
la permuter avec une phase relative est une erreur. La comparaison doit
respecter les étiquettes des modes et le conditionnement demandé. Deux
circuits qui coïncident sur l'entrée fixée sont indistinguables pour cette
réponse particulière : les marquer «équivalents pour l'observable et l'entrée
testées», sans certifier l'unitaire complet. Si la tâche porte sur la
transformation ou des entrées multiples, étendre la vérité terrain avant
l'expérience. Il n'est pas justifié d'étiqueter toute différence de structure
comme une erreur observable.

## Mesures et séparation proposées

- Rapporter les omissions, ajouts et contradictions par clause, puis un
  critère binaire «toutes les clauses requises fidèles»; conserver les cas
  ambigus séparément. Les scores d'entités ou de déclarations ne sont pas
  automatiquement interchangeables avec notre fidélité de contrat.
- Rapporter couverture sur cas bien définis et supportés, risque parmi les
  acceptations, refus corrects hors portée et clarifications sur cas ambigus.
  Une abstention justifiée ne doit pas devenir une mauvaise compréhension.
- Réutiliser exactement la même proposition avant/après vérificateur, journaliser
  tous les refus et corrections, puis contrôler le contrat corrigé de nouveau.
  Une régénération constitue une intervention supplémentaire à distinguer.
- Grouper paraphrases, mutations et mêmes données de base dans le même split;
  C01–C04 restent développement. Figer les annotations et le schéma avant les
  sorties d'agent. Une évaluation généralisante demande ensuite des cas plus
  larges et indépendants de cet auteur.

Statut bibliographique : chevauchement **partial or adjacent result only**;
aucune affirmation de nouveauté. Consultation ciblée de trois sources déjà
indexées, pas recherche exhaustive, pas de suivi complet des citations.
Prochaine action : obtenir un jeu de contrats annoté par un second rôle avant
génération; comparer séparément fidélité sémantique, validité numérique et
couverture d'abstention sur propositions réelles dûment journalisées.
