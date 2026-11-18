# C10 — amendement de développement v4

La première correction v3 supprime le cas d'entrée inconnue et restaure deux
acceptations valides, mais la reconnaissance de «greatest» ouvre une nouvelle
acceptation erronée : la direction est explicitement non décidée entre poids et
nombre de sommets. Le résultat v3,7/9supportés et1/7hors contrat accepté, reste
dans results/ et son manifest n'est pas modifié. Ce n'est pas un nouveau test.

Correction supplémentaire avant seconde régression : les clauses de direction
explicitement indécise ont priorité sur les mots de maximisation présents dans
une alternative. Ajouter un veto borné sur goal/objective/direction/choice avec
not decided/unresolved/unknown, sans ID de cas. Le module v4 est séparé, le code
et les résultats v3 sont conservés. Scorer exactement les mêmes propositions
C09, aucune génération ou label modifié. Le résultat reste une régression
rétrospective après consultation, sans preuve de généralisation.

Le CLI final utilise v4. Un troisième smoke/replay reprend le contre-exemple
d'objectif inconnu pour vérifier en bout de chaîne ce veto. Les deux premiers
smokes restent identifiés v3; tous les replays vérifient seulement ces traces
et configurations, pas une reproductibilité universelle inter-matériels.
