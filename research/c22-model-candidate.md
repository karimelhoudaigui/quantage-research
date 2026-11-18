# C22 — candidat officiel 8B, métadonnées seules

Contrôle du 15 novembre 2026. Le dépôt officiel **Qwen/Qwen3-8B-GGUF** fournit un candidat **Q4_K_M**; aucun Q3 ne figure dans son inventaire à la révision consultée. Cela identifie une route de capacité, sans établir qu'elle tiendra sur8GiB ou résoudra l'erreur d'implication. Aucune acquisition de poids, exécution, installation ou suppression de cache n'a été effectuée.

## Fichier précisément identifié

| Champ | Valeur vérifiée dans les métadonnées distantes |
|---|---|
| Dépôt | Qwen/Qwen3-8B-GGUF, organisation officielle Qwen |
| Commit | `7c41481f57cb95916b40956ab2f0b139b296d974` |
| Fichier le plus petit | `Qwen3-8B-Q4_K_M.gguf` |
| Taille exacte | **5 027 783 488 octets**, soit4,682488GiB |
| SHA256 LFS du contenu distant | `d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785` |
| Licence déclarée | Apache-2.0 |

L'[API officielle](https://huggingface.co/api/models/Qwen/Qwen3-8B-GGUF?blobs=true) donne commit, tailles et hashes. La [page du fichier au commit figé](https://huggingface.co/Qwen/Qwen3-8B-GGUF/blob/7c41481f57cb95916b40956ab2f0b139b296d974/Qwen3-8B-Q4_K_M.gguf) confirme son SHA. L'inventaire complet est Q4_K_M, Q5_0, Q5_K_M, Q6_K et Q8_0 : « aucun Q3 » est limité à ce dépôt et ce commit. Le hash est rapporté par le dépôt, **pas mesuré sur un téléchargement local**. LICENSE est présent; ses octets n'ont pas pu être lus par le navigateur. La licence ci-dessus est la déclaration des métadonnées, sans interprétation juridique.

## Mode non-thinking et intégration

La [carte originale Qwen3-8B, commit b968826d9c46dd6066d109eabc6255188de91218](https://huggingface.co/Qwen/Qwen3-8B/blob/b968826d9c46dd6066d109eabc6255188de91218/README.md) décrit un modèle **hybride**8,2B,36couches, contexte natif32768. Le hard switch du template est `enable_thinking=False`; thinking est activé par défaut. `/no_think` est un mécanisme distinct. Les paramètres conseillés pour non-thinking sont **T0,7, top-p0,8, top-k20, min-p0**. Ce checkpoint n'est pas une version native non-thinking-only de l'Instruct-2507 employé précédemment.

Le [guide officiel Qwen llama.cpp](https://qwen.readthedocs.io/en/latest/run_locally/llama.cpp.html), version flottante lue aujourd'hui, documente les GGUF officiels, AppleSilicon et le serveur. Il mentionne encore un template personnalisé pour le hard switch. Ce passage ne vérifie pas le comportement exact de b12359. Il faudra contrôler prospectivement le template réellement embarqué et le prompt non-thinking fermé dans le runtime épinglé; aucune compatibilité précise n'est inférée de cette seule page. Les commandes d'installation présentes sur les sites n'ont pas été exécutées.

## Ce qui reste à établir

4,682488GiB est une **taille disque**, pas une mesure de RAM résidente ou Metal. KV cache, buffers, serveur/Python et macOS partagent la mémoire; chargement, réserve disque et latence restent non mesurés. Aucun fit4096tokens/8GiB, offload complet ou absence de swap n'est promis.

Pour un cycle ultérieur autorisé, le cas de développement417127d82203 permettrait de sonder l'orientation des implications avec les mêmes initiales, outil candidat, gloss, limites1024tokens/768ASCII, contexte4096 et sampler que C21. Figer le protocole avant acquisition/inférence. Deux probes déjà observées ne deviennent pas un test réservé. Même en tenant ces réglages constants, passer de4BInstruct-2507 à8Bhybride change aussi la variante et l'entraînement : aucun effet causal isolé de taille, généralisation ou nouveauté n'en découlerait.

Le [JSON compagnon](c22-model-candidate.json) conserve inventaire complet, versions, URLs, passages lus, restrictions et échecs d'accès. Trois sources primaires logiques seulement : dépôt GGUF officiel, carte/métadonnées du modèle original et guide Qwen llama.cpp; leurs représentations API/pointeur appartiennent aux mêmes dépôts. Aucun article, state, claims ou fichier source n'a été modifié.
