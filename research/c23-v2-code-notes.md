# C23 v2 — notes de code prospectives

Date : 16 novembre 2026. Auteur de l’implémentation : agent formulation. Ces notes décrivent du code et des fixtures synthétiques, pas un résultat expérimental C23. Aucun modèle, réseau ou corpus/gold C23 n’a été lu ou exécuté pour cette livraison. Les anciens modules C23v1, C22 et antérieurs restent inchangés par cette livraison.

## Précondition matérielle

Le coordinateur a signalé que C24, contexte 6144 et 99 couches GPU, a échoué au premier ubatch avec MetalInsufficientMemory, sans proposition LLM. Cette observation n’a pas été reproduite ici et n’est pas remplacée par les fixtures. Les deux nouveaux drivers demandent désormais **30 couches GPU**, MTL0, 4 threads CPU, batch/ubatch 128, cache KV inchangé. Il s’agit d’un placement partiel proposé : aucune promesse de fit mémoire, d’exécution GPU seule ou de débit.

**C25 doit produire une proposition complète avant tout appel modèle C23.** Cette précondition de protocole appartient au coordinateur ; le texte de métadonnées ne constitue pas un verrou d’autorisation automatique. Chaque phase enregistre séparément les couches demandées et les couches réellement observées dans le journal du chargeur, le total de couches rapporté, le buffer Metal positif et les lignes de preuve. Sans offload Metal observé, aucune complétion n’est demandée.

La phase garde sa borne 1650 s, chaque requête sa borne 180 s et le watchdog serveur 1800 s. Le serveur reste dans le groupe de processus du wrapper : un **watchdog externe du groupe est obligatoire**. Le nettoyage utilise TERM/attente 2 s puis KILL/réattente 10 s ; l’alarme de phase est désarmée pendant cette fenêtre bornée. En cas d’échec de reap, la cause initiale demeure `error`, le second échec devient `cleanup_error` (également `shutdown_error` pour compatibilité), et les stats/`server_reaped` disponibles sont conservées. Un processus noyau bloqué n’est pas déclaré nettoyé.

## Modules nouveaux

- `quantage/repair_iterative_full_inference.py` : copie du driver complet figé, limitée à initial round 0 et direct rounds 1/2. Grammaire générique sans valeurs d’instance ; le LLM rédige les coefficients et clauses.
- `quantage/repair_iterative_patch_inference.py` : deux réparations self/guided ; seules les éditions explicitement produites par le LLM sont appliquées.
- `quantage/repair_iterative_state.py` : matérialisation littérale et provenance des états, sans oracle ni construction de contrainte.
- `quantage/repair_study_c23_v2.py` : préparation trusted du feedback et scoring après génération, sans exécution de modèle.
- `quantage/repair_iterative_checks.py` : fixtures logicielles synthétiques bornées, sans données C23 ni performance LLM simulée.

Tous les appels réservent 1024 tokens de sortie et une position dans un contexte de 6144 : **entrée <= 5119**, y compris si un petit plafond de sortie est demandé par l’API Python. Température 0.7, top-p 0.8, top-k 20. Seed = premiers 8 hex de SHA256(id), plus round 0/1/2 modulo 2^32 ; la valeur réservée 0xffffffff est rejetée. Les deux drivers vérifient que le préfixe natif final assistant est exactement un bloc de pensée fermé et vide. Les probabilités viennent de l’API après sampling ; leur moyenne sert d’heuristique de choix, sans interprétation comme vraisemblance inconditionnelle ou conditionnée exactement par la grammaire.

## Boucle et absence de correction implicite

Round 1 reçoit comme assistant la véritable réponse complète initiale. Round 2 reçoit comme assistant le **raw patch réellement produit au round 1**. Son dernier message user contient `current_model_state`, obtenu par application littérale de ce patch à l’initial, et `state_provenance`. Ce JSON matérialisé n’est jamais étiqueté comme une nouvelle génération LLM. Les SHA de l’initial, du patch précédent et de la base sérialisée permettent le replay. Le nouveau patch est parsé par `parse_patch` contre cette base exacte, jamais comme une formulation complète.

L’état courant est le dernier candidat syntaxiquement valide. Si le patch 1 est invalide, l’initial valide reste courant, dans les deux bras. Sans état valide au round 2, l’état public est null et la première édition doit être un `replace_model` explicite ; une réparation locale cachée d’un objet initial invalide est refusée. Aucun certificat sémantique ne choisit l’état ou le candidat. Le diagnostic textuel du LLM est conservé mais n’a aucun effet sémantique.

Guided reçoit le feedback trusted sur l’état courant : verdict/contre-exemple minimal et évaluation exacte des propres lignes du candidat, avec gloss générique. Aucun coefficient ou ligne du modèle de référence n’est transmis. Self reçoit seulement la consigne et l’état. Les quatre canaux de patch utilisent la même consigne système fournie par le coordinateur. Le gold est lu uniquement par les modes offline feedback/score du contrôleur, jamais par les drivers d’inférence.

