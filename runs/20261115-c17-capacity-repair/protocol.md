# C17 — capacité de formulation et réparation, nouvelle génération de modèle

15 novembre2026, avant acquisition et toute générationC17. Les expériences
C15/C16 sont conservées comme limites : aucune réparation mathématique fidèle
d'un cas faisable observée. C16a63réponses sur64tentatives,1perdue ENOSPC;
guidée1à2/16contreauto1/16, seuil+3 impossible, pas d'imputation.

Première étape bornée : acquire Qwen3.5-2B Q4_K_M, conversion communautaire
SoAIHQ àcommit/SHAépinglés, source originaleQwen/Apache2 déclarée paréditeur.
Quantification non reproduite, identitéd'origine déclarée, pas authenticité
numérique par fabricant. Runtime b12359 existant àhashesconservés, MetalMTL0.
Pasde multimodalité/mmproj, entraînement, secret, achat, QPUoupublication.
Exiger au moins1GiB libre après acquisition, refuser si manque; surveiller
ressources avant les appels. Rendre le templatechat depuisleGGUF avec
enable_thinking=false, pas de raisonnement caché horsbudget.

Deux probes de développement seulement, surles2anciens casC16
080d034c34b2 et4e0256180e89 (déjà vus, jamais rebaptisés test).
Même instructionC16figée, mêmes plafonds384/context2048,180s/appel, pasde
retry de modèle. Une correction d'adaptateur avant génération doit garder
traces et sources. Si au moinsun modèle entièrement fidèle est obtenu et
la ressource viable, poursuivre corpusentièrementnouveau pourlecomparatif;
sinon diagnostiquer/arrêter cette étape sans prétendre à une solution.

Question finale inchangée : effetdu feedback surla fidélité de formulations
complètes, combinaisons réservées, direct/auto/guidée à2appels et768tokens
maximumparbras/cas. Oracle structuré annoté supposé fiable; comparaison
relative au contrat, pas certificatdu texte libre. Grammaire de forme fixe
sans données ni coefficients correctifs. Figer toutavant test, n4..7.
Nouveauprotocole de testdétaillé et nouveaux labels requis avanttoutegénération
test. Les quotas natifs sont épuisés : tâches séquentielles et auto-revue
explicitement non indépendante si aucune nouvelle disponibilité.
