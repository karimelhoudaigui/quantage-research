# Choix de stratégie ex ante — plan et limites

## Méthodes candidates

- Exact dense diagonalization de `H` pour petit système, état pur, contrôle constant et observable de populations.
- Simulation locale Pulser/QuTiP quand la tâche exige une `Sequence`, des conventions SDK ou une dynamique échantillonnée.
- Méthode de densité/émulation avec bruit seulement si modèle de bruit explicite, validé et même observable demandé; hors du pilote initial.
- Abstention/clarification si hypothèses, observable, unités, portée modèle, contraintes logicielles ou ressources sont inconnues/incompatibles.

## Décision pré-exécution

Un agent doit choisir une stratégie et enregistrer justification/prérequis **avant** exécution. Le code de sélection n'a pas accès au temps ou résultat du candidat de test. L'oracle de benchmark choisit la référence après génération uniquement pour calculer des labels, sans exposer ces mesures au modèle. Aucune comparaison « exécuter tous puis sélectionner le plus rapide » ne compte comme politique ex ante.

## Limite identifiée

Sur 2–3 atomes et un pulse constant, l'exact est toujours bon marché; l'exigence « produire une Sequence Pulser » justifie directement le chemin SDK, tandis qu'une probabilité idéale seule favorise l'exact. Ce cas ne teste pas une politique générale et ne donne pas une baseline de portefeuille suffisamment diverse. La sélection de solveur est donc **exploratoire et non évaluée comme contribution primaire** lors du pilote.

Un futur protocole devra établir des régimes où plusieurs méthodes répondent à la même question/précision, mesurer `N`, dimension, profondeur/segments, observable, ressources et coûts complets, fixer le budget et définir le regret ex ante. Si une telle diversité n'est pas réalisable localement au budget autorisé, supprimer cette revendication plutôt que déduire une compétence d'un choix trivial.

## Statuts autorisés

Les étiquettes sont `exact reference`, `local SDK simulation`, `supported deterministic shortcut`, `abstain / clarification`, et `unsupported`. « Quantum advantage », « meilleur solveur quantique », « QPU-ready » et « sélection intelligente démontrée » sont interdits par les preuves actuelles.
