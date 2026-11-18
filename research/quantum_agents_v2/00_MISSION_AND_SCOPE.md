# Phase 2 — mission et périmètre

**Statut : cadrage provisoire; pas de test réservé exécuté.** Date : 19 novembre 2026. Cette phase reprend la question quantique du dépôt après l'audit scientifique du 18 novembre. Les résultats C19/H19, runs C12/C13 et historiques C23/C28 sont immuables pour cette étude.

## Mission

Étudier quand un agent peut transformer une demande sur une expérience analogique Rydberg en un modèle scientifique inspectable, identifier les informations absentes, préserver le sens à travers Pulser et choisir une voie locale de calcul ou s'abstenir. La contribution n'est pas la production de code à elle seule.

## Verticale de travail

- Atomes neutres / interactions Rydberg / Pasqal / Pulser.
- Cible logicielle de développement : Pulser 1.7.2 et `AnalogDevice` tel qu'installé pour C13.
- Cible de preuve : modèle mathématique fini et simulation locale Pulser; pas de soumission QPU.
- C13 est une preuve de faisabilité physique/logicielle de référence, non une validation de la nouvelle architecture.
- L'extension Perceval/Quandela est explicitement hors de cette phase.

## Limites du cadrage

Le benchmark candidat n'est pas une population d'expériences réelles. Le premier pilote peut être synthétique, borné et non aveugle; ses résultats serviront à valider l'infrastructure et le contrat, pas à estimer une capacité générale d'agent. Le solveur selector ne sera évalué scientifiquement que si des tâches offrent plusieurs méthodes admissibles et des régimes de coût différents. Un choix évident à deux/trois atomes ne démontrerait pas un routeur.

## Interdictions appliquées

Aucune donnée du test réservé n'est lue, créée comme résultat de test ou présentée à un modèle. Aucun appel QPU, cloud payant, dépense externe, accès secret, push, publication ou modification C19/C23/C28. Pas de retry de génération après timeout. Les résultats anciens et claims réfutés restent conservés.

## Décision de continuation

La question initiale de l'utilisateur est trop large pour une revendication originale : QAOS et les benchmarks de code quantique sont des antériorités proches. La sous-question de développement proposée dans `02_SCIENTIFIC_QUESTION.md` est un candidat plus précis, pas une preuve de nouveauté. La revue indépendante du protocole et la recherche bibliographique complète restent des prérequis du test réservé.