## Interface de lancement pour le coordinateur

Tous les répertoires de sortie doivent être neufs. Les drivers exigent `--server-binary`, `--model`, `--acquisition`, `--cases`, `--instructions`, `--output` et `--execute`. Le coordinateur fournit les mêmes b12359/GGUF/acquisition épinglés et son wrapper avec watchdog ; ces notes n’exécutent aucune commande d’inférence.

1. Driver complet : `python -m quantage.repair_iterative_full_inference`, `--phase initial --round 0`, puis deux phases indépendantes `--phase direct --round 1` et `--phase direct --round 2`, avec la même consigne initiale.
2. Feedback initial : `python -m quantage.repair_study_c23_v2 feedback --cases PUBLIC --gold PRIVATE --initial INITIAL/raw.jsonl --round 0 --output FEEDBACK0`. Les seuls résultats envoyés au driver sont `FEEDBACK0/minimal.json`.
3. Driver patch round 1 : `python -m quantage.repair_iterative_patch_inference`, `--phase self|guided --round 1 --initial INITIAL/raw.jsonl --initial-instructions INITIAL_INSTRUCTIONS`. Guided ajoute `--feedback FEEDBACK0/minimal.json` ; self ne passe pas ce flag.
4. Feedback après guided1 : mode `feedback`, mêmes cases/gold/initial, `--round 1 --previous GUIDED1/raw.jsonl --phase guided --output FEEDBACK1`. Il vérifie l’état courant littéral, y compris le fallback syntaxique.
5. Driver patch round 2 : mêmes arguments historiques, `--round 2 --previous SELF1/raw.jsonl` pour self ; `--previous GUIDED1/raw.jsonl --feedback FEEDBACK1/minimal.json` pour guided. Les patches précédents ne sont jamais rééchantillonnés.
6. Score complet : mode `score`, cases/gold/initial et les six flags `--direct1`, `--direct2`, `--self1`, `--self2`, `--guided1`, `--guided2` vers leurs `raw.jsonl`, plus `--feedback-reports FEEDBACK0/reports.jsonl FEEDBACK1/reports.jsonl`. Une matrice partielle n’est pas imputée. Le score initial seul est aussi possible sans ces six flags.

Direct choisit parmi initial/direct1/direct2 selon validité syntaxique, puis moyenne logprob, puis premier en cas d’égalité. Self/guided gardent le dernier état valide. Les résultats après round 1 et finaux, les régressions par rapport à l’initial et celles du round 1 vers le final sont tous enregistrés. Les modèles évaluables passent ensuite par vérification finie et les deux vrais solveurs DFS/HiGHS ; ce diagnostic postérieur ne modifie aucun choix. La fidélité est un résultat borné au cube et au contrat annoté, pas une garantie générale de compréhension.

## Coûts, hypothèse et vérification

Pour 20 cas complets : 7 propositions physiques par cas (initial partagé, deux direct, deux self, deux guided), donc **140 appels physiques / 180 attribuables**. Chaque bras coûte 3 appels et au plus 3072 tokens générés par cas. Le scorer conserve tous les raws, y compris patches invalides et diagnostics, leurs tokens/EOS, coûts client, métadonnées serveur/chargement et coûts de matérialisation, feedback, replay, vérification et portfolio. Énergie GPU et coût de session complet demeurent inconnus.

Le code expose la proposition H23 : gain final guided-self d’au moins 3 cas fidèles et au plus 1 régression finale guided depuis l’initial. **Le coordinateur doit figer cette règle avant tout test** ; les fixtures n’en sont pas une évaluation empirique.

Commande auteur exécutée : `python3 -B -m quantage.repair_iterative_checks --output research/c23-v2-code-notes.json`. Huit groupes passent, dont deuxième réparation supprimant une erreur résiduelle, replay/fallback/replacement explicite, cap d’entrée fixe, seeds, message assistant authentique, sélection sans gold, 7/9 appels, refus de provenance altérée et état logiciel de cleanup TERM2/KILL10 pour les deux drivers. Les solveurs classiques exécutent réellement les fixtures synthétiques ; le processus de cleanup y est un objet de test, sans mesure de performance. Résultats, empreintes des sources et provenance de revue : JSON compagnon.

Deux défauts initiaux détectés indépendamment ont été corrigés avant modèle : réparation locale d’un état null et contournement du cap d’entrée avec un plafond de sortie réduit. La relecture indépendante du delta 30 couches / nettoyage renforcé ne constate aucun défaut bloquant dans ce périmètre. Elle exécute les huit groupes synthétiques une seule fois et confirme les empreintes courantes ; ses réserves sur l’absence de preuve matérielle sont conservées dans le JSON. Aucune de ces vérifications ne démontre la viabilité matérielle, l’utilité du feedback ou H23.
