# C19 — revue du test observé

15 novembre 2026. **H19 n'est pas soutenue sur ce test fini** : guidée 13/20 contre auto-révision 12/20, soit +1 pour un seuil préenregistré de +4. La guidée produit une réparation mathématique et une régression; sa condition d'au plus une régression est satisfaite. Le direct atteint 15/20. Les 80 appels physiques ont une réponse conservée; l'incident disque a arrêté l'auto-révision avant l'appel suivant, puis seuls les sept cas jamais appelés ont été continués.

## Résultats recalculés

| Méthode sélectionnée | Fidélité stricte | Faisables | Infaisables | FR | EN | Réparations depuis initial | Régressions |
|---|---:|---:|---:|---:|---:|---:|---:|
| Initial | 13/20 | 10/17 | 3/3 | 7/10 | 6/10 | — | — |
| Direct, deux candidats | 15/20 | 12/17 | 3/3 | 9/10 | 6/10 | 2 | 0 |
| Auto-révision | 12/20 | 9/17 | 3/3 | 7/10 | 5/10 | 0 | 1 |
| Révision guidée | 13/20 | 10/17 | 3/3 | 8/10 | 5/10 | 1 | 1 |

Les 80 réponses respectent le schéma et terminent sur EOS; les améliorations observées ne sont donc pas des réparations de format. Le direct retient l'initiale dans 17 cas et son second candidat dans trois; auto et guidée retiennent leur seconde réponse dans les vingt cas. Les objectifs initiaux et directs sont identiques à la référence sur tout le cube; l'auto et la guidée ont chacune 64 désaccords d'objectif, tous sur le même cas. Les nombres cumulés de désaccords de faisabilité sont respectivement 17, 9, 17 et 16 sur 1 200 affectations comparées par méthode. Aucun score n'est imputé et aucun cas n'est exclu.

Trois exemples rendent le diagnostic vérifiable :

- **Réparation guidée `66f7838312e1`, FR, n=4.** L'initiale omet « au moins deux éléments » et accepte à tort `[0,0,1,0]`. Le feedback contient ce témoin et ses deux booléens, sans clause corrigée. La guidée ajoute elle-même `x0+x1+x2+x3>=2`. Son domaine passe de trois à deux affectations, exactement celles de la référence; l'objectif et les autres clauses restent fidèles. L'auto et le direct sélectionné restent infidèles sur ce cas. C'est une réparation mathématique faisable réellement observée.
- **Régression `caf531e5abc9`, EN, n=7.** L'initiale est fidèle. Auto et guidée changent le poids de l'entrée 1 de 46 à 48, malgré le feedback guidé `no_counterexample`. Elles gardent le domaine et l'ensemble des optimiseurs, mais modifient l'objectif sur les 64 affectations contenant cette entrée. Le maximum et son optimiseur restent ici identiques. Cette régression montre pourquoi la fidélité de toutes les valeurs d'objectif est distincte de l'accord sur l'optimum.
- **Deux améliorations directes.** Le deuxième candidat de `29507bb778cc` rétablit l'implication 5→4 omise; celui de `765e3caadee5` remplace l'implication erronée 5→4 par 6→4. La sélection par validité puis score de tokens retient ces candidats sans consulter leur certificat final. Les deux références sont faisables. Le résultat ne prouve pas que cette heuristique est supérieure hors de ces vingt cas.

Les trois références infaisables sont réussies par les quatre méthodes. L'égalité de deux domaines vides ne démontre pas à elle seule la compréhension des clauses; ces cas sont séparés dans le tableau. Le gain guidé est +1 également sur les seuls cas faisables et reste inférieur au seuil de quatre. Les scores d'équivalence d'optimisation avec domaine égal sont 13, 15, 13 et 14; ils dépassent la fidélité stricte pour les deux révisions à cause de la régression d'objectif décrite ci-dessus. L'égalité isolée des ensembles d'optimiseurs donne 15, 16, 15 et 15 et constitue une exigence encore plus faible.

## Contrôles et solutions

Le [script](c19-observed-review.py) réutilise l'interpréteur algébrique distinct écrit pour l'audit C16; il n'importe aucun scorer, parser, vérificateur ou solveur de production. Huit contrôles manuels couvrent une normalisation algébrique, quatre syntaxes interdites, un domaine singleton, son optimum et un domaine vide. Les 23 506 contrôles de l'audit passent. L'interprétation AST ne contient ni `eval` ni `exec`; la référence est évaluée directement sur les ensembles d'indices sélectionnés.

Les domaines et tous les optima des vingt cas coïncident exactement avec l'[oracle reviewer](c19-annotation-oracle/raw.json). Les 80 propositions sont reparsées depuis leur texte brut, puis évaluées sur leur cube complet; les modèles compilés, rapports sélectionnés et métriques agrégées concordent avec les traces conservées. Les contre-exemples initiaux et leurs payloads guidés correspondent au recalcul indépendant. Les messages contiennent uniquement les consignes, données publiques, réponse initiale et feedback minimal attendus. Les requêtes `/apply-template`, prompts rendus, SHA, seeds, tokens d'entrée/sortie et moyennes logarithmiques des probabilités de tokens choisis sont vérifiés contre les fichiers HTTP. Le contrôle porte sur ces traces; il ne réexécute pas le template GGUF ou son tokenizer.

