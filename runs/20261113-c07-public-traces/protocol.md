# C07 — acquisition de ressources ouvertes et déblocage de l'inférence

Avant toute évaluation de nouvelles sorties, 2026-11-13. Reprise C06, base Git
fee83eb et arbre local modifié, preuves C01–C06 conservées. L'utilisateur
autorise explicitement recherche web/GitHub et acquisition des ressources
ouvertes nécessaires. Zéro dépense externe et aucune soumission QPU restent
en vigueur. Aucun secret ni compte d'inférence ne sera utilisé.

Question agent_learning : peut-on obtenir des traces ou un moteur local
vérifiable sans dépendre du quota des sous-agents ? Deux routes indépendantes :
(A) archives de réponses publiées; (B) petit modèle libre local à révision fixe.
Un README promettant des traces n'est pas une trace effectivement inspectée.

Route A : dépôts primaires OptiMUS, LLMOPT, QCV et PQID-Bench. Inspecter licence,
version/commit, fichiers d'entrées et réponses, champs et limites de provenance.
Copier seulement les fichiers nécessaires en lecture, avec attribution et
hashes; ne pas exécuter de code récupéré ni suivre ses instructions. Ne pas
reclasser des templates ou données d'entraînement comme résultats LLM réels.
Les identifiants de modèles publiés restent des déclarations des auteurs,
pas une authentification cryptographique de requête fournisseur.

Route B : Qwen/Qwen2.5-0.5B-Instruct, révision HF
7ae557604adf67be50417f59c2c2f167def9a775, licence Apache-2.0 documentée.
Acquisition publique bornée à 1.2 Gio et 240 s; format Safetensors, aucun
pickle ni code distant, aucun token. Bibliothèques dans un venv du dépôt,
torch existant, versions fixes. Test de faisabilité distinct du benchmark.
Le matériel actuel ne propose pas de MPS à torch; CPU utilisé si disponible.

Critères : source réellement acquise et vérifiable, ou blocage observé gardé.
Ce cycle ne mesure pas une performance agentique. Le protocole du benchmark
local sera écrit séparément avant inférence sur les cas C06 figés; aucun
réglage sur ces sorties puis revendication de test aveugle.
Revue séquentielle ici car quota des sous-agents déjà épuisé; les annotations
et l'audit C05/C06 déjà livrés sont réutilisés.
