# Question scientifique et hypothèses concurrentes

## Question de travail

Pour des demandes contrôlées d'évolution analogique de quelques atomes de Rydberg, un système à représentation intermédiaire typée et vérificateurs indépendants peut-il mieux préserver l'intention physique jusqu'à un programme Pulser 1.7.2 et décider correctement d'accepter, de clarifier ou de s'abstenir, qu'un LLM direct ou une baseline déterministe à domaine explicite?

Le mot « mieux » est ici opérationnalisé comme **moins d'acceptations scientifiquement incorrectes**, tout en publiant séparément la couverture des demandes supportées. Une abstention n'est pas un succès de formulation; elle est évaluée comme décision distincte.

## Portée opérationnelle candidate

Première famille : modèle de deux à quelques atomes en base ground–Rydberg, interactions van der Waals finies `C6/r^6`, contrôle global constant par créneau, système initial en base, évolution idéale sans bruit/modulation, observable de populations. Le niveau d'affirmation maximum du pilote est « modèle exact pour l'IR déclarée » et « Sequence acceptée/localement simulée par Pulser 1.7.2 ». Pas de compatibilité QPU.

## Hypothèses concurrentes

- **H_A — gains de vérification au-delà du refus.** À budget d'appels et couverture contrôlés, le pipeline à IR et vérificateurs réduit les fausses acceptations et augmente la proportion de toutes les demandes ayant une réponse acceptée correcte, par rapport au LLM direct et à une baseline déterministe forte.
- **H_B — sécurité principalement par abstention.** Les vérificateurs diminuent les fausses acceptations, mais la proportion de demandes supportées correctement acceptées chute; aucun gain de couverture correcte à risque fixé n'est observé.

H_A et H_B distinguent une correction productive d'un système qui refuse tout. Le pilote de développement ne tranche pas ces hypothèses. Les seuils de décision, effet minimum pertinent et taille du corpus réservé restent **provisoires** jusqu'à examen de puissance et accord humain.

## Critères et métriques candidates

Pour chaque tâche étiquetée avant inférence :

1. validité d'IR/schéma;
2. fidélité exacte ou équivalence sémantique à la référence annotée;
3. cohérence du modèle (hermiticité, indices, unités, normalisation);
4. acceptation Pulser et invariance de la séquence par rapport à la demande;
5. conformité de la stratégie déclarée aux préconditions/ressources;
6. décision correcte d'abstention/clarification;
7. fausse acceptation d'un cas ambigu/invalide;
8. couverture correcte sur les tâches supportées et risque sélectif;
9. régressions et taux de réponses incomplètes;
10. appels, tokens, latence, mémoire et coût de calcul local.

Un seul critère primaire et seuils doivent être gelés avant accès au test. Pas d'intervalle de population sur des défis choisis manuellement sans hypothèses d'échantillonnage; rapporter les dénominateurs finis et différences appariées.

## Pourquoi cette question

Elle se rattache à la mission intention → compréhension → formulation → sélection, en concentrant l'étude sur un point quantique réel plutôt qu'une ILP classique. C13 donne un petit oracle et une implémentation Pulser réelle. La revue de littérature révèle déjà des workflows agentiques neutres-atomiques proches; l'angle d'évaluation des divergences sémantique/SDK est donc plus précis, mais pas encore une revendication originale.
