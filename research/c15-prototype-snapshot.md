# C15 — snapshot du prototype historique v2

Le manifest historique `research/c15-code-audit-v2/manifest.json` est valide avec
la racine isolée `research/c15-code-audit-v2/source-snapshot`. Les sept entrées
épinglées et les trois sorties conservées correspondent exactement à leurs
SHA-256 historiques. Cette opération restaure la provenance de cet audit avant
gel ; elle ne réexécute ni l'expérience scientifique ni une inférence LLM.

Le module historique `quantage/repair_model.py` a été reconstruit dans le
snapshot à partir du cœur courant inchangé et du patch textuel fourni par
l'intégrateur : insertion de `validate_feedback` entre `objective_value` et
`model_feasible`, branche historique `schema` avec les seuls champs `kind` et
`detail` (chaîne de longueur au plus 400), puis conservation des optima de la
référence et du modèle dans `verify_model`. Ses octets n'ont été retenus
qu'après correspondance exacte avec l'empreinte déjà enregistrée :

`d929c7b14cc8a67154c74d54c586a084950b1abb5ece0b1def1ed933d5bf498c`.

Le script d'audit courant a été restauré au prototype v1 pendant cette mission.
Le script historique v2, archivé séparément par l'auditeur dans
`research/c15-code-audit-source-v2.py`, a donc été copié sous son chemin attendu
`research/c15-code-audit.py` dans le snapshot. Son empreinte correspond exactement
à celle du manifest v2 :

`d4ef992bc18e456789c46b611c8c6964e7b4a89c27ee84581514b50ee4072953`.

Les autres entrées et sorties ont été copiées octet pour octet sous les mêmes
chemins relatifs : oracle indépendant, deux corpus publics, annotations du
relecteur, solveurs, résultat brut et deux logs. Le manifest original est aussi
copié sans modification à son chemin relatif. Le package contient les modules
nécessaires à cet audit et une copie de `quantage/__init__.py` telle qu'observée
lors de la construction du snapshot. Ce dernier fichier supplémentaire n'était
pas épinglé par le manifest historique ; cette limite est déclarée séparément.

La commande effectivement exécutée à la racine du workspace est :

```sh
python3 /Users/karimelhoudaigui/.codex/plugins/cache/openai-curated-remote/mathbox/4.0.0/skills/computation-audit/scripts/validate_manifest.py research/c15-code-audit-v2/manifest.json --root research/c15-code-audit-v2/source-snapshot
```

Elle a terminé avec le code 0 et le message :

```text
valid evidence record (run status: completed); mathematical interpretation requires review
```

Les chemins, origines et empreintes des douze copies sont enregistrés dans
`source-snapshot/snapshot-provenance.json` ; la commande et sa sortie observée
figurent dans `source-snapshot/manifest-validation.json`. Aucun manifest
historique, résultat original, corpus figé ou module courant n'a été modifié
par ce rôle. Le cœur courant est resté à l'empreinte
`e022473093267ca7d32fa52bd21a75618fc4cec3888479d655ef4cbcec5a0745`.

La correspondance des empreintes authentifie les octets attendus par ce manifest,
sans reconstruire une observation d'exécution manquante : le statut `completed`
reste celui du calcul historique enregistré. Les bibliothèques Python externes
ne sont pas vendues dans le snapshot ; leurs versions historiques restent celles
du manifest. La validation des fichiers ne démontre aucune performance de
réparation, de routage, de compréhension ou d'avantage quantique.

Le rôle de provenance est distinct de l'auteur du prototype mais a précédemment
conçu le corpus C15 ; il ne revendique donc aucune nouvelle revue aveugle des
intentions, des annotations ou des résultats scientifiques. Aucun résultat de
génération LLM n'a été consulté pour cette restauration. Aucun échec de quota
n'a été rencontré. Procédure utilisée : skill `mathbox:computation-audit` pour
la validation de provenance avec racine explicite.
