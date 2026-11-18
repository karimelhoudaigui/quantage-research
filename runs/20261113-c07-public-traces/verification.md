# C07 — acquisition vérifiée, pas résultat de benchmark

Modèle : neuf fichiers à révision fixe, tailles et SHA-256 vérifiés durant le
téléchargement; hash des poids égal au LFS primaire. Format Safetensors,
trust_remote_code=False, local_files_only=True, HF_HOME propre au projet,
HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE et token implicite désactivé pour inférence.
Les métadonnées indiquent modèle non gated, licence Apache-2.0.

Le smoke test C07 n'a reçu que la demande de JSON ready=true : réponse réelle
{"ready":true}, six tokens générés. Python3.9.6, torch 2.8.0, Transformers 4.45.2,
CPU float32, quatre threads. Temps de chargement6.3357925s et génération0.936010625s
observés; ces mesures ne sont ni performance scientifique ni capacité générale.
Le benchmark C08 est préenregistré séparément et ne réutilise pas ce texte
comme cas d'examen.

Archives :12 fichiers,554646octets acquis, commit et hash par fichier. Les
contrôles archive-inspection.json/archive-joins.json établissent les comptes,
liaisons et contenu non vide; pas d'exécution des codes. Sources réellement
consultées et licences dans sources.md/public-acquisition.json.

Revue d'acquisition par l'intégrateur; pas d'agent indépendant nouveau à cause
du quota. Les rapports et labels indépendants C05/C06 sont réutilisés, leurs
fichiers restent inchangés. Les dépenses externes et soumissions QPU sont zéro;
coût CPU, stockage et énergie non chiffré. Aucun secret lu ou copié.
