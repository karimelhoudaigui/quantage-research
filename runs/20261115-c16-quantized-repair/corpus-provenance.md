# C16 — provenance privée du corpus auteur

Création : 2026-11-15. Avant toute inférence C16. Aucun brut du test C15 lu.
Le rôle auteur a lu la conception et les diagnostics agrégés C15; les requêtes publiques
C15 sont lues seulement pour les contrôles de collision. Le code de vérification, les
réponses LLM, les prompts/grammaires C16 et le gold relecteur ne sont pas importés.
Les textes sont des compositions synthétiques déterministes FR/EN, et non 24 textes
rédigés indépendamment ou des observations naturelles. Le filtrage des paramètres
repose exclusivement sur les ensembles faisables exacts avant toute génération.
Le seed de conception et le nombre d'essais sont conservés dans le gold auteur.

8 dev : 4 FR/4 EN, deux par n=4..7, six familles seules et doubles BI/LM.
16 test : 8 FR/8 EN, quatre par n=4..7; 16 signatures inédites par rapport au
test C15, de 3 à 5 familles (dans l'intervalle demandé 3..6). L'unique signature
à six familles était déjà présente en C15 et n'est donc pas réutilisée.
Les graphes normalisés (n,edges) sont distincts entre les 24 cas et de tous ceux
du corpus C15, de même que les données complètes et les textes. Arêtes : 1..4.
Poids : 17..61; coûts : 13..39. Unités abstraites, bornes inclusives, indices à zéro.
Les implications sont à sens unique. Les familles absentes restent absentes.

Exactement trois tests sont infaisables. Pour chaque famille présente, même dans
ces cas, supprimer toute cette famille ajoute une affectation faisable. Les
comptes et témoins sont dans author_check.family_drop_checks; les optima sont
des contrôles exacts d'auteur, jamais des performances de LLM. Les exclusions
sont dans edges; aucun encodage matériel/QPU n'est revendiqué.

Ce fichier, build_corpus.py et private_gold.author.json sont privés pour l'expérience.
Seuls dev_cases.json et test_cases.json sont fournis au LLM et au relecteur aveugle.
Une revue distincte doit extraire les clauses du texte sans importer ce générateur.
Indépendance humaine ou de famille de modèles non établie; quota auteur non rencontré.

Commande : python3 runs/20261115-c16-quantized-repair/build_corpus.py
Répétition : mêmes fichiers ou erreur avant remplacement d'un artefact différent.

| ID | Split | Langue | n | Familles | Faisables | Optimum | Essais auteur |
|---|---|---|---:|---|---:|---:|---:|
| 4e0256180e89 | dev | fr | 4 | B | 7 | 86 | 2 |
| a21822897a9c | dev | en | 5 | L | 12 | 141 | 1 |
| f79cab9b73d0 | dev | fr | 6 | U | 39 | 150 | 1 |
| 080d034c34b2 | dev | en | 7 | M | 48 | 237 | 1 |
| ffa9d668bbda | dev | en | 4 | F | 6 | 67 | 2 |
| b97cb5f56812 | dev | fr | 5 | I | 15 | 125 | 1 |
| f60764a678d2 | dev | en | 6 | BI | 19 | 149 | 2 |
| d28fc0e8d61e | dev | fr | 7 | LM | 26 | 191 | 3 |
| fcec7afd3dd6 | test | fr | 4 | LUF | 3 | 53 | 4 |
| 79769e445d63 | test | en | 4 | UMI | 0 | None | 4 |
| 38289dce9fa8 | test | fr | 4 | LFI | 0 | None | 3 |
| bc6455847de3 | test | en | 4 | UMF | 3 | 78 | 258 |
| 192394ff7b7a | test | fr | 5 | LMI | 0 | None | 1 |
| a84cf14c247d | test | en | 5 | UFI | 4 | 61 | 4 |
| 2869335ff788 | test | fr | 5 | BLUM | 2 | 56 | 79 |
| 5c92952e6b23 | test | en | 5 | BLUF | 4 | 86 | 792 |
| cd5f7022ac2e | test | fr | 6 | BLUI | 4 | 61 | 65 |
| bce63f435951 | test | en | 6 | BLMF | 5 | 156 | 10 |
| dcdad683f9dc | test | fr | 6 | BLMI | 4 | 156 | 13 |
| 37e4073ab724 | test | en | 6 | BLFI | 7 | 83 | 3 |
| e208889911d5 | test | fr | 7 | BUMF | 5 | 93 | 926 |
| 0917fa453976 | test | en | 7 | BUMI | 14 | 104 | 248 |
| 5d9702fb5f6c | test | fr | 7 | BLUMI | 6 | 161 | 385 |
| 54969ba6bb41 | test | en | 7 | BLUFI | 9 | 103 | 393 |

Empreintes avant inférence :

- build_corpus.py: f31f5cbd322a282bb1847198f30e5a10a59d7d714fb1cb2fec6a12d003843ae7
- dev_cases.json: 7fa915cda7f7522ec069bcee6c30130a76dba601095c92a9e72585e6c232a3c3
- test_cases.json: d62f745775946817ed59b37d6e8f1e25bbbb24d9bdccd4e74ad95a7bd8c1429c
- private_gold.author.json: 3ffb3fb71f049c1d461afbeec233f43758f4ac5f08a488c327f0da47f52af665
