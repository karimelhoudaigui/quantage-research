# C28 — pilote borné de viabilité sous la configuration C23

## Question et priorité

C23 est l'étude réservée liée à l'article sur la formulation et la réparation de modèles ILP par un agent. Son ancien gate C25 n'a pas produit de proposition complète. C27 a réussi une génération sur un cas de développement, mais avec 99 couches demandées et des caches K/V `q8_0`, donc il ne teste pas la configuration du driver C23. Après l'autorisation explicite de l'utilisateur d'amender prospectivement le gate, C28 vérifie si **un seul** appel initial peut produire une proposition complète sous la configuration réellement demandée par C23. La priorité est le risque de ressources et de faisabilité d'exécution; C28 ne teste aucune hypothèse scientifique de l'article.

## Sources et séparation

- Cas : `case.json`, copié sans transformation depuis l'ancien jeu de test C19 désormais réservé au développement. Il s'agit du cas n=7 dont l'intention est la plus longue parmi les cas n=7 de cette source (règle et identifiant déterministes vérifiés avant gel). Il ne provient pas du corpus C23.
- Instructions : `runs/20261115-c19-instruct-repair/instructions.frozen.txt`, mêmes instructions génériques de formulation initiale.
- Modèle et runtime : artefacts locaux acquis et épinglés dans les métadonnées C22; llama.cpp b12359 et Qwen3-8B-Q4_K_M.
- Driver : `quantage.repair_iterative_full_inference`, avec vérifications d'intégrité et de contexte.
- Le corpus C23, ses annotations, son gold et ses sorties sont exclus des entrées, des commandes et du gel C28. Aucune référence ou réponse attendue n'est transmise au modèle.
- Les constatations matérielles antérieures proviennent du `--help` local de b12359 et de la revue C27. C23 ne fixe pas explicitement Flash Attention ni les types de cache : le runtime garde ses valeurs par défaut (`auto` et K/V `f16`). Le placement demandé reste 30 couches Metal, batch/ubatch 128 et quatre threads. Une configuration demandée ne garantit ni mémoire disponible ni succès.

## Protocole préenregistré

- Un seul cas, une génération initiale, aucun retry, continuation, réparation ou nouvelle graine.
- Contexte 6144; plafond de sortie 1024; réserve complète fixe de 1024 tokens, donc entrée maximale 5119, sans troncature.
- Serveur local b12359, `--offline`, loopback uniquement, modèle Qwen3-8B-Q4_K_M épinglé; 30 couches GPU demandées sur `MTL0`, quatre threads, batch/ubatch 128; aucun argument Flash Attention ou K/V ajouté au driver.
- Échantillonnage : température 0,7, top-k 20, top-p 0,8; graine initiale déterministe `int(first8hex(SHA256(id)),16) mod 2**32`, sentinelle `0xffffffff` refusée.
- Au plus 180 s par requête; phase 1650 s; watchdog de groupe externe 1800 s avec arrêt et reap bornés. Budget : une requête locale, aucun coût externe.
- Le wrapper refuse la réutilisation d'une sortie et vérifie avant exécution l'égalité du cas avec sa source C19 et la sélection n=7 préenregistrée. Il gèle les sources, hashes, commande, commit/arbre de départ et manifeste avant d'appeler le runner borné.

## Critère de passage du gate

C28 passe uniquement si le runner se termine sans timeout ni résultat manquant/invalide, le driver conserve exactement une réponse, la réponse s'arrête sur EOS (pas sur le plafond), le parseur ILP l'accepte, le runtime rapporte Metal avec au moins une couche effectivement déchargée, le serveur est reap et `cleanup_error` est nul. Le critère atteste une exécution de ce cas seulement; il ne prouve ni marge mémoire, ni débit garanti, ni aptitude des phases de réparation, ni validité mathématique du modèle par rapport à la demande.

Tout échec, timeout, arrêt incomplet, réponse invalide ou configuration observée contraire bloque C23 et clôt le pilote sans retry. En cas de succès seulement, le gate C28 autorise la préparation puis l'exécution séparées de C23, après gel du protocole complet de C23; il ne lance pas automatiquement cette étude.

## Validation et limites

Avant inférence : vérifier les hashes des sources, l'égalité de l'instance, les tests logiciels ciblés et le dry-run. Après inférence : vérifier les artefacts bruts, la commande réellement utilisée, le comptage des tokens, EOS, le schéma parseur, l'observation Metal et le statut du serveur; aucun solveur ni gold n'est nécessaire au gate de capacité.

La sélection d'un cas de développement posthoc n'est pas une estimation de population. Ce cas ne teste pas les trois implications individuellement actives de C23. C28 n'ajoute pas de mesure au dénominateur C19 et ne modifie pas le verdict H19. Pas de QPU, réseau externe, dépense, publication, push ou message externe.
