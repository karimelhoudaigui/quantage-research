# C20 — notes d'implémentation et vérification statique

15 novembre 2026. Candidat prêt pour revue root; **aucune génération C20, aucun démarrage de serveur, aucun chargement GPU**. Les seules écritures persistantes de ce lot sont les deux nouveaux modules et les quatre fichiers de ce répertoire. Les sources et données C19 restent inchangées.

## Contrat des éditions

`parse_patch(raw, n, initial_raw)` ne reçoit aucun chemin, donnée du problème, label ou référence. Il importe seulement le compilateur de chaînes linéaires et les utilitaires de schéma existants. Le modèle de base provient du JSON réellement écrit par le LLM initial, avec son ordre original de contraintes. Ni ses clauses ni ses coefficients ne sont reconstruits depuis les poids, coûts, arêtes ou intentions.

La sortie brute contient exactement `diagnosis` et `edits`. Le diagnostic accepte 0..256 caractères ASCII imprimables; des guillemets/backslashes peuvent être échappés en JSON. Il n'a aucun effet sémantique. Une preuve de compréhension ou de justification n'est pas déduite de son texte. Les six opérations utilisent les objets documentés dans instructions.txt. Les listes comportent au plus 32 opérations et chaque liste intermédiaire de contraintes au plus 32 lignes. Les indices 0..31 portent sur la **liste courante**; une suppression décale donc les suivants. Les variables sont génériquement bornées à 0..7, les vecteurs à huit entrées et les entiers finaux en valeur absolue à 10000; le schéma final doit aussi respecter n et son ordre d'indices.

Un ajout/replacement de ligne doit fournir une chaîne linéaire complète. Les coefficients et relations sont conservés par normalisation, sans réparation sémantique. `set_objective` reste autorisé, sans comparaison aux poids du problème : le mécanisme n'immunise pas artificiellement les régressions. `set_variables` peut réparer une liste mal formée. `replace_model` doit fournir explicitement les cinq champs complets avec des lignes chaînes valides; il est aussi la seule manière de démarrer si la base ne peut pas être décodée comme objet à cinq champs. Aucune base vide, coefficient par défaut ou formulation canonique n'est synthétisé.

Application atomique : chaque opération est appliquée à une copie locale; au premier échec, `valid=false` et aucun `model`/`authored_model` matérialisé n'est renvoyé. Le patch écrit par le modèle et son erreur sont conservés. Un patch vide peut être valide et laisser une initiale mathématiquement erronée inchangée. L'appliqueur n'utilise pas l'oracle pour le détecter.

## Driver copié et provenance des historiques

`quantage/repair_patch_inference.py` copie le driver linéaire courant au SHA `27da08e8c072ae711aaf8451e761ed91bea0bec421974626241503e74b4195be`. Le fichier original conserve exactement ce SHA après le travail. Une comparaison AST des définitions montre 19 fonctions/classes identiques; seules `run_phase` et `main` ont un corps modifié. Les autres changements sont imports, constantes de phases/grammaire, consignes de suivi et métadonnées. Pas de modification des fonctions d'acquisition, de requêtes, du sampler, des bornes, du serveur, des signaux ou du nettoyage de processus.

Les seules phases admises sont self/guided. `--initial` et `--initial-instructions` sont obligatoires; les anciennes consignes C19 authentifient l'historique conservé. Le nouveau système C20 accompagne la réponse initiale historique et la demande d'édition. Ce changement de contexte est explicite dans les consignes et n'est pas présenté comme une initiale générée sous C20. Le hash du texte initial apparaît dans la ligne et dans le résultat de parse_patch; le fichier des anciennes consignes est inclus dans les hashes d'entrée.

Les lignes conservent les champs messages/raw_response/parsed/tokens/seed/temps habituels, mais `raw_response` est désormais **un patch**. `parsed.model` est le modèle dense littéralement matérialisé; `parsed.authored_model` conserve le modèle complet avant normalisation, et `parsed.authored_patch` les opérations écrites. Le champ `response_format=diagnosis_and_literal_edits`, la version de `patch_interpretation`, les fichiers patch-schema.json/patch-grammar.gbnf et leurs hashes distinguent cette interprétation. Le diagnostic ne doit pas être scoré comme certificat.

**Incompatibilité volontaire à gérer dans le runner root :** `repair_study_c19.indexed` reparsait chaque raw_response comme modèle complet. Il rejettera les nouvelles lignes si réutilisé tel quel. L'évaluation C20 doit reconstruire `parse_patch(raw_response,n,initial_raw)` et comparer exactement les données parsed conservées avant d'évaluer ce modèle avec l'oracle séparé. Ne pas substituer silencieusement une version complète dans raw_response ni utiliser les scores de l'auteur pour appliquer les éditions.

