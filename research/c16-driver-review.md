# C16 — driver llama.cpp, préparation statique

`quantage/repair_llama_inference.py` implémente les phases initial/direct/self/guided
avec un serveur local possédé par le driver. Aucun binaire ML, GGUF ou serveur
d'inférence n'a été exécuté par ce rôle. La disponibilité réelle de l'API et la
grammaire compilée restent à confirmer par le préflight autorisé de l'intégrateur.

Le driver lit exclusivement les cas publics, les instructions, les métadonnées
d'acquisition, les premières réponses pour self/guided et le feedback minimal
pour guided. Aucun argument gold ou modèle canonique n'existe. Les propositions
sont analysées par `parse_proposal`, jamais exécutées. Le schéma JSON est constant :
exactement cinq champs, listes d'entiers pour variables/objective, liste de chaînes
pour constraints, valeurs de format binary_ilp/max. Il ne spécifie ni longueur n,
ni indices attendus, ni coefficient, borne ou clause issue d'une instance.

## API primaire vérifiée

Lecture au tag officiel **b12359** : `/completion`, `/tokenize`, `return_tokens`,
`json_schema`, chaîne explicite top_k/top_p/temperature, et `post_sampling_probs`
dans le [README du serveur](https://raw.githubusercontent.com/ggml-org/llama.cpp/b12359/tools/server/README.md).
La chaîne demandée utilise T=0.2, top-k=50, top-p=1, sans pénalités ni cache.

La lecture de `populate_token_probs` confirme que la probabilité du token choisi
est recherchée dans tous les candidats après sampling, indépendamment du nombre
de meilleures alternatives demandé. Le chemin spéculatif annonce ne pas supporter
ce mode : aucune spéculation n'est admise ici.
[Source primaire](https://raw.githubusercontent.com/ggml-org/llama.cpp/b12359/tools/server/server-context.cpp).

La sérialisation non-OAI produit `completion_probabilities` et, avec le mode
post-sampling, les champs `id`, `prob`, `top_probs`. Le driver prend log(prob)
du token choisi, sans remplacer une valeur absente par le meilleur token ou
une probabilité avant traitement. Il exige des IDs alignés et des comptes exacts,
EOS rapporté compris. [Source primaire](https://raw.githubusercontent.com/ggml-org/llama.cpp/b12359/tools/server/server-task.cpp).
Le champ `speculative.types` est une chaîne séparée par virgules dans ce tag,
ce qui est pris en charge explicitement.
[Source primaire](https://raw.githubusercontent.com/ggml-org/llama.cpp/b12359/common/speculative.cpp).

Le prompt suit le template textuel ChatML Qwen pour system/user/assistant et
ajoute le préfixe assistant. Les chaînes et leur SHA-256 sont conservés ; les
IDs proviennent de `/tokenize` avec analyse des tokens spéciaux, puis sont envoyés
directement à `/completion` pour éviter un second ajout implicite de BOS.
La branche sans outils du [tokenizer officiel Qwen](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/raw/main/tokenizer_config.json)
a été consultée ; cette page de référence n'est pas présentée comme une nouvelle
révision épinglée du GGUF. Le GGUF acquis possède son identité distincte.

## Bornes et provenance

Avant lancement, `acquisition_pins` vérifie le statut completed et le tag b12359,
les empreintes de tous les fichiers extraits du runtime, puis le GGUF téléchargé.
Le binaire et le modèle doivent être les fichiers désignés par l'acquisition.
Les empreintes, la révision GGUF et le commit runtime sont consignés. Le contrôle
réel de ces fichiers sera effectué au lancement ; les tests de ce rôle utilisent
uniquement des fichiers artificiels.

Le serveur se lie à 127.0.0.1, CPU quatre threads, contexte 2048, une session,
sans UI/outils, téléchargement, GPU, cache de prompt ou context shifting.
Le client désactive proxy et redirections. Limites : 384 nouveaux tokens,
180 secondes par requête HTTP, deadline POSIX de phase 1650 secondes, watchdog
du serveur 1800 secondes. Le serveur hérite du groupe du processus appelant :
le runner externe doit imposer lui aussi 1800 secondes au groupe complet.
Le prompt doit réserver les 384 tokens de sortie et une position de garde dans
le contexte ; aucune troncature silencieuse n'est admise.

Une phase exige un répertoire de sortie inexistant et refuse tout écrasement.
Si le runner crée le répertoire parent pour ses logs, utiliser par exemple
`--output <répertoire-du-runner>/driver`. La commande CLI doit inclure
`--execute` après l'autorisation de lancement. Pour le préflight prospectif,
`--case-limit 2` sélectionne les deux premiers IDs triés avant toute réponse.

Les lignes conservent messages, seed, hash du prompt, parse v2, IDs, log-probabilités,
arrêt, tokens et temps. Elles passent `repair_study_v2.indexed` dans la fixture.
Les seed initiales sont distinctes des secondes phases ; les trois secondes
utilisent la même seed. La valeur réservée 0xffffffff est rejetée explicitement.

Le CPU par ligne mesure seulement le client Python ; le CPU total du serveur
est mesuré après son arrêt et enregistré une seule fois dans generation.json.
Les temps de chargement, requêtes et processus sont distingués. Additionner le
seul CPU des lignes ne constitue donc pas le coût CPU d'inférence. Les réponses
HTTP originales sont conservées même si leur validation échoue. Une erreur,
un timeout ou SIGTERM préserve les lignes déjà flushées et leur nombre réel ;
aucune ligne absente n'est fabriquée.

## Validation effectuée et limites

Commande exécutée :

```sh
python3 -B -m unittest discover -s tests -p test_repair_llama_inference.py -q
```

**13 tests passent**, exclusivement sur échanges HTTP simulés en mémoire : forme
du prompt et du schéma, phases, absence de lecture initiale en direct, feedback
fermé, probabilités choisies, EOS, rejets de comptes incohérents, cap de contexte,
digests modifiés, conservation de partiels, refus d'écrasement, arrêt/kill du
processus simulé et sélection du préflight. Une première variante des fixtures
a tenté de lier un serveur HTTP factice ; le sandbox a refusé bind avec EPERM.
Les fixtures ont ensuite été remplacées par une simulation sans socket. Cette
réussite ne valide ni une communication TCP réelle ni un résultat LLM.

Le préflight devra confirmer le lancement du binaire acquis, l'application du
schéma et l'alignement de tous les tokens/probabilités sur les sorties réelles.
Les séquences UTF-8 incomplètes, sorties sans scores ou comptes dépassant le cap
provoqueront un arrêt explicite, pas un score de baseline inventé. Le passage
en génération réelle peut nécessiter le contexte d'exécution autorisant bind
local, contrairement au sandbox utilisé pour ces tests.

Aucun changement du corpus, des prompts C16, du protocole, de l'article, des
claims, de l'état ou du comparatif C15 n'a été réalisé par ce rôle. La seule
compatibilité démontrée est logicielle sur fixtures ; aucune performance de
réparation, vitesse, consommation mémoire ou avantage scientifique n'est établie.
