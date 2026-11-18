# C16 — audit des observations conservées

Audit achevé le 15 novembre 2026. L'expérience reste **partielle** : 64 appels tentés, 63 réponses conservées, une réponse guidée inconnue (`54969ba6bb41`) après ENOSPC. L'audit confirme les comptes du rapport partiel, sans importer le scorer, le parser, le vérificateur ou les solveurs de production. Aucune inférence ni nouvelle exécution de solveur n'a été effectuée.

## Résultat principal

| Méthode sélectionnée | Observations | Schéma valide | Fidélité exacte | Faisables | Infaisables |
|---|---:|---:|---:|---:|---:|
| Initial | 16 | 13 | 1/16 | 0/13 | 1/3 |
| Direct, deux candidats | 16 | 15 | 1/16 | 0/13 | 1/3 |
| Auto-révision | 16 | 13 | 1/16 | 0/13 | 1/3 |
| Révision guidée observée | 15 | 12 | 1/15 | 0/12 | 1/3 |

Les quatre méthodes réussissent uniquement sur `79769e445d63`, une instance anglaise infaisable. Il n'y a aucune réparation mathématique observée d'un modèle initialement infidèle, ni régression observée d'un modèle initialement fidèle. Le résultat guidé sur les 16 cas appartient à `[1,2]`; son gain contre l'auto-révision appartient à `[0,1]`. Ce sont des bornes déterministes sur la réponse absente, pas des intervalles de confiance. Le gain d'au moins trois requis par H16 est impossible, même dans le scénario favorable. Aucune valeur n'est imputée à l'appel perdu.

La réussite sur le cas infaisable demande une réserve substantielle. La référence impose l'entrée 1, l'implication 1→2 et au plus une entrée : son domaine est vide. Le modèle initial retenu exige notamment `x0==1` et `x3==1` tout en imposant `x0+x3<=1`; il ajoute aussi des restrictions absentes du texte. Son domaine est également vide et son objectif est identique sur tout le cube. Il satisfait donc le critère extensionnel préenregistré, mais ne démontre pas la récupération des clauses originales. Les deux révisions conservent ce modèle; le direct sélectionne le candidat initial. Aucun cas faisable n'est fidèlement formulé.

L'égalité du seul ensemble des optimiseurs vaut pour trois cas par méthode, contre une seule fidélité et une seule équivalence d'optimisation avec domaine égal. Elle ne doit pas servir de score de fidélité : un modèle peut garder l'optimum tout en supprimant des solutions admissibles.

## Contrôles indépendants

Le [script borné](c16-observed-audit.py) utilise uniquement la bibliothèque standard et un délai interne de 60 secondes. Il interprète les expressions AST sur le vecteur nul et les vecteurs de base, au lieu de reprendre le compilateur de coefficients de production. Les contraintes d'origine sont évaluées directement sur les ensembles d'indices sélectionnés. Les domaines et tous les optima des 16 cas coïncident exactement avec l'[oracle reviewer antérieur](c16-annotation-oracle/raw.json), établi après annotation publique indépendante.

Les 26 863 contrôles passés couvrent : les 63 réponses et paires HTTP conservées; la validité et la normalisation des propositions; les objectifs et faisabilités sur chaque cube binaire; les contre-exemples initiaux et tous les rapports de vérification sélectionnés; la règle de choix direct et les replis des révisions; les historiques de messages, prompts ChatML et SHA; les seeds; les nombres de tokens; les identifiants des tokens choisis, leurs probabilités et leur moyenne logarithmique; les limites et paramètres HTTP enregistrés. Les feedbacks initiaux minimaux correspondent exactement au recalcul et aux payloads guidés. Le script ne construit jamais de modèle corrigé à partir de l'oracle.

Les 15 cas complètement appariés contiennent 50 portfolios valides, soit 100 résultats de solveurs réels enregistrés. Leurs statuts, objectifs, solutions et ensembles d'optima DFS sont tous conformes à une nouvelle énumération exacte de chaque **modèle proposé**. Les statuts et objectifs bruts HiGHS sont cohérents. Le choix du solveur le plus rapide correspond aux temps enregistrés; le coût des deux solveurs est comptabilisé. Les modèles invalides n'ont pas de portfolio. Cette vérification ne reproduit pas les temps et ne transforme pas une solution optimale du mauvais modèle en solution utilisable pour le problème original.

