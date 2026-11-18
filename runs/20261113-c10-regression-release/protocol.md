# C10 — correction de prototype et régression rétrospective

Après lecture des résultats C09, avant score de la correction. Ce n'est PAS
un nouveau test réservé : C09 devient développement pour cette version.
Les réponses, règles et résultats C08/C09 restent inchangés et leurs échecs
restent dans l'article. Aucune nouvelle réponse n'est fabriquée ou réparée.

Défauts observés : «greatest value» et «distribution» provoquent deux refus
inutiles; une entrée explicitement non spécifiée passe une vérification de
présence du token mode0. Correction bornée : reconnaître les deux synonymes
généraux et refuser les clauses d'incertitude sur l'entrée ainsi que
l'alternative mode0-ou-mode1 non résolue. Code sans ID ni label. Pas de
prétention à un analyseur universel de négation/entailment.

Régression : mêmes16réponses C09, même gold, comparaison sans/avec veto v3.
Le texte brut et les modèles restent identiques. Mesurer couverture, faux
refus et fausses acceptations, sans transformer ce score en résultat réservé.
Budget Python<=60s, aucun hasard ou génération nouvelle dans cette comparaison.
Les métadonnées d'inférence sont réutilisées, pas une nouvelle dépense.

Livraison : CLI locale qui reçoit une intention JSON, génère réellement un
contrat v2 avec le modèle fixé, applique le veto v3, puis formule, vérifie et
sélectionne la référence locale. Deux smoke tests d'intégration séparés des
scores scientifiques : demande photonique explicite valide et demande où
l'entrée est explicitement inconnue. Traces sauvegardées, aucun gold lu au
runtime, aucune API payante/QPU, pas de poids ou code distants au runtime.

Critère de clôture : correction bornée testée, erreurs antérieures conservées,
prototype exécutable sur les deux familles, preuves/manuscrit/état synchronisés.
Le prochain test scientifique devra employer de nouveaux groupes annotés
séparément, car tous les groupes C06 ont maintenant servi à l'évaluation ou
au développement. Fiabilité générale et compatibilité physique restent ouvertes.
