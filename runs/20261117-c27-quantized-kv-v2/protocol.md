# C27 — premier appel réel après correction de l'observation Flash Attention

## Question et priorité

C27 reprend le pilote de capacité C26, priorité active du backlog : vérifier si le Qwen3-8B-Q4_K_M acquis peut atteindre une génération locale dans la configuration mémoire visée, avant de décider si l'expérience réservée C23 est praticable. Cette question est opérationnelle et ne constitue pas le résultat scientifique principal de l'article.

C26 n'a envoyé aucune requête de génération. Le serveur a démarré, a chargé les 37/37 couches signalées sur Metal, a rapporté les caches K/V `q8_0` et `flash_attn = enabled`, puis le driver s'est arrêté parce que son détecteur ne reconnaissait pas cette forme de log. Le détail reste dans `runs/20261116-c26-quantized-kv/`. C27 corrige uniquement la reconnaissance de cette preuve et la validation préalable des sources ; un seul nouvel appel est autorisé. Il n'y a donc ni réponse C26 à réessayer ni résultat de génération à imputer.

## Protocole gelé

- Cas et état : exactement le cas de développement C24, état composé des réponses réellement enregistrées, sans rééchantillonnage.
- Modèle et runtime : même GGUF officiel Qwen3-8B-Q4_K_M et llama.cpp b12359, hashes acquis vérifiés.
- Configuration : contexte 6144, sortie au plus 1024 tokens, entrée au plus 5119, batch/ubatch 128, placement GPU demandé 99 couches sur `MTL0`, quatre threads CPU, Flash Attention `on`, cache K et V `q8_0`.
- Prompt, feedback, grammaire et graine : inchangés par rapport au protocole C26 ; aucune donnée de référence ou gold à l'inférence.
- Appels : un appel guidé maximum ; pas de retry, de continuation ni de seconde génération.
- Délais : 180 s par requête, 420 s phase, 480 s groupe externe ; terminaison TERM puis KILL/reap bornés.
- Réseau : serveur détenu localement, lié à loopback et `--offline`; aucune dépense, soumission QPU, publication, push ou message externe.

Avant le gel C27, le wrapper vérifie les empreintes des entrées C24 contre le gel C24 original et contrôle la présence de tous les artefacts requis. Le driver reconnaît les lignes réellement émises `flash_attn = enabled|disabled` et les formats K/V du cache. La version antérieure de C26 demeure intacte.

## Analyse et interprétation

En cas de réponse complète, conserver les octets et métadonnées effectivement retournés, rejouer les états littéraux, énumérer les affectations du cas, puis exécuter les deux solveurs prévus. En absence de réponse complète, consigner seulement les observations et l'échec réel. Dans les deux cas, C27 est un pilote de développement sur un seul cas et ne répond ni à H19 ni à la généralisation C23.

Même si le serveur démarre, cela ne garantit pas la mémoire disponible pendant le prefill ou la génération. Une configuration réussie ne valide pas l'avantage du cache quantifié : plusieurs paramètres évoluent par rapport à C24/C25 et le cas n'est pas comparatif.
