# Dossier documentaire figé — bras avec documentation

MIS pondéré : x_i dans {0,1}; maximiser somme w_i x_i, contraintes
x_i+x_j<=1 pour toute arête. Une pénalité P>max_i w_i permet de minimiser
-somme w_i x_i + P somme_(i,j) x_i x_j. Chaque arête est comptée une fois.
Retirer un sommet d'une sélection infaisable diminue l'énergie puisque
w_i-P*d_i<0. À la frontière P=max w, un minimiseur infaisable peut rester
ex aequo. Le cas non pondéré est la construction classique de Lucas, §4.2,
https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2014.00005/full.
L'argument pondéré est explicitement donné ici; pas attribué à cette section.

Photonique : pour l'entrée mode 0 et U=R(b)diag(1,e^(i*phi))R(a), les amplitudes
sont c_b*c_a-s_b*s_a*e^(i*phi) et s_b*c_a+c_b*s_a*e^(i*phi). Les probabilités
sont leurs modules carrés, somme 1 dans le modèle idéal. Perceval Ry(theta)
emploie le demi-angle : R(a) correspond à Ry(2*a), pas au BS par défaut Rx.
Documentation Perceval 1.3, Beam Splitter conventions :
https://perceval.quandela.net/docs/v1.3/reference/components/unitary_components.html.
Une amplitude complexe, un échantillon ou une distribution avec pertes n'est
pas la même sortie que les probabilités idéales du contrat.

Pasqal : candidat à étudier pour MIS, pas un exécuteur universel de QUBO.
Interactions dépendant de la géométrie, contrôles et encodage des poids à
valider. Le Device est distinct du QPU; droits de compte et backend non
interrogés ici. Sources Pulser 1.8.0 :
https://docs.pasqal.com/pulser/v1.8.0/hardware/
https://docs.pasqal.com/pulser/v1.8.0/register/.
Quandela : simulation et acquisition physique distinctes; aucune probabilité
idéale exacte ne peut être revendiquée comme résultat de mesures physiques
de cette session. Source Perceval 1.3 Computer :
https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html.

Toutes les URL ont été consultées lors des revues du projet; ce dossier est
une synthèse QuantAge figée, pas une récupération dynamique. Aucun SDK/QPU
n'a été exécuté. Nationalité du fournisseur et localisation d'un job diffèrent.
