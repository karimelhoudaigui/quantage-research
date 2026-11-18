# Unique révision sur développement, avant tout test
Deux préflight réels (080d034c34b2,4e0256180e89) sont au schéma valide mais
mathématiquement faux. La sérialisation triée du JSONSchema conduit à écrire
constraints avant variables/objectif; l'agent ignore des clauses et en invente.
La révision demande les variables et l'objectif avant les contraintes, via
une grammaire GBNF fixe. Même cinq champs/types, valeurs/indices/longueurs/clauses
toujours choisis par le modèle; aucune donnée ou référence dans la grammaire.
Consigne raccourcie, exemples de deux familles maximum, exclusion explicite
de contraintes non demandées. Les deux premières réponses restentv1; les
six autres développement sontv2. Pas de répétition des deux premiers cas.
C'est l'unique révision de prompt; après les six, gel quel que soit le résultat.
Toutes les méthodes test utiliseront exactement cette version.
