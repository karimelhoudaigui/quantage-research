# C05 — intégration de la vérification indépendante

Ancien moteur conservé : core.py SHA-256
35001246743a201d2326a53a586fd50bedca48d8e322f52124f2a3e0c7403be2;
verification.py c7d070281763bb46ad6244ef1c0bc4734c159bc32d5adca1dfac6e9786f6426f.
La nouvelle frontière externe contracts.py n'est pas une modification des
calculs C01–C04. Elle valide le problème, les types, enums, indices, métadonnées
et tolérance avant de demander une comparaison finie de sorties.

L'auditeur distinct a produit audit_cases.json et independent-audit.md :
73 cas, dont 67 propositions externes et 6 tests du pipeline canonique.
Les labels d'acceptabilité de schéma ont été écrits avant le nouveau scoring.
Comparaison enregistrée : 23 acceptations malformées par verify direct,
aucune par verify_external; les 11 contrôles valides restent admis.
Les 6 requêtes invalides du pipeline sont déjà toutes refusées par l'ancien
pipeline : aucune faille d'injection de modèle dans ce CLI n'est revendiquée.

La revue séparée external-contract-review.md et external-contract-audit.json
reconstruit ses propres attentes sur 109 cas (67 initiaux +42 discriminants),
sans employer les labels de l'intégrateur comme oracle. Aucune divergence :
81 rejets de schéma, 4 rejets numériques et 24 acceptations prévues. Revue
non aveugle, même famille de modèle possible; indépendance d'auteur seulement.
Le sous-agent a été interrompu par quota après avoir écrit les deux rapports
et les preuves brutes; ses fichiers existent et leurs empreintes sont contrôlées.

L'intégrateur réévalue ces 109 entrées comme données, sans exécuter leur champ
replay_source, dans la vérification de clôture. Le manifest v2 principal
results/manifest.json enregistre le run comparatif de 73 cas, les inputs exacts,
la commande, les versions et les hashes avant/après.

Ce certificat reste limité aux sorties de l'instance. Les champs de l'intention
originale, la compatibilité physique, un taux populationnel d'erreur ou une
performance LLM ne sont pas établis par ces cas. Les coefficients QUBO externes
admis sont entiers, restriction explicite et non preuve sur les flottants.
