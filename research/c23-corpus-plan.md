# C23 — plan de construction, avant toute inférence

16 novembre2026 (Paris). Le chemin historique attribué au lot conserve20261115 comme identifiant, sans antidater sa création ou son gel. Lot auteur uniquement. Préparer20instances candidates pour une future évaluation de composition relationnelle; ne lancer aucune génération LLM. La capacité du8B reste à observer par root. Le code, les consignes et le protocole d'une éventuelle expérience seront figés séparément avant les appels; ce corpus ne constitue pas encore un résultat ou une promesse de test confirmatoire.

## Contrat prévu avant construction

Vingt publics `{id,language,intention,data}`, données `{n,weights,costs,edges}`; dix textes français et dix anglais, dix groupes de deux instances indépendamment numérisées. Chaque groupe contient une FR et une EN, avec données et indices différents : pas de traduction appariée. Cinq groupes utilisent n6, cinq n7. Poids17..61, coûts13..39 strictement positifs, une à trois exclusions, sauf nécessité documentée avant publication. Objectif maximiser la somme des weights, variables binaires, seuils et clauses supplémentaires explicitement énoncés.

**Chaque instance contient exactement trois implications dirigées distinctes.** Chacune est individuellement essentielle au domaine faisable : retirer uniquement cette implication, en conservant toutes les autres contraintes et implications, ajoute au moins une affectation. Les20domaines complets doivent être non vides. Aucun certificat sur domaine vide n'entre dans ce lot.

Interprétation de l'activité : les exclusions E et chaque famille optionnelle **présente** parmi B/L/U/M/F/I doivent changer le domaine après retrait complet de cette famille. Chaque implication est en plus testée par retrait individuel. Le constructeur cherchera également des exclusions individuellement essentielles; cette exigence plus forte sera rapportée explicitement. Les familles absentes restent null/listes vides dans le gold. Les ensembles de familles peuvent être historiquement connus; ils ne seront pas qualifiés de globalement inédits.

Les dix motifs prévus sont : chaîne de trois arcs; étoile sortante; étoile entrante; embranchement après un arc; cycle dirigé de longueur3; cycle réciproque de longueur2 plus un arc disjoint; trois arcs disjoints; bifurcation avec prolongement; deux antécédents partageant une conséquence plus un arc disjoint; un second groupe dense avec cycle réciproque et arc disjoint. Le dernier distingue la présence simultanée des six familles du motif moins contraint. Une permutation des indices ne sera pas présentée comme un nouveau motif. Les groupes ne sont donc pas dix types de graphes à isomorphisme près.

Le groupe avec les six familles est affecté à n7 **avant construction**, afin de ménager des témoins distincts pour budget, cardinalités, obligation, interdiction et implications. Aucune impossibilité générale à n6 n'est revendiquée sans preuve. Les autres groupes varient explicitement le sous-ensemble de familles; les groupes denses utilisent n7. Cela préserve la variété des relations plutôt que d'imposer artificiellement toutes les familles à chaque problème.

## Recherche bornée et contrôles

Le constructeur privé utilise seulement les publics et annotations historiques nécessaires au contrôle des doublons et du nombre d'implications. Il ne lit aucune réponse, métrique, sélection de solveur ou sortie de modèle. Les motifs, familles et tailles sont fixés avant recherche; les paramètres numériques peuvent être choisis pour rendre les restrictions actives. Aucun filtrage sur un résultat LLM.

Au plus50000candidats par cas, une seed fixe par emplacement, et un délai global300s. Les rejets sont conservés avec motif de rejet, numéro de tentative et digest du candidat; seed et générateur suffisent à les rejouer. En cas d'échec borné, écrire le bilan privé et conserver les rejets, sans fabriquer vingt publics ou effacer un gabarit réfuté. Aucun second budget illimité. Une adaptation mathématique éventuelle devra être notée avant tout gel public.

Chaque cube comporte64 ou128affectations. Contrôler faisabilité, valeurs et tous les optima en arithmétique entière; activité de chaque famille présente et chaque implication par retrait exact. Contrôler également les graphes étiquetés, textes, données et ID contre les publics C15/C16/C19/C20/C21 et entre nouveaux cas. L'absence de doublon de graphe étiqueté n'implique pas l'absence d'isomorphisme. Les invariants mécaniques n'établissent pas la correction sémantique de l'intention; celle-ci nécessite une annotation publique distincte.

## Séparation et remise

Le générateur, les labels et les certificats de construction restent **privés** sous `runs/20261115-c23-compositional-repair/`. Avant gel des annotations indépendantes, root/reviewer ne reçoit ni contenu ni hash du générateur ou du gold auteur. Seuls le chemin et le SHA de `test_cases.json` sont annoncés pour annotation. Le gold auteur n'est jamais une entrée LLM.

Après lecture des seuls publics, le reviewer fige ses labels avant comparaison. Root pourra alors recevoir les privés, arbitrer et figer le corpus final. Aucun résultat de performance n'existe; l'auteur est aussi impliqué dans les corpus et réparations antérieurs, sans indépendance humaine ou de famille de modèle. Si une méthode est adaptée après observation de ces futurs cas, ils deviennent du développement et ne peuvent plus servir de test réservé à cette méthode.

Ce lot n'écrit aucun code de production, article, state ou claim et ne lance aucun modèle, solveur externe, téléchargement ou QPU. Les seules recherches numériques portent sur la construction mathématique finie du corpus.
