# C15 — formulation explicite, test comparatif bloqué

La boucle est implémentée : proposition ILP complète, compilateur linéaire
sans complétion de clauses, vérificateur exhaustif, feedback minimal et révision,
deux solveurs exécutables. Ses tests et audits logiciels ne sont pas une
performance LLM. La question comparative H15 reste non résolue.

Deux séries réelles de développement Qwen2.5-0.5B : v1, huit schémas invalides;
v2 après l'unique révision autorisée, sept invalides et un modèle valide mais
faux. Ce dernier conserve 32 affectations au lieu de9, soit23 désaccords de
faisabilité et aucun d'objectif. DFS et HiGHS concordent sur son optimum31,
alors que l'optimum du contrat de référence vaut17. Résoudre le candidat
correctement ne répare donc pas sa formulation.

Le test initial a été arrêté anticipativement pour ressources : une réponse
EOS203tokens a été enregistrée en483.215s avant l'arrêt final; quinze sont
absentes. La réponse s'est terminée entre l'inspection initiale zéro ligne et
le SIGTERM. Le fichier de réconciliation corrige explicitement le bilan final
sans réécrire l'observation pré-signal. Manifest failed, exit-15,519.331s,
generation.json absent. Aucune phase direct/auto/guidée de test, aucune
imputation, aucun taux comparatif ou H15 réfutée inventé.

Revue indépendante : c15-v2-review.md et c15-observed-review.md. Deux rôles
distincts, pas d'indépendance humaine ou de modèle prouvée.17traces réelles
contrôlées sans charger le modèle. Un décalage UTCv1 de6698.924s entre
métadonnées et enveloppe reste inexpliqué malgré hashes conformes; les temps
monotones sont distincts. Aucune conclusion sur la chronologie/coût complet
de session n'est tirée de cet horodatage.

Les sources du manuscrit étaient réellement corrompues : cinq expressions
restaurées, originaux archivés, tableaux et displays multilignes corrigés.
89tests passent à ce checkpoint, dont13régressions de manuscrit. Pas de
compilateur LaTeX, pas de manuscrit PDF validé.

Suite autorisée : C16 distinct, moteur quantifié llama.cpp/Metal et corpus
entièrement nouveau, contrôle de forme identique dans les bras. C15 reste
bloqué et conservé; aucune reprise de son test après adaptation.