## Vérifications effectuées, sans ML

Python 3.9.6, `python3 -B`; aucune installation. Cinq méthodes de test unittest en mémoire passent en 0,015 s, avec des sous-cas multiples :

1. Les six opérations, ordre séquentiel après suppression, objectif effectivement modifiable et absence de mutation de la base.
2. Patch vide, base JSON inutilisable, récupération explicite par replace_model et réparation explicite de variables invalides.
3. Rejet atomique après une première édition valide : opération inconnue, clé supplémentaire, index booléen/négatif/hors liste, variable hors n, produit non linéaire, coefficient10001, objectif booléen/hors borne, variables dans le mauvais ordre, plus de32opérations ou dépassement32lignes.
4. Diagnostic256 accepté,257 rejeté; Unicode non ASCII, retour de ligne et clés JSON dupliquées rejetés.
5. Fixture HTTP des deux phases : faux fichier GGUF et faux binaire **non exécutables**, acquisition synthétique hachée, opener urllib injecté pour apply-template/tokenize/completion, Popen interdit par mock. Deux réponses de fixture sont appliquées, anciennes consignes authentifiées, nouveau système et ancienne réponse conservés, métadonnées patch et coûts présents, stop appelé. Réutilisation de destination et phase initial interdites. La réserve disque est mockée pour isoler le test logiciel. Ces deux réponses ne sont pas des générations LLM et n'ont aucun score scientifique.

Les deux nouveaux modules compilent via `compile(source,filename,'exec')` sans créer de bytecode. `python3 -B -m quantage.repair_patch_inference --help` confirme les deux phases et les arguments obligatoires sans démarrer de serveur. Les deux probes sont structurellement identiques aux objets publics C19 correspondants.

Une vérification courte reproductible de l'appliqueur est possible sans modèle :

~~~python
import json
from quantage.repair_patch_language import parse_patch
base = {"formulation":"binary_ilp", "variables":[0,1], "sense":"max",
        "objective":[3,2], "constraints":["x0+x1<=1", "x0>=0"]}
patch = {"diagnosis":"Software fixture only.", "edits":[
    {"op":"add_constraint", "row":"x1==0"},
    {"op":"replace_constraint", "index":0, "row":"x0+x1<=2"},
    {"op":"delete_constraint", "index":1},
    {"op":"set_objective", "values":[9,8]}]}
r = parse_patch(json.dumps(patch), 2, json.dumps(base))
assert r["valid"] and r["model"]["objective"] == [9,8]
assert r["authored_model"]["constraints"] == ["x0+x1<=2", "x1==0"]
patch["edits"].append({"op":"delete_constraint", "index":31})
r = parse_patch(json.dumps(patch), 2, json.dumps(base))
assert not r["valid"] and "model" not in r
~~~

La grammaire GBNF n'a **pas** été chargée par un exécutable llama dans ce lot. Sa validation par le runtime épinglé et la revue root restent nécessaires avant une génération; aucun résultat de fit mémoire ou de succès LLM C20 n'est annoncé.

## Hashes des entrées et du candidat

| Fichier | SHA256 |
|---|---|
| quantage/repair_patch_language.py | 69b2010c28b56f56e4d8b9c4d34445ac887f9edd5544dccef6fd51e6e8b9e4ab |
| quantage/repair_patch_inference.py | 5e8afddfe5d366168757f2a62ecc624bcd141297561616eded882eb97a51946e |
| protocol.md | fcaa04cc0337797220224a2816313f53d0c4e89776540da0812e42349ee5b60d |
| probe_cases.json | 8fd6bce09815dbd72d0f1d4c863c4ca562e7d78a34ccbd859daa13bd87d157f3 |
| instructions.txt | 91c312b1c9116fbe685d7061e5fc5e8778b9c8c585d4722f9b90fb1ee675ac07 |
| C19/test_cases.json source | 742301bb909289baaf1f34f328032851aa1ca8b935ede5b34e4081aa903d223b |
| C19/test-initial-v2/driver/raw.jsonl | 3015269fb4eaed4f50d3eefa5da8c046ffd4872ad509a0109be80eb2228b86e3 |
| C19/test-feedback-v2/minimal.json | 7162bddf83622498e08638019e45c21ef1d81d350f2731c584f80720e8e32e9a |
| C19/instructions.frozen.txt | 8281e49d29eeb992240e50b8929cbf70c7ae0c4ede698ef2d3f231bd84d176a0 |

Ces SHA identifient le candidat remis à la revue, avant toute exécution C20. Si la revue demande une correction, root devra actualiser le gel et les hashes avant les deux appels autorisés. Aucun changement article/state/claims, aucune publication, aucun QPU ni test futur produit.
