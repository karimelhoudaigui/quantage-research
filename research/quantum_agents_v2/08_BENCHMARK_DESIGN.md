# Conception du benchmark quantique — développement seulement

## Unité d'évaluation

Une requête dans une langue, un jeu de données de géométrie/contrôle, les informations de plateforme/budget explicitement données, une référence sémantique indépendante et un statut pré-étiqueté parmi `supported`, `ambiguous`, `contradictory`, `outside_scope`. Les cas sont groupés par intention de base afin de réserver des groupes et genres linguistiques entiers dans une future évaluation.

## Familles candidates

1. Extraction et conversion unités.
2. Géométrie, distances et interactions pair-à-pair.
3. Hamiltonien, phase, signe et état initial.
4. Observable et calcul de distribution.
5. Séquence Pulser, contrainte de clock/normalisation et canal.
6. Choix de calcul ex ante et abstention.
7. Généralisation à des combinaisons / formulations linguistiques non vues.

Le développement commence par une tâche à trois atomes non colinéaires et des contrôles ciblés (durée clock, layout, distances, champs manquants), sans prétendre couvrir les sept familles.

Les sondes 101→104 ns et registre sans layout ont déjà été observées dans C13; elles sont des contrôles de régression historiques uniquement et sont exclues de tout score de développement/évaluation présenté comme nouveau. Toute étude scorée doit utiliser des demandes et cas distincts, annotés indépendamment.

## Annotations et références

L'auteur de cas et l'annotateur de la référence doivent être des rôles séparés. Le relecteur vérifie les étiquettes avant exposition au modèle. Les références dérivent d'une spécification physique formelle et d'un oracle numérique indépendant; elles ne sont pas générées par le modèle évalué. Les sorties de même auteur ne sont pas décrites comme « indépendantes » sans preuve.

Le test réservé, s'il est approuvé plus tard, ne doit pas être consulté pendant développement, prompts ou choix de seuils. Dans cette exécution de Phase 2 aucun fichier/résultat de test réservé ne sera créé ou ouvert.

## Mesures

Rapporter tableaux de confusion multi-classes, dénominateurs, fidélité sémantique exacte, taux d'acceptation erronée, couverture correcte, risque sélectif, résultats par famille, succès SDK, divergence entre durée demandée/effective, erreurs d'observable, temps/tokens et coût local. Les incertitudes sont calculées par groupes appariés si les hypothèses le permettent; aucune généralisation à une population naturelle n'est revendiquée sans plan d'échantillonnage.

## Taille et puissance

Aucun effectif de test n'est fixé à partir de la seule disponibilité de compute. Le nombre de groupes, répétitions et seuils nécessitent une taille d'effet minimale scientifiquement pertinente et précision/statistiques définies avec supervision humaine. Tant que cela manque, le protocole test réservé n'est pas gelé.
