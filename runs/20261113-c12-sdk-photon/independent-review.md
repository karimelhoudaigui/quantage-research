# Revue indépendante C12 — conformité photonique finie

Relecteur : /root/c11_audit, 13 novembre 2026. Auteur distinct du code expérimental, accès aux protocoles et résultats; revue non aveugle et sans indépendance de modèle démontrée. Aucun code ou résultat de l'auteur modifié. Les commandes, sorties et empreintes relues figurent dans independent-review.json.

## Verdict et contrôles exécutés

Assertion finie vérifiée indépendamment sous la tolérance flottante préenregistrée 1e-10. Le manifest v2 est completed et sa validation avec --root . passe. Les trois tests analytiques sans SDK passent. La grille contient exactement les 81 quadruplets annoncés et les six occupations de deux photons sur trois modes, sans doublon ou manque : 486 évaluations et 2 916 probabilités. Chaque sortie couvre les six occupations attendues; aucune probabilité SDK négative observée.

Le relecteur a recalculé toutes les probabilités avec une construction différente : somme explicite des chemins de la matrice U=R01(c)R12(b)D1(phi)R01(a), puis somme des deux permutations des chemins à deux photons. L'oracle de l'auteur utilise une propagation d'opérateurs de création; ce recalcul n'importe ni cet oracle, ni Perceval ou SLOS. Pour les indices d'entrée développés j1,j2 et de sortie i1,i2, la probabilité est

P(s|t)=|U[i1,j1]U[i2,j2]+U[i1,j2]U[i2,j1]|² / (prod_k(s_k!) prod_k(t_k!)).

Cette expression découle de l'expansion du produit des deux opérateurs de création transformés, avec normalisation des états de Fock; elle conserve les deux termes même si les indices se répètent. Elle donne bien 1/2,1/2,0 pour Hong–Ou–Mandel équilibré et 1/4,1/2,1/4 pour une entrée en collision sur un seul séparateur équilibré.

Erreur maximale du recalcul contre SDK : 3.3306690738754696e-16; contre l'oracle de création enregistré : 2.220446049250313e-16; erreur maximale de normalisation : 4.440892098500626e-16. La différence avec le maximum 2.22e-16 annoncé par l'auteur provient de l'algorithme flottant de recalcul, pas d'une modification des données. Le recalcul dure environ 0.06 s sur ce processus et ne mesure pas le temps du SDK.

## Portée de la validation logicielle

Le code construit réellement un circuit Perceval 1.3.1 avec BS.Ry(theta=2a) et phases explicites, puis exécute SLOS localement. Les versions et les empreintes de l'environnement sont enregistrées; cet audit contrôle leurs enregistrements sans réinstaller les dépendances. Le relecteur n'a pas rejoué la totalité du SDK ni les six sous-processus de sondes pendant les inférences C11; il a vérifié leurs traces et l'intégrité du manifest.

Les six sondes sont correctement interprétées : composants/entrées hors dimensions, occupation négative et non-unitarité rejetés; trois photons acceptés légitimement par le SDK, mais refusés par le contrat deux photons; perte rejetée par Circuit/SLOS, sans prétendre que toute la plateforme ignore les pertes. Plusieurs rejets s'appuient sur des assert SDK; les observations portent sur optimisation Python=0. La frontière propre a neuf sondes, pas une preuve d'exhaustivité pour toute entrée.

## Limites et implication

La vérification concerne une grille finie à photons indistinguables, cohérence et détection résolvant le nombre idéales, sans pertes, bruit ou shots. Aucune erreur bornée par arithmétique d'intervalles n'est fournie et aucune correction générique de Perceval n'est démontrée. Les paramètres ne sont pas des échantillons statistiquement indépendants; aucune inférence populationnelle.

Ce résultat établit une conformité mathématique/logicielle bornée au niveau simulateur réel local. Les sources, pertes, détecteurs et limites d'une machine Quandela précise ne sont pas validés. specific_hardware_compatible reste unverified et qpu_executed reste false. Aucun avantage quantique, originalité algorithmique ou généralisation de l'agent n'est établi. La prochaine étude agentique pourra utiliser ce domaine, avec de nouvelles intentions annotées et une frontière de compatibilité explicitement séparée.
