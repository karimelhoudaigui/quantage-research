# C28 — vérification

## Vérifications d'intégrité

`python scripts/audit_c28_probe.py` réanalyse localement le gel, le contrat, le manifeste externe, la requête HTTP, la génération et le stderr. Aucun modèle, réseau, corpus C23 ni gold n'est chargé par l'audit. Les sources gelées et le hash du contrat concordent; le cas correspond exactement au cas n=7 déterminé depuis l'ancien jeu C19 de développement. Les entrées contractuelles ne contiennent aucun fichier du corpus ou gold C23.

Le binaire et le modèle correspondent aux acquisitions épinglées. La commande observée demande les 30 couches, le périphérique MTL0, quatre threads et batch/ubatch 128, sans remplacer les options par défaut. L'aide locale b12359 et les logs réels concordent sur Flash Attention `auto` et K/V `f16`. Les logs confirment 30/37 couches sur Metal.

## Résultat du critère préenregistré

Le critère n'est pas atteint : après la limite de requête 180 s, le driver a enregistré `partial_error`, zéro ligne achevée et aucune réponse HTTP complète; le runner signale `http/000.response.json` manquant. `raw.jsonl` est vide, donc aucune analyse de schéma ou de fidélité n'est possible. Le serveur affiche un prompt de 740 tokens, une progression jusqu'à 640 tokens à 126,05 s et l'initialisation du sampler; la quantité de sortie réellement générée est inconnue. Le serveur est reap, code `-9`, sans `cleanup_error`. Aucun marqueur explicite d'OOM n'a été trouvé; cela ne certifie pas la mémoire disponible.

**Décision :** cycle C28 terminé; gate de capacité bloqué; C23 non lancé; aucun retry.

`verification-final.json` est le rapport correctif autoritatif. Le premier script `verify_c28_probe.py` avait deux erreurs de diagnostic, documentées dans le rapport; `verification.json` est conservé comme sortie préliminaire. L'audit final et la préparation du protocole ont été faits par le même intégrateur; la revue n'est pas indépendante.
