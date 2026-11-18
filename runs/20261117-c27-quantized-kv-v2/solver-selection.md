# Sélection et vérification des solveurs C27

## Entrée évaluée

Le seul candidat transmis aux solveurs est la formulation finale C27, déjà vérifiée comme fidèle sur les 16 affectations du cas de développement. Les solveurs classiques ne reçoivent ni le texte d'intention ni le gold.

## Résultats exécutés

La commande `python scripts/audit_c27.py` exécute les deux solveurs :

- DFS exhaustif : `optimal`, objectif 78, solution `[1,1,0,0]`, 16 feuilles visitées.
- SciPy HiGHS MILP : `optimal`, objectif 78, solution `[1,1,0,0]`, statut natif 0.
- Concordance : oui. Environnement : Python 3.11.15 et SciPy 1.17.1.

Le temps total mesuré du portefeuille est d'environ 0,755 s, dont environ 0,755 s pour HiGHS dans cet environnement; les temps sont des mesures d'un seul petit cas et ne sont pas des estimations de débit généralisables.

## Interprétation

Le sélecteur retient DFS après avoir exécuté les deux solveurs, selon leur temps mesuré sur ce cas. C'est une sélection ex post et non un routeur prédictif; les coûts des deux solveurs sont engagés. Aucun solveur quantique n'a été lancé et aucune compatibilité QPU n'est inférée.
