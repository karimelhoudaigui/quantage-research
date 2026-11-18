# Revue indépendante C13 — simulation Rydberg à deux atomes

Relecteur : /root/c11_audit, 13 novembre 2026. Auteur distinct du code expérimental, accès aux résultats; revue non aveugle et sans indépendance de modèle démontrée. Aucun code ni résultat de l'auteur modifié. Commandes, sorties et empreintes dans independent-review.json.

## Verdict et calculs exécutés

Assertion finie vérifiée indépendamment dans les tolérances préenregistrées, avec la distinction importante entre pulse nominal constant et représentation temporelle SDK. Le manifest v2 completed est valide avec --root .; les trois tests analytiques de l'oracle passent. Les 162 combinaisons distance, amplitude, detuning, phase et durée sont présentes une fois chacune. Les 648 probabilités finales ont été recalculées.

Construction orthogonale : matrice d'un atome h=[[0,Omega*exp(-i phi)/2],[Omega*exp(i phi)/2,-delta]], puis H=h tensor I + I tensor h + V diag(0,0,0,1), dans l'ordre gg,gr,rg,rr, avec V=C6/r^6. L'interaction enregistrée correspond exactement au C6 de la spécification de Device et aux distances. Le relecteur n'importe pas la construction par retournement de bits de l'auteur.

L'exponentielle exp(-iHt) est calculée par série de puissances matricielles après réduction à une norme de lignes au plus 0.25, puis carrés successifs. Le terme de série est arrêté au-dessous de 1e-18, au plus 79 termes; ce critère numérique n'est pas une borne d'intervalle. Aucun numpy.linalg.eigh, Hamiltonien QuTiP ou oracle du projet n'est utilisé dans ce recalcul. Les 54 cas à entraînement nul conservent gg. L'hermiticité de la matrice reconstruite est satisfaite.

Écart maximal contre l'oracle diagonalisation de l'auteur : 3.064215547965432e-14. Écart maximal contre les probabilités SDK : 0.00047265280720587555, sous le seuil 0.005. Erreur maximale de normalisation, SDK inclus : 1.611415334501487e-09, sous 1e-8. Le maximum Hamiltonien enregistré 6.123233995736766e-17 concerne la matrice SDK au seul instant initial; il ne certifie pas l'identité des trajectoires temporelles complètes. Le recalcul pur Python prend environ 0.05 s et ne mesure pas le temps Pulser/ODE.

## Interprétation des conventions et contraintes

Le code convertit correctement nanosecondes en microsecondes; les amplitudes/detunings sont en rad/µs et les distances en µm. La base SDK est inversée explicitement par rapport à l'oracle. Les tolérances atol/rtol=1e-10 du solveur ODE ne sont pas des garanties globales et les probabilités ne concordent pas à 1e-10 avec le modèle nominal. Le protocole a préenregistré 5e-3; c'est ce seuil, et non une précision supposée du solveur, que les résultats soutiennent.

La frontière temporelle échantillonnée du pulse est une explication plausible de l'écart nominal/SDK. Le présent recalcul confirme la dynamique nominale et la taille de l'écart, mais n'isole pas causalement son origine. Toute phrase attribuant intégralement l'écart à un effet de frontière doit être appuyée par un contrôle temporel distinct ou rester qualifiée.

Les neuf sondes sont conservées : sept rejets pour géométrie, canal, limites d'amplitude/detuning, durée trop courte ou trop longue; une durée 101 ns acceptée après arrondi à 104 ns avec avertissement; un registre sans layout accepté bien que requires_layout=true. Ces observations ne doivent pas être transformées en neuf rejets ni en validation complète de QPU. La vérification du constructeur Device couvre un sous-ensemble des contraintes; les contrôles backend/layout physiques n'ont pas été exécutés.

Le relecteur n'a pas rejoué Pulser/QuTiP ni les sondes pendant les inférences C11; les résultats SDK sont audités comme traces intègres et confrontés au recalcul orthogonal. Les versions Pulser 1.7.2 et QuTiP 5.2.3 enregistrées fixent la portée de cette observation, pas toute version ultérieure.

## Limites et suite

Deux atomes, canal global, un pulse nominal, interaction finie, absence de bruit et modulation : pas de blockade parfait, bruit Pasqal, contrôle optimal ou extrapolation à une machine accessible. Les grilles ne sont pas une population naturelle et les phases globales de conduite peuvent préserver les populations. Ce run ne mesure pas l'agent, son abstention ou sa généralisation.

La compatibilité avec un QPU précis demeure unverified; qpu_backend_constraints_checked et qpu_executed restent false. Aucun compte ou calcul matériel. Le résultat permet de distinguer modèle mathématique nominal, séquence acceptée par SDK, vérifications partielles de spécification et compatibilité physique non établie. Un contrôle séparé de la forme temporelle échantillonnée serait l'extension pertinente pour expliquer l'écart numérique avant toute précision plus forte.