## Coûts et incident

Les 63 réponses conservées totalisent **45 797 tokens d'entrée**, **11 648 tokens de sortie**, **305,620 s** de durées par appel et **0,538434 s** de CPU du client HTTP. Le fichier de la requête interrompue contient 940 identifiants de tokens d'entrée; sa réponse et ses tokens de sortie restent inconnus. Ce coût d'entrée séparé n'est pas ajouté aux sommes de réponses conservées.

| Bras, avec initial partagé | Réponses connues | Entrée | Sortie | Durées des appels |
|---|---:|---:|---:|---:|
| Direct | 32/32 | 19 054 | 5 835 | 132,515 s |
| Auto-révision | 32/32 | 22 449 | 5 953 | 156,580 s |
| Guidé, données partielles | 31/32 | 23 348 | 5 430 | 138,994 s |

Ces bras partagent les mêmes réponses initiales : leurs coûts ne s'additionnent pas comme dépenses physiques distinctes. Le JSON donne aussi les coûts des trois bras sur le seul sous-ensemble apparié de 15 cas. Les feedbacks initiaux prennent 0,004223 s selon les traces. Les portfolios conservés totalisent 1,120323 s, contre 0,008825 s si l'on ne retenait que les temps des solveurs finalement sélectionnés; seul le premier total représente le coût enregistré des deux exécutions.

Les métadonnées complètes des phases initiale, directe, auto et continuation guidée totalisent 246,171549 s de CPU processus client+serveur. Leurs durées par phase incluent le chargement et diffèrent des sommes de durées par requête. La première phase guidée n'a pas de manifeste ni de `generation.json` final valide : son CPU serveur, son chargement et l'appel perdu ne sont pas entièrement mesurés. Aucun coût total complet, énergie ou prix monétaire n'est déduit. Les cinq réponses guidées initialement conservées et les dix cas ensuite continués sont disjoints; la continuation porte uniquement sur les cas jamais appelés. Le cas interrompu n'est pas régénéré.

## Portée, provenance et reproductibilité

Les métadonnées conservées déclarent Qwen2.5-1.5B-Instruct Q4_K_M, llama.cpp b12359, Metal MTL0 avec quatre threads CPU, contexte 2048, plafond 384 tokens, T=0,2/top-k=50/top-p=1. Les réponses HTTP confirment les paramètres d'échantillonnage et les scores de tokens. Ces probabilités sont celles rapportées par l'API épinglée après traitement des samplers; la branche d'acceptation/rééchantillonnage de grammaire peut modifier leur normalisation. Leur moyenne est une heuristique de sélection, pas une log-vraisemblance globale conditionnelle à la grammaire. L'audit présent n'a pas rechargé le GGUF ni revérifié son gros binaire; il vérifie les traces et références conservées, dont tous les fichiers effectivement lus sont hachés avant et après calcul.

Le [contrat](c16-observed-audit.contract.json), le [résultat brut](c16-observed-audit/raw.json) et le [manifeste](c16-observed-audit/manifest.json) conservent la commande, Python 3.9.6, les 146 artefacts d'entrée, leurs SHA, les bornes et le statut du calcul. Le validateur de manifeste retourne `valid evidence record (run status: completed)`. Le [JSON de revue](c16-observed-review.json) est une copie exacte du résultat brut. `completed` qualifie cet audit fini, pas une expérience C16 complète.

Commande de calcul enregistrée : `python3 -B research/c16-observed-audit.py --output research/c16-observed-audit/raw.json`, enveloppée par le runner de computation-audit avec délai 70 s, plafond de logs 65 536 octets et un thread. Les arguments et toutes les entrées sont dans le manifeste; la validation s'effectue par `python3 <computation-audit>/scripts/validate_manifest.py research/c16-observed-audit/manifest.json --root .`.

L'indépendance est celle du recalcul et du rôle de revue : cet agent n'a écrit ni le scorer C16 ni les annotations reviewer C16, mais a participé à l'infrastructure initiale d'inférence C16 et à d'autres corpus. La documentation du parser a été consultée pour respecter le contrat syntaxique, puis une interprétation distincte a été écrite sans import de production. Aucune indépendance humaine, de famille de modèle ou cécité générale n'est revendiquée. Aucun brut C19 n'a été lu pour cet audit; aucun article, state, claim, corpus ou source de production n'a été modifié.
