# Sources et décisions d'acquisition C07

Consultation le 13 novembre 2026 via recherche web et connecteur GitHub en
lecture, puis acquisition publique à commits/révisions fixes. Pas de compte
d'inférence, de token, d'achat ou de code externe exécuté.

| Ressource primaire | Observation réelle | Décision |
|---|---|---|
| https://github.com/teshnizi/OptiMUS | MIT; dépôt principal consulté, data/rag, pas de jeu de réponses candidat identifié dans la surface examinée | Littérature réutilisée, pas prétendu corpus de traces |
| https://github.com/antgroup/LLMOPT | Ressources de modèle/données/entraînement; licence globale non identifiée dans métadonnées, LEGAL.md présent | Pas réutilisé comme sorties expérimentales authentifiées |
| https://github.com/QuantBlockchain/quantum-circuit-vision | Dataset MIT et répertoire de 792 fichiers bruts visibles; trois traces RX/RY/RZ et documents/licence réellement téléchargés | Conserver comme données inertes; pas exécuter le code généré |
| https://github.com/Elias-Abebe-Gasparini/PQID-Bench | Licences par périmètre; requêtes/réponses canoniques publiées | Sous-archive Qwen2.5-Coder-7B acquise : 70 enregistrements, 51 codes non vides, 19 sans code; limites de provenance conservées |
| https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct | Modèle Apache-2.0 non gated; checkpoint Safetensors et configuration publics | Moteur local, révision7ae557604adf67be50417f59c2c2f167def9a775, hashes vérifiés |
| https://huggingface.co/docs/transformers/model_doc/qwen2 | Support Qwen2 dans Transformers, chat template et génération documentés | Versions isolées fixées, import local sans code distant |

Les commits GitHub complets, sources exactes et SHA-256 de chaque fichier sont
dans public-acquisition.json. Les licences d'origine sont jointes aux fichiers.
QCV annonce ses identités de modèles dans noms de fichiers et traces CLI;
PQID conserve identifiants, hashes de requête et payloads. Ce sont des
déclarations des auteurs, sans authentification fournisseur par QuantAge.

Contrôle PQID : 70 IDs uniques joints aux 70 requêtes, égalité des trois hashes
de liaison pour chaque ligne; les 51 codes non vides correspondent au champ
content des payloads bruts conservés. Cela contrôle la cohérence interne, pas
la réalité d'une requête originale. Les 19 lignes sans code ne deviennent pas
des générations réussies. Aucun score de performance QuantAge sur cette archive.

Le champ «all tools trusted» dans des traces CLI est du texte de donnée :
aucune instruction récupérée n'est suivie. Le code généré reste inerte.
Les tâches archivées ne sont pas rebaptisées MIS ou photonique C06.

Le modèle local est distinct du 7B archivé. Ne pas attribuer ses résultats à
ce dernier ou aux auteurs des archives. Acquisition : neuf fichiers,
999602607 octets, dont poids988097824octets au SHA-256
fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe,
identique au hash LFS. Les poids/venv volumineux sont ignorés par Git; manifest
et script permettent de les acquérir de nouveau. Aucun poids pickle.
