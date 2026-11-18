# C16 — voie candidate, étude prospective uniquement

Date : 2026-11-15. Aucune génération, modification de prompt, révision de
code C15, installation, compilation ou téléchargement de poids n'a été effectué
par l'auteur de cette étude. Aucun brut du test C15 n'a été consulté.
Après la revue documentaire, l'intégrateur a autorisé le script d'acquisition
C16 séparé décrit en fin de rapport; seuls ses contrôles logiciels synthétiques
sans réseau ont été exécutés par cet auteur.
Le diagnostic de développement communiqué par l'intégrateur est : sept
propositions v2 sur huit gardent des contraintes en listes imbriquées; la
huitième passe le format mais présente 23 désaccords de faisabilité. Il motive
un contrôle du langage de sortie, pas une nouvelle correction du gold.

## Voie prioritaire : llama.cpp Metal, 1.5B quantifié et grammaire

Proposer un C16 distinct avec **llama.cpp + Qwen2.5-1.5B-Instruct Q4_K_M +
GBNF**, batch 1, contexte initialement plafonné à 2048, 384 nouveaux tokens par
appel. Le runtime expose des grammaires contraignant les sorties, dont JSON;
le support Metal est activé par défaut sur macOS. Ce sont des capacités
documentées, pas une compatibilité ou une vitesse mesurée sur cette machine.
[GBNF officiel](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md),
[build Metal v1.0.0](https://github.com/ggml-org/llama.cpp/blob/v1.0.0/docs/build.md).

Version publique examinée initialement : v1.0.0, annoncée par l'API officielle au commit
2d8a32502909ca065c41c4cf5f2fb1c427c047fc. Figer le commit et vérifier les
options effectives avant toute future exécution; les exemples de commandes
sur les pages courantes peuvent évoluer.
[Release primaire](https://github.com/ggml-org/llama.cpp/releases/tag/v1.0.0).

Poids concrets : dépôt officiel Qwen/Qwen2.5-1.5B-Instruct-GGUF, seul fichier
qwen2.5-1.5b-instruct-q4_k_m.gguf, taille annoncée 1.12 GB, SHA-256 public :

    6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e

Ne pas télécharger les 13.3 GB de toutes les variantes. Ce fichier compact
réduit le volume des poids par rapport au GGUF fp16 annoncé à 3.56 GB, mais sa
taille disque n'est pas son pic de RAM : cache KV, buffers, runtime et mémoire
unifiée partagée s'ajoutent. Une machine de 8 GiB déjà sous pression ne devient
pas disponible par ce seul changement. La faisabilité est **plausible, non
démontrée**; aucun nombre de tokens/s ou RSS futur n'est promis.
[Fichier et empreinte officiels](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/blob/main/qwen2.5-1.5b-instruct-q4_k_m.gguf),
[variantes Qwen](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/tree/main).

La grammaire future imposerait les cinq champs, les types, les arités, les
indices de variables autorisés par n et un tableau de chaînes d'expressions
linéaires, excluant les listes imbriquées. Les coefficients signés, les
relations, membres droits, variables présentes dans chaque ligne et le nombre
de lignes restent choisis par le LLM. Elle ne doit lire ni weights/costs, ni
edges, ni budget/cardinalité de référence, ni gold pour remplir une ligne.
Forcer l'ordre des indices est une aide structurelle déclarée : ne pas créditer
ce choix comme une découverte autonome des variables. Le compilateur
algébrique et le certificat fini restent séparés.

Préférer une GBNF explicite et vérifiable à la confiance aveugle dans un
convertisseur JSON Schema : la documentation signale des mots-clés ignorés
silencieusement et des limites sur prefixItems/uniqueItems. La grammaire peut
assurer la syntaxe d'une réponse terminée, jamais sa fidélité aux clauses ni
sa terminaison sous 384 tokens. Une sortie tronquée reste un échec observable.
[Limites documentées](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md).

## État local et option à changement de runtime réduit

Lecture seule des métadonnées du venv LLM :

    Python 3.9.6; arm64; macOS 26.2
    torch 2.8.0; transformers 4.45.2
    jsonschema 4.25.1; pydantic 2.13.1
    packaging 24.1; pyyaml 6.0.3
    lm-format-enforcer/interegular/outlines/guidance/xgrammar : non installés
    mlx/mlx-lm/llama-cpp-python : non installés
    llama-cli et llama-server : aucun chemin renvoyé

Commande de provenance : .venv-local-llm/bin/python -B avec
importlib.metadata.version pour chaque distribution et platform pour
Python/architecture/macOS; aucun module d'inférence n'a été importé.
command -v et sw_vers ont servi aux deux dernières vérifications.

Transformers 4.45.2 expose déjà prefix_allowed_tokens_fn, mais cette interface
ne fournit pas seule un parseur incrémental JSON. jsonschema/Pydantic valident
après génération; ils n'empêchent donc pas le mauvais type de constraints.
Une option de repli serait LM Format Enforcer 0.11.3 dans un environnement
C16 isolé, avec les poids 0.5B déjà présents, pour isoler l'effet du décodage.
Ses métadonnées admettent Python 3.9; son intégration Transformers filtre les
tokens via un parseur JSON Schema. L'installation future d'au moins la
bibliothèque et interegular reste nécessaire; aucune compatibilité de bout en
bout n'est testée ici. Surcoût de masque/tokenizer et scores après masquage
doivent être comptabilisés.
[Transformers 4.45.2](https://huggingface.co/docs/transformers/v4.45.2/en/main_classes/text_generation),
[LMFE intégration](https://github.com/noamgat/lm-format-enforcer),
[LMFE version/dépendances](https://github.com/noamgat/lm-format-enforcer/blob/main/pyproject.toml).

## MLX : alternative crédible, moins directe pour cette première étape

MLX documente Apple Silicon, macOS ≥14 et Python natif ≥3.10. La machine
arm64/macOS 26.2 satisfait ces deux premiers critères; le venv actuel Python
3.9.6 ne satisfait pas le troisième. Le mlx-lm courant exige même Python
≥3.11 et Transformers ≥5.7 : environnement séparé requis. Le checkpoint
mlx-community/Qwen2.5-1.5B-Instruct-4bit annonce model.safetensors à 869 MB.
Il est distinct du GGUF et ne se charge pas en substituant simplement un
chemin dans le driver C15. La présente revue n'établit pas une intégration
de grammaire aussi directe que GBNF dans llama.cpp.
[Installation MLX](https://ml-explore.github.io/mlx/build/html/install.html),
[dépendances mlx-lm](https://github.com/ml-explore/mlx-lm/blob/main/pyproject.toml),
[checkpoint MLX](https://huggingface.co/mlx-community/Qwen2.5-1.5B-Instruct-4bit/tree/main).

## Décision bornée proposée, non exécutée

Après clôture ou arrêt documenté du processus C15 et libération des ressources,
préenregistrer un préflight C16 sur deux cas de développement fixés à l'avance,
un appel chacun, sans retry : 384 tokens, contexte 2048, limite par processus
180 secondes et arrêt si aucun premier token en 60 secondes ou pression mémoire
anormale. Ces limites sont des choix de protocole proposés, pas des résultats.
Ne lancer une matrice nouvelle qu'après validation de disponibilité, schéma,
coût et absence de fuite. Conserver tous les échecs et mesurer préparation de
grammaire, chargement, préfill, décodage, tokens, pic mémoire et pression système.

La comparaison future du décodage libre/contraint doit garder le même runtime,
modèle et budget pour isoler la contrainte; le 1.5B quantifié constitue ensuite
une baseline de capacité distincte, pas une reprise du C14 CPU float16.
Les réponses contraintes de format ne seront créditées comme formulations
correctes qu'après contrôle sémantique indépendant. C15 reste figé; tout
développement ultérieur emploie de nouveaux groupes de test, sans adapter puis
rebaptiser le test C15. Aucun gain de formulation n'est établi à ce stade.

## Acquisition C16 séparée, préparée pour exécution par l'intégrateur

Le choix effectif d'acquisition communiqué ensuite par l'intégrateur est
**b12359**, commit b1b770d90d94cad9e9ea5b993bdbc383a522fb28, archive
llama-b12359-bin-macos-arm64.tar.gz et SHA-256 attendu :

    82b00abc740160e1b9980e6cc79c117345fa34af058c80e6c0a69aa8ddccde75

Ce pin remplace la version candidate examinée initialement pour l'acquisition;
aucune compatibilité ABI entre versions n'est supposée. Le script
scripts/acquire_c16_runtime.py ne lance ni installation ni binaire. L'intégrateur
peut l'exécuter avec un dossier neuf :

    python3 scripts/acquire_c16_runtime.py --output research/external/c16-public

Le script consulte l'API HF publique, exige le SHA LFS Qwen déjà examiné,
fige son commit de dépôt, puis télécharge uniquement l'URL resolve de ce commit.
Les deux téléchargements sont hachés en flux par blocs de 1 MiB. Aucun login,
token, cookie, secret ou proxy d'environnement n'est utilisé. Les redirections
restent HTTPS dans les domaines d'actifs autorisés. Le timeout global est de
1800 secondes; les fichiers partiels et le manifest failed restent visibles
en cas d'échec, sans retry. Un contrôle de disque inclut la taille du modèle,
les plafonds d'archive/extraction et une réserve de 1 GiB.

Tous les membres tar sont validés avant création du dossier d'extraction :
pas de chemin absolu/traversant, doublon normalisé, périphérique, parent fichier,
cycle ou cible externe. L'extraction est manuelle, sans extractall. Les liens
internes vers des fichiers sont matérialisés en copies régulières; aucun lien
symbolique/hardlink n'est créé. Modes limités à 0644/0755, sans setuid/gid ni
restauration de propriétaires ou attributs étendus. Les sorties restent dans
le nouveau dossier du dépôt.

Une sonde logicielle sur de minuscules archives temporaires a vérifié les
copies de liens internes, le retrait du setuid, les refus de traversée, cible
externe, cycle et parent-lien ainsi que les URL non autorisées. Sortie brute :

    {"model_or_runtime_executions":0,"network_requests":0,"software_security_checks":{"cycle_rejected_before_output":true,"internal_link_materialized_without_setuid":true,"link_parent_rejected_before_output":true,"outside_link_rejected_before_output":true,"traversal_rejected_before_output":true,"unsafe_urls_rejected":true}}

Cela vérifie des frontières du code d'acquisition; ce n'est ni l'acquisition
réelle de l'archive b12359 ni une mesure de compatibilité ou de performance.

Mise à jour après exécution explicite par l'intégrateur : le manifest
runs/20261115-c16-quantized-repair/acquisition.json enregistre completed,
18.701141708 secondes, archive de 16907811 octets et GGUF de 1117320736 octets,
avec les deux SHA attendus observés. Commit modèle figé :
91cad51170dc346986eccefdc2dd33a9da36ead9. Le contrôle séparé
acquisition-source-check.json constate la même empreinte du script avant/après.
Ces métadonnées ont été lues par l'auteur du script; il n'a ni rejoué le
téléchargement ni exécuté le modèle. Le manifest conserve model_execution=false.
