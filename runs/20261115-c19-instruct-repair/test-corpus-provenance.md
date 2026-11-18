# C19 — provenance privée du test auteur

Création et gel auteur : 2026-11-15, avant toute génération de test C19.
Ce fichier, build_test_corpus.py et private_gold.author.json restent privés.
Seul test_cases.json est communiqué au LLM et au relecteur public-only.

## Inventaire et construction

Inventaire automatique des contrats structurés gold.json C15 et C16, tous splits :
les 10 signatures de taille 3..6 absentes de leur union sont exactement :
BFILM, BFIM, BFIMU, BFIU, FILM, FILMU, FILU, FIMU, FLMU, ILMU. Deux nouvelles instances par signature, une FR et une EN.
Ce sont des signatures globalement réservées, pas des problèmes mathématiques nouveaux.
Tailles initiales : n_FR=4+(j mod4), n_EN=4+((j+2) mod4), puis échange
approuvé BFIMU_EN : 4→5 et FIMU_EN : 5→4 ; cinq cas par n=4,5,6,7.
Poids entiers 17..61, coûts entiers 13..39, une à quatre arêtes, indices zéro.
Les 20 données, textes et IDs sont distincts de l'historique et entre eux.
Les 20 graphes étiquetés normalisés (n,edges) sont tous distincts entre eux et
de ceux des 48 publics C15/C16 ; aucune unicité à isomorphisme près n'est affirmée.

Recherche pseudo-aléatoire déterministe, un seed par cas, au plus 50000 candidats
par cas. Rejet uniquement sur collision, faisabilité prévue et activité exacte
de chaque famille : retirer une famille doit ajouter une affectation faisable.
Les comptes, témoins et optima viennent d'une énumération des 2^n masques.
Ce filtrage mathématique d'auteur ne mesure aucune performance de modèle.

## Réfutations conservées et corrections avant génération

La première recherche bornée a épuisé 50000 essais pour BFIMU_EN à n4
sans écrire de public. Ce cas faisable ne peut rendre B et U essentiels :
M oblige au moins un élément et F en interdit au moins un, donc au plus
trois indices sont autorisés. U=1 ne permet que le singleton obligatoire
s'il existe, donc B est redondant. Pour U=2, l'activité de U exige que les
trois autorisés passent B ; leurs coûts étant positifs, B accepte alors
tous leurs sous-ensembles et est redondant. U≥3 est lui-même redondant.
L'intégrateur a approuvé avant génération l'échange n de BFIMU_EN et FIMU_EN
décrit ci-dessus. Aucun résultat LLM n'a motivé ce changement de plan.

Une deuxième recherche uniforme, à n5 après correction, a aussi atteint
le plafond de50000 pour BFIMU_EN. Le générateur final utilise pour BFIMU n5
une construction faisable ciblée : M0,F4,U2,I1→2, coûts1/2 en13..16, coût3
en35..39, coût0 en13..39, coût4 en13..26 et B=cost0+cost1+cost2, puis
permutation. Les témoins de retrait sont U:{0,1,2}, B:{0,3}, I:{0,1},
F:{0,4}, M:∅. Les arêtes sont tirées parmi (1,3),(1,4),(2,3),(2,4),(3,4)
avant permutation pour préserver ces témoins. Chaque candidat est néanmoins
recontrôlé exactement et rejeté en cas de collision. Ces deux recherches
avortées précèdent le gel et n'ont produit aucune donnée de génération LLM.

Les gabarits initialement transmis FILMU/ILMU avec seulement I={1→2}, M={0}
et L=U=2 étaient faisables : {0,2} est un contre-exemple, aussi après ajout de
l'indice 4 bloqué par l'arête (0,4). Cette réfutation n'est pas effacée.
Correction approuvée par l'intégrateur avant génération : I={1→2,2→1}.
Le bloc indivisible {1,2} crée alors le trou de cardinalité requis.
FILMU_FR (n5) : M0,F3,L=U2,E={(2,3),(0,4)}, cycle1↔2 avant permutation.
ILMU_FR (n5) : M0,L=U2,E={(0,3),(0,4)}, cycle1↔2 avant permutation.
FILM_EN (n6) conserve le gabarit valide M0,F5,I1→2,L3,E={(0,2),(3,4)}.
Ces trois cas seuls sont infaisables. Tous ont chaque famille essentielle ;
les permutations d'indices sont privées dans le gold. Aucune arête n'a été
ajoutée aux trois gabarits minimaux, et les témoins sont recalculés exactement.

## Texte, connaissance préalable et séparation

