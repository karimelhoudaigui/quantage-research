# P2-RYD-00 — cadrage Rydberg agentique bloqué

**Statut du cycle : `blocked` avant protocole gelé et avant exécution.** Date : 19 novembre 2026.

## A — Priorité et lien à l'article

Question choisie dans le backlog `many_body` : dynamique Ising/Rydberg avec Pulser/Pasqal. Elle adresse directement la limite de l'article C19, qui étudie une réparation d'ILP classique. C12/C13 sont des validations SDK indépendantes, pas une mesure d'agent quantique.

## B — Littérature

La revue ciblée confirme que l'ambition générale d'un workflow agentique neutre-atomique n'est pas différenciée : Dalyac et al. (arXiv:2607.25834v1) relient déjà protocoles, simulation et campagnes QPU Pasqal; Sheng et al. (arXiv:2610.25014v1) rapportent le pilotage humain-dans-la-boucle d'une plateforme de pinces; QCoder/QTestBench/Quantum Leap couvrent la génération, le test ou l'audit de code quantique. L'angle resserré sur la conservation de l'intention physique au passage Pulser/Device est une hypothèse de contribution, pas une nouveauté établie.

La source QAOS comporte un écart non résolu : abstract arXiv `633` articles, introduction HTML v1 `526`. Aucun chiffre de corpus n'est utilisé.

## C — Matériel et preuve quantique disponible

C13 a construit et simulé 162 séquences Pulser 1.7.2/QuTiP 5.2.3 sur deux atomes; erreur probabiliste max `0.0004726528 < 0.005`. C'est une comparaison locale avec Hamiltonien indépendant, sans bruit ni QPU. L'arrondi 101→104 ns et le layout manquant sont des cas C13 déjà observés, pas de nouveaux résultats de Phase 2.

## D — Formulation et niveaux de vérification

Un brouillon d'IR et un contrat séparent parse, fidélité sémantique, mathématiques, SDK, Device/backend et simulation. Le modèle proposé est idéal, petit, ground–Rydberg, `C6/r^6`, pulse global constant et observable de populations. Aucune de ces couches n'est implémentée pour Phase 2.

## E — Question et hypothèses

La question candidate porte sur la prévention des fausses acceptations par une IR et des vérificateurs indépendants, sans perte de couverture correcte par abstention. H_A (gain de vérification) et H_B (sécurité par refus) sont consignées comme hypothèses non testées. Critère primaire, seuil d'effet et puissance ne sont pas définis.

## F — Baselines et routeur

Baselines déterministe, direct LLM, schéma seul, auto-révision à appels comparables et pipeline vérifié sont spécifiées, mais aucune n'est exécutée. Le choix de solveur est exclu de l'évaluation primaire : le cas à trois atomes ne distingue pas suffisamment les méthodes.

## G — Protocole proposé

Un pilote local de développement de 300 s max, un cas principal et une génération locale au plus était esquissé; le protocole n'a pas été gelé. Les sondes C13 connues seraient des tests de régression uniquement et seraient exclues des scores. Aucun cas réservé n'a été ouvert ni généré.

## H — Revue

La revue indépendante a échoué avant lecture : erreur `400 The requested model is not supported`. L'auto-revue de l'intégrateur consigne cinq blocages majeurs; elle n'est pas indépendante.

## I — Exécution et vérification

Aucun code nouveau, appel de modèle, simulation, seed ou résultat Phase 2. Aucune QPU, dépense externe, réseau de modèle ou lecture de C23. Le gate s'arrête avant toute exécution; ce blocage n'est pas une preuve d'échec scientifique de l'hypothèse.

## J — Claims et manuscrit

Aucun claim quantique de performance/nouveauté n'est vérifié. Un claim `inconclusive` documente le statut. Le manuscrit est mis à jour pour expliciter le gate bloqué; les résultats C19/H19/C12/C13 ne sont pas modifiés. `paper/main.pdf` a été reconstruit hors ligne avec le Tectonic local épinglé à partir de `paper/main.tex`; provenance et empreintes dans `paper-build.json`. Les seuls avertissements TeX observés sont des underfull boxes; le PDF est un document de travail, pas une validation scientifique ni une soumission prête.

## K — Décision et prochaine action

Ne pas exécuter le pilote ni le test réservé dans cette tentative. Reprendre uniquement avec (1) revue bibliographique indépendante focalisée sur la sous-question, (2) reviewer humain/agent distinct capable de lire le protocole, (3) métrique primaire et justification de taille/effet, (4) cas d'évaluation indépendants des sondes C13, (5) choix humain et protocole gelé. C23 reste bloqué; C28 n'est pas relancé. L'article demeure document de travail.