L'union auto contient exactement les treize réponses physiques originales et les sept réponses de continuation, sans doublon. Chaque source possède autant de requêtes de complétion que de réponses. L'erreur originale indique un arrêt avant le prochain appel pour réserve disque inférieure à 1 GiB. La liste de continuation correspond exactement au complément des treize ID déjà appelés; aucune réponse n'est régénérée.

Les 80 portfolios enregistrés, soit **160 résultats de solveurs**, sont contrôlés contre une nouvelle énumération exacte de chaque modèle candidat. Statuts, objectifs, solutions, ensembles complets des optima DFS et statuts/objectifs bruts HiGHS concordent. La sélection du solveur le plus rapide est conforme aux temps enregistrés. Aucun solveur n'est relancé et les temps ne sont pas reproduits. Accord DFS/HiGHS signifie que le modèle proposé est résolu correctement; son utilisation pour le problème d'origine exige aussi la fidélité. Le JSON conserve séparément les solutions incidentellement faisables ou optimales pour l'original : elles ne remplacent pas ce certificat.

## Coûts observés et limites matérielles

Les 80 réponses totalisent **61 763 tokens d'entrée**, **9 260 tokens de sortie**, **748,058 s** de durées par appel et **1,319348 s** de CPU du client HTTP. Ces nombres concordent avec les métriques publiées par le scorer.

| Bras avec initial partagé | Appels attribuables | Entrée | Sortie | Durées des appels |
|---|---:|---:|---:|---:|
| Direct | 40 | 27 274 | 4 667 | 371,179 s |
| Auto-révision | 40 | 30 325 | 4 582 | 373,772 s |
| Guidé | 40 | 31 438 | 4 593 | 382,079 s |

Le plafond est identique, deux appels de 512 tokens au plus par bras et cas; les longueurs utilisées diffèrent. L'initiale est partagée : additionner les trois bras compterait ses vingt réponses trois fois, soit 120 appels attribuables contre 80 physiques. La révision guidée utilise davantage de tokens d'entrée. Le calcul enregistré des feedbacks initiaux prend 0,010104 s.

Les cinq processus physiques d'inférence conservés totalisent **907,255 s** de durée par phase, dont **102,438 s** de chargement, et **241,567856 s** de CPU client+serveur. L'auto comporte deux chargements, tous deux inclus. Les portfolios prennent **1,221463 s** au total pour les deux solveurs, contre **0,012508 s** si l'on ne gardait que leurs temps sélectionnés ex post; le coût complet est le premier.

**Le processus parent de nettoyage disque n'est pas inclus dans les lignes ni dans ce total CPU client+serveur.** Son CPU propre, l'activité globale de l'hôte, les coûts de développement/annotation/session et l'énergie ne sont pas entièrement comptés. Le nettoyage borné est concomitant à la continuation; ces temps sont descriptifs, pas un benchmark de latence isolé ni une comptabilité exhaustive. Les durées de wrappers disponibles figurent dans les métriques originales et diffèrent encore des durées des processus d'inférence.

Les traces enregistrent Qwen3-4B-Instruct-2507, conversion communautaire Q4_K_M, runtime officiel llama.cpp b12359, Metal MTL0 avec quatre threads CPU, contexte 4096, T=0,7/top-k=20/top-p=0,8. Les paramètres HTTP sont vérifiés; les métadonnées de chargement indiquent 37/37 couches déportées et un buffer Metal, sans preuve d'une exécution exclusivement GPU ni mesure exhaustive de RAM globale. La grammaire linéaire est générique; le modèle écrit lui-même indices, coefficients et clauses. Les probabilités de tokens sont celles de l'API après traitement des samplers; leur normalisation peut dépendre de la branche de grammaire. Leur moyenne reste une heuristique de sélection.

## Provenance et statut de revue

Le [contrat](c19-observed-review.contract.json), le [résultat brut](c19-observed-review.audit/raw.json) et le [manifeste](c19-observed-review.audit/manifest.json) enregistrent 446 artefacts d'entrée, SHA avant/après, Python 3.9.6, la commande et les bornes. Le script impose 60 s; le runner impose 70 s, un thread et 65 536 octets de logs. Les 26 artefacts du gel v2 sont conformes à leurs SHA. Les fichiers GGUF et binaires volumineux ne font pas partie de ces 26 entrées du gel et ne sont pas rechargés ou revalidés ici; leurs métadonnées d'acquisition restent celles de l'expérience.

Commande de calcul : `python3 -B research/c19-observed-review.py --output research/c19-observed-review.audit/raw.json`, enveloppée par le runner de computation-audit; arguments complets dans le manifeste. Le validateur retourne `valid evidence record (run status: completed)`. Le [JSON de revue](c19-observed-review.json) est une copie exacte du résultat brut. `completed` indique que ce calcul de revue est terminé, sans transformer H19 en hypothèse confirmée.

**Limite d'indépendance :** cet agent a écrit le corpus C19 et participe maintenant au recalcul final après indisponibilité des autres agents. Le calcul est distinct du scorer et utilise les annotations et l'oracle d'un reviewer séparé; cette revue finale n'est ni aveugle ni indépendante de l'auteur du corpus. Les comptes ont aussi été communiqués par l'intégrateur avant la revue. Aucune indépendance humaine ou de famille de modèle n'est revendiquée. Le rapport ne fonde aucune nouveauté, garantie de généralisation, effet causal du changement C16→C19 ou avantage quantique. Aucun article, state, claim, corpus, modèle ou source de production n'a été modifié.