Le renderer request() du builder C16 est importé à empreinte fixe, sans appeler
son main. Son texte est conservé, à remplacement du repère C16- par C19- près.
Extension mécanique pour les deux cycles : toutes les implications sont
verbalisées explicitement et la mention 'réciproque non imposée' est retirée.
Les 18 autres cas reprennent exactement le renderer à une implication.
Cette correction garantit que le texte expose tout le contrat ; elle n'est
fondée ni sur une réponse LLM ni sur une sélection de performances.

L'auteur connaît les bilans agrégés C15–C18 et le développement C19 communiqués
par l'intégrateur/research/continuation-c19.md. Il a auparavant conçu C15 et
travaillé sur le driver C16. Aucune nouvelle trace ou métrique de test C19
n'est lue ; aucun appel modèle ou code de vérification de production n'est
exécuté/importé ici. Le corpus est synthétique, pas une population naturelle.
Une relecture distincte réextraira les contrats depuis les seuls publics.
Indépendance de modèle/humaine non démontrée. Aucun quota observé à cette reprise.

Commande : python3 -B runs/20261115-c19-instruct-repair/build_test_corpus.py
Une répétition identique contrôle les mêmes octets ; aucune divergence n'est écrasée.

| ID | Langue | n | Familles privées | Faisables | Optimum | Essais auteur |
|---|---|---:|---|---:|---:|---:|
| a7cee13741d7 | fr | 4 | BFILM | 1 | 87 | 1545 |
| 3c3aeb08aafb | en | 6 | BFILM | 2 | 92 | 47 |
| 312bdf4f360f | fr | 5 | BFIM | 3 | 103 | 10 |
| 433fb7624d1a | en | 7 | BFIM | 2 | 58 | 3 |
| 29507bb778cc | fr | 6 | BFIMU | 6 | 129 | 5316 |
| eca92fb0c776 | en | 5 | BFIMU | 2 | 67 | 1 |
| 765e3caadee5 | fr | 7 | BFIU | 15 | 110 | 41 |
| 4cc6cc21f46a | en | 5 | BFIU | 3 | 38 | 349 |
| 66f7838312e1 | fr | 4 | FILM | 2 | 81 | 2509 |
| 8c55da367b52 | en | 6 | FILM | 0 | None | 1 |
| 409b79d93348 | fr | 5 | FILMU | 0 | None | 1 |
| 2755ab981f66 | en | 7 | FILMU | 14 | 154 | 2 |
| e6637cdda4dc | fr | 6 | FILU | 5 | 97 | 3 |
| 88a560c8b3f6 | en | 4 | FILU | 2 | 52 | 35 |
| 6e8232652580 | fr | 7 | FIMU | 10 | 167 | 1 |
| 417127d82203 | en | 4 | FIMU | 2 | 78 | 2250 |
| 7c800233c771 | fr | 4 | FLMU | 2 | 63 | 650 |
| 4dddb4cfc8db | en | 6 | FLMU | 3 | 96 | 7 |
| 70cc302cf8a4 | fr | 5 | ILMU | 0 | None | 1 |
| caf531e5abc9 | en | 7 | ILMU | 11 | 248 | 1 |

Empreintes des entrées historiques et du renderer :

- runs/20261114-c15-formulation-repair/dev_cases.json: 22afc76c2318d180331693129189a814020ff4e785d17fb8b19eaacfc6c6337b
- runs/20261114-c15-formulation-repair/gold.json: 21fe525a57c12e698fb16d7aaba27dcdfd794a6a778aa1a46512182f6ec8dd8a
- runs/20261114-c15-formulation-repair/test_cases.json: f48e5bbe5b16554719e0abd535bd943eee2074c212300f6b76a1ecaaee92b89f
- runs/20261115-c16-quantized-repair/build_corpus.py: f31f5cbd322a282bb1847198f30e5a10a59d7d714fb1cb2fec6a12d003843ae7
- runs/20261115-c16-quantized-repair/dev_cases.json: 7fa915cda7f7522ec069bcee6c30130a76dba601095c92a9e72585e6c232a3c3
- runs/20261115-c16-quantized-repair/gold.json: 3591f586f76f224ea806c79e843b55286e1a2bfcf234c9341f07c876f154505d
- runs/20261115-c16-quantized-repair/test_cases.json: d62f745775946817ed59b37d6e8f1e25bbbb24d9bdccd4e74ad95a7bd8c1429c

Empreintes du gel auteur avant inférence :

- build_test_corpus.py: 4ae254e2ae728e696386e4cfdc98d8b9cc5de6b000473eda269d7ca39d97c4f9
- private_gold.author.json: 32590e6dae74fe0494e22ec794ec7da1633db2dc8a8cfd5ec33abef898c4c695
- test_cases.json: 742301bb909289baaf1f34f328032851aa1ca8b935ede5b34e4081aa903d223b
