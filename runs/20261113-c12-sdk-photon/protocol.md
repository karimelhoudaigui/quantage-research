# C12 — validation logicielle multiphotonique indépendante

Préenregistré le13novembre2026 avant import ou exécution scientifique de Perceval. L'installation du venv est une préparation de l'environnement. Base Git et versions effectives seront observées au run. Historique C01–C10 inchangé.

## Question et hypothèse

La distribution de Fock complète d'un vrai circuit3modes/2photons accepté par Perceval1.3.1 concorde-t-elle avec un oracle construit indépendamment, et quelles contraintes le SDK refuse-t-il effectivement? Hypothèse bornée H12 : chaque probabilité de la grille ci-dessous concorde à1e-10, les distributions sont normalisées et les conventions de matrice coïncident. Ce test d'implémentation est un prérequis pour étudier plus tard la généralisation agentique; ce n'est pas une contribution algorithmique nouvelle ou une performance LLM.

## Domaine et oracle

Photons indistinguables idéaux, état de Fock pur,3modes spatiaux,2photons, aucune perte, aucun bruit, aucun post-traitement/post-sélection, détection idéale résolvant le nombre. Angles en radians. Circuit dans l'ordre temporel R01(a), PS1(phi), R12(b), R01(c), où R(theta)=[[cos(theta),-sin(theta)],[sin(theta),cos(theta)] et la construction SDK utilise BS.Ry(theta=2*theta). Ainsi U=R01(c)R12(b)diag(1,exp(i phi),1)R01(a).

Grille déterministe exhaustive déclarée : a,b,c dans{0,pi/4,pi/2}, phi dans{0,pi/3,pi}, six occupations d'entrée non négatives de somme2. 81 configurations de paramètres et486 évaluations entrée/circuit; toutes les six sorties sont comparées. Ces cas ne sont pas des échantillons indépendants d'une population naturelle. Les paramètres distincts peuvent décrire des probabilités équivalentes; tous sont conservés.

Oracle séparé du SDK : construction3x3 avec trigonométrie et multiplication matricielle propres, puis application successive des opérateurs de création transformés au vide. Chaque création sur le mode i apporte sqrt(n_i+1), puis division par sqrt(prod(t_j!)). Aucun permanent, matrice ou simulateur fourni par Perceval n'est utilisé par l'oracle. Calcul flottant complexe, représentation Fock finie complète; pas arithmétique exacte. La formule de normalisation est confrontée au papier Perceval§4.2.1eq7.

Contrôles connus inclus dans la grille : identité, photons en collision à l'entrée et Hong–Ou–Mandel équilibré a=pi/4,b=c=phi=0,t=(1,1,0), dont P(2,0,0)=P(0,2,0)=1/2 et P(1,1,0)=0. Pas de tirage de shots, aucune seed nécessaire; aucun ajustement après observation pour améliorer les métriques.

## Négatifs préenregistrés

Observer en processus séparés les résultats/erreurs SDK pour : composant2modes placé à l'indice2 d'un circuit3modes; état d'entrée de longueur2; occupation négative; composant nonunitaire; trois photons valides; tentative de composant de perte dans Circuit/SLOS si API disponible. Ne pas présumer que tous seront refusés :3photons est une entrée SDK légitime, hors du contrat2photons. Une perte est une fonctionnalité possible d'autres couches, hors de ce backend idéal. Si l'API de perte est absente, enregistrer unsupported_api, pas un rejet physique. Conserver les messages et les acceptations non attendues; un crash devient échec de cette sonde et non succès.

Vérifier aussi la frontière du contrat propre : longueur3, entiers non booléens non négatifs de somme2, angles finis, backend idéal sans perte, observable distribution résolvant le nombre. Ce contrôle d'entrée ne prouve aucune propriété d'un QPU. Un cas invalide n'est jamais normalisé silencieusement en autre tâche.

## Métriques et interprétation

Pour chaque évaluation : U SDK contre U oracle, toutes probabilités, erreur maximale, somme, états négatifs éventuels, durée, type/version du backend. Agrégats : évaluations prévues/observées, nombre de comparaisons, maxerreurs, contrôles HOM, toutes issues négatives SDK et refus du contrat. L'absence d'erreur au seuil soutient H12 uniquement sur cette grille finie et ces conventions. Échec numérique ou API reste visible et ne doit pas être réparé en écrasant les sorties; un protocole ultérieur est nécessaire.

Niveaux : mathematique_ideal vérifié par l'oracle; sdk_accepted observé par construction/exécution; specific_hardware_compatible=unverified; qpu_executed=false. Aucun SDK succès ne démontre sources/pertes/détecteurs/nombre de modes permis sur une machine Quandela précise. Pas d'avantage quantique, pas de résolution d'optimisation, pas d'évaluation LLM.

## Ressources, séparation et arrêt

Venv dédié .venv-quantum-sdk sous Python3.11; package officiel public Perceval1.3.1. Versions dépendances gelées après installation et avant run. Zéro achat, compte, secret, message externe, publication, push ou QPU. Exécution locale seule; pas de RemoteComputer/communication/cloud.

Budget scientifique :180secondes pour grille+sondes,20secondes par sonde, au plus486évaluations et6sondes, mémoire prévue petite. Arrêt au premier échec de l'expérience principale, erreur conservée. Budget installation autorisé distinct, borné par commande. Le runner de provenance Mathbox v2 enregistre avant/après hashes, commande, Python, temps et sorties. Pas de réutilisation des requêtes C01–C10 comme test indépendant; cette grille est un test de conformité SDK mathématique et ne devient pas une validation de l'agent v4.

La revue de ce run n'est pas indépendante tant qu'un auditeur distinct n'a pas contrôlé ces artefacts. L'intégrateur sera prévenu avant le lancement pour éviter la concurrence avec une inférence CPU lourde.
