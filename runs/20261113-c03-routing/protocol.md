# C03 — vérification des propositions de solveur

Préenregistré après C02, avant exécution C03. Parent : C02 results/manifest.json;
Git fee83eb + changements locaux, empreintes exactes dans le manifest C03.
Backlog : agent_learning, hardware comme dépendance.

Question : un certificat de formulation suffit-il à accepter une proposition
de solveur ? Hypothèse : un contrôle des modalités, de la provenance et de la
portée des promesses rejette des propositions qu'une règle de nom accepte.

Corpus de 20 propositions manuelles, labels fixés dans cases.json avant le run.
Deux familles supportées, variantes de statut simulation/physique, fournisseur
français vs hébergement en France, QUBO arbitraire, bruit SpinPulse, observable
exacte vs mesures. Labels : acceptable comme recommandation locale ou candidat
CONDITIONNEL; refus des promesses non établies. Aucun label «QPU validé».
Séparer acceptabilité de la recommandation et permission d'exécution : même un
candidat conditionnel ne peut être soumis physiquement selon policy.json.

Baselines déterministes : nom de famille/localisation (naïve), + vérification
de modalité, + portée de la promesse. Mêmes données pour chaque ablation.
Métriques : matrice acceptation/rejet, fausses acceptations des propositions
non justifiées, rejet des recommandations admissibles, permissions physiques.
Les labels sont construits par l'auteur et non une validation matérielle.
Pas de généralisation statistique, pas de comparaison à un LLM.

Budget Python standard <=60 s, 20 cas fixes, aucune seed nécessaire, zéro
appel externe ou SDK. Arrêt à la première exception. Revue non indépendante.
Commande : python3 -m quantage.routingstudy --cases RUN/cases.json
--policy config/policy.json --output RUN/results, provenance manifest v2.
