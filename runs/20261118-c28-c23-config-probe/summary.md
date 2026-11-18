# C28 — résumé de la tentative de viabilité C23

Date : 18 novembre 2026. Statut du cycle : `complete` (tentative clôturée). Résultat du gate : `blocked`. Le statut `complete` ne signifie pas que la configuration permet une réponse complète ni que l'hypothèse scientifique est confirmée.

## Question et priorité

Après l'échec C25 et l'appel C27 sous une configuration différente, l'utilisateur a autorisé un amendement prospectif : essayer une seule génération initiale sous la configuration C23, sur un cas de développement non-C23, avant tout appel réservé. C28 vérifie cette précondition opérationnelle; il ne teste pas l'hypothèse principale de l'article.

## Protocole, sources et commande

Le protocole et l'amendement sont dans `protocol.md` et `c23-gate-amendment.md`. Le cas `765e3caadee5` est le plus long texte parmi les cinq cas n=7 du jeu C19 désormais utilisé comme développement (653 caractères). Il a été copié exactement dans `case.json`; la sélection et les hashes sont contrôlés par `freeze-v1.json` et `contract-initial-v1.json`. Les seules entrées du modèle sont ce cas et les instructions génériques figées C19. Aucun jeu de cas, annotation ou gold C23 n'est dans le contrat ou les entrées.

Commande exécutée : `python scripts/run_c28_probe.py --execute`, via le runner de provenance borné, watchdog groupe 1800 s, requête 180 s, phase 1650 s. Python 3.11.15, macOS 26.2 arm64, llama.cpp b12359 (`b1b770d90d94cad9e9ea5b993bdbc383a522fb28`), Qwen3-8B-Q4_K_M révision `7c41481f57cb95916b40956ab2f0b139b296d974`. Le commit de départ est `fee83eb4575198e3e142d41c621300b4d11361d8`; l'arbre était déjà modifié. La commande exacte, l'environnement, les entrées, la graine `2686330052` et les empreintes sont dans `initial-v1/manifest.json`, `initial-v1/driver/generation.json` et `freeze-v1.json`.

Configuration demandée : contexte 6144, sortie max 1024, réserve fixe 1024 (entrée max 5119), 30 couches Metal, quatre threads, batch/ubatch 128. Flash Attention n'est pas forcé (`auto`); K/V restent `f16` par défaut. Une requête initiale seulement, sans retry, continuation, solveur ou référence.

## Résultat observé

- Le runner a terminé en 252,597 s avec statut `failed` et code 1 : le résultat HTTP déclaré `http/000.response.json` manque.
- Le driver a `status=partial_error`, `completed=0`, `error="TimeoutError: signal 14: interrupted phase, preserve actual rows"` et `cleanup_error=null`. La limite de la requête était 180 s.
- Le fichier de requête contient 740 tokens. Les logs marquent 640 tokens (86 %) après 126,05 s, puis l'initialisation du sampler pour 740 tokens. Aucune réponse HTTP complète n'a été conservée; `raw.jsonl` est vide.
- Le champ `output_tokens=0` est le compteur de lignes achevées du driver, pas une preuve que le serveur n'a échantillonné aucun token. Le nombre réellement généré mais non transmis est inconnu.
- Le runtime rapporte Metal et 30/37 couches déchargées. Les logs observés sont `flash_attn=auto`, cache K/V `f16` (432 MiB chacun), sans marqueur explicite `MetalInsufficientMemory`/OOM. Cela ne prouve pas une marge mémoire. Le serveur a été reap; son code de sortie `-9` est conservé sans attribuer sa cause.

Le gate exigeait une réponse complète, EOS et acceptée par le parseur. Il échoue donc; C23 n'a reçu aucun appel et aucun retry n'est autorisé par le protocole. Ce résultat n'établit ni impossibilité matérielle générale, ni fidélité ou infidélité mathématique, ni performance de population.

## Vérification, article et suite

`verification-final.json` et `verification.md` donnent l'audit borné et les hashes des preuves. Le premier vérificateur a produit deux faux positifs de diagnostic (chemin C28 pris à tort pour un chemin corpus C23; champ du `--help` lu au mauvais niveau); `verification.json` reste conservé comme sortie préliminaire, et `verification-final.json` le remplace pour l'interprétation. Le constat décisif de blocage est corroboré par le manifeste, le délai, l'absence de réponse/raw et les logs. L'audit a été effectué par l'intégrateur; pas de revue par un agent distinct.

Le manuscrit ajoute uniquement cette limite opérationnelle, séparée des résultats C19. Les dénominateurs C19 et le rejet de H19 restent inchangés. `paper/article.md` et `paper/main.tex` sont régénérés depuis `paper/template-c19.md`; `paper/main.pdf` a été compilé avec le binaire Tectonic épinglé, sans accès réseau, provenance et empreintes dans `research/c28-pdf-build.json`. La compilation vérifie la syntaxe et la mise en page, pas la vérité scientifique ni l'aptitude à soumission. C23 demeure bloqué. Ne pas relancer C28 ni lancer C23; tout nouvel essai exige une nouvelle décision prospective et un protocole révisé. L'autre option est de clore la campagne avec l'article comme document de travail, sans prétention de soumission.
