# C19 — vérification et portée des preuves

Annotation public-only distincte figée avant accès aux labels auteur :20/20contrats concordants. Oracle entier indépendant :20/20domaines et ensembles d’optima concordants,3références infaisables. Revue préalable du moteur/scorer,15sondes logicielles, deux contrôles corrigés avant test (NaN et réserve contexte). Tous les freezes avant appels et sources historiques sont conservés.

Recalcul final : research/c19-observed-review.md/json/.audit/manifest.json,23506contrôles et8sondes manuelles.80réponses/80pairesHTTP (initial20,direct20,auto13+7,guidé20), tousEOS/schémasvalides. Scores13/15/12/13, H19gain1<4 avec1régression. Le modèle guidé répare réellement66f7838312e1 sur référence faisable, en ajoutant lui-même la cardinalité minimale absente ; aucune clause corrigée n’a été fournie. Six autres modèles faux restent inchangés. Régression d’objectif46→48 commune à auto/guidé,64désaccords malgré mêmes optimiseurs.

80profils/160sorties DFS et HiGHS réellement exécutés, vérifiés contre une énumération différente des modèles candidats. L’accord ne certifie pas la formulation. Le routage est un profilage ex post avec coût des deux. Les17références faisables donnent10/12/9/10 ; les3vides passent dans tous les bras, sans preuve structurelle de clauses.

Limite d’indépendance : l’annotateur et son oracle sont séparés de l’auteur, mais le rôle qui a recalculé les scores est aussi auteur du corpus et avait travaillé sur le driver. Le recalcul n’importe pas les fonctions de production ; il n’est ni aveugle ni indépendant de l’auteur des données. Pas d’indépendance humaine/de modèle.

Deux incidents de disque : lancementv1 avant toute inférence puis arrêt auto après13requêtes/13réponses, avant prochaine tentative. Seuls7cas jamais appelés repris, ni retry ni imputation. Sources/consignes/graines identiques. Nettoyage borné des seuls tmp_pack Git anciens/fermés/classés déchets ; références inchangées, objets valides conservés. Coûts ligne748.058s, processus907.255s, CPUclient+serveur241.568s ; CPU du parent de nettoyage, énergie et session complète inconnus. Pas benchmark de latence isolé.

Démonstration séparée de développement b97cb5f56812 :1initiale réutilisée et1vrai appel guidé, toujours15désaccords de faisabilité. Les deux solveurs donnent125 sur ce candidat, mais la boucle conserve usable_for_original=false. Manifest failed carCLI2 signifie budget de réparation épuisé ; aucun incident caché ni succès inventé. Cette observation n’est pas incluse dans les80appels du test.
