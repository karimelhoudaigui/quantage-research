# C15 — provenance restaurée du prototype historique du scorer

Le contenu historique de `quantage/repair_study.py` a été reconstruit exactement
dans `research/c15-study-audit/source-snapshot/`. Il correspond au SHA-256 déjà
épinglé par le manifest du calcul original, sans modification de ce manifest :

`753f27af0e6a7c332b05b72b1b31b30712b5dbb67b632e11cc67d5d870d0e7e9`
(10 930 octets).

Le fichier courant utilisé comme point de départ, resté inchangé, avait le
SHA-256 `eced021e8899e4298ea6f771c533ba6bbfb50ec4f096b74e6367f8c6fefe92ac`.
Le premier candidat obtenu par retrait des ajouts identifiables a correspondu
à l'empreinte historique ; aucun candidat sans correspondance n'a été retenu.
La recherche, commencée le 15 novembre 2026 à 13:09:57 UTC, s'est achevée dans
la borne de vingt minutes autorisée.

La reconstruction s'appuie sur le script de fixtures indépendant
`research/c15-study-audit.py`, dont l'empreinte est restée identique à celle du
manifest, le rapport `research/c15-study-review.md`, et la source courante.
Le rapport historique décrit notamment les validations encore absentes et
la portée initiale de la comptabilité. Les retraits concernent les contrôles
de phase/tokens/messages, les contrôles supplémentaires d'annotations/familles,
l'argument `feedback_reports` et les champs de coûts étendus. La différence
textuelle complète est conservée dans `source-snapshot/current-to-historical.patch`.
Cette description n'est pas le critère d'authentification : seule la concordance
exacte avec le SHA-256 préexistant a permis de retenir les octets.

Les cinq entrées épinglées et les sept sorties du manifest ont été copiées
sous les mêmes chemins relatifs dans le snapshot ; toutes correspondent à
leurs empreintes originales, y compris `sha256_after` pour les entrées. Les
sorties sont celles de fixtures artificielles explicitement identifiées comme
tests logiciels, pas des réponses LLM réelles. Le manifest original lui-même
est copié octet pour octet. Le package contient aussi `quantage/__init__.py`
tel qu'observé lors de cette restauration ; ce fichier supplémentaire n'était
pas épinglé par le manifest historique, ce qui reste une limite déclarée.

Commande effectivement exécutée depuis la racine du workspace :

```sh
python3 /Users/karimelhoudaigui/.codex/plugins/cache/openai-curated-remote/mathbox/4.0.0/skills/computation-audit/scripts/validate_manifest.py research/c15-study-audit/manifest.json --root research/c15-study-audit/source-snapshot
```

Code de sortie observé : **0**. Sortie :

```text
valid evidence record (run status: completed); mathematical interpretation requires review
```

`source-snapshot/snapshot-provenance.json` conserve les origines et empreintes ;
`source-snapshot/manifest-validation.json` conserve la commande et son résultat
observé. La validation vérifie les fichiers attendus sous une racine alternative.
Elle ne réexécute pas la commande scientifique du manifest et ne crée aucune
nouvelle observation d'exécution, de temps ou de coût. Le statut `completed`
est celui du calcul historique, daté du 14 novembre 2026 à 23:22:58 UTC.

Ce prototype V1 a été remplacé dans le dispositif actif par les sources et
l'audit distincts `research/c15-study-audit-v2/`. La présente restauration
n'étend pas l'audit V1 à ces sources V2 et n'en modifie aucune preuve. Elle
permet seulement d'authentifier à nouveau les octets du prototype auxquels
le premier calcul se référait. Le manifest V1 ne doit pas être présenté comme
une validation du fichier courant modifié.

Aucun manifest, run original, source courante, corpus figé, article, claim ou
état de recherche n'a été modifié par ce rôle. Aucun brut de test LLM n'a été
lu ; aucune inférence ni exécution de l'audit scientifique n'a été lancée.
Les bibliothèques externes ne sont pas incluses dans le snapshot ; les versions
enregistrées dans le manifest restent des observations historiques. Aucun
résultat de performance ou de H15 n'est déduit de cette restauration.
