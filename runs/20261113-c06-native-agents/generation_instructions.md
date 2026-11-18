# Instructions communes des agents candidats

Vous recevez un lot de requêtes scientifiques et devez produire une
proposition structurée par requête, sans exécuter de solveur. La seule portée
locale disponible est (a) maximum du poids d'un ensemble indépendant d'un graphe
simple non orienté, 1<=n<=12, poids entiers strictement positifs; (b) probabilités
idéales à deux modes avec un photon initial en mode 0, rotation réelle R(t)
=[[cos(t),-sin(t)],[sin(t),cos(t)]], réseau R(b)diag(1,exp(i*phi))R(a), radians,
pertes nulles. Toute autre tâche, ambiguïté ou donnée invalide exige abstention.
Ne pas modifier silencieusement objectif, donnée, contrainte, unité ou observable.

Pas d'accès QPU, compte, SDK ni modèle de bruit validé. Référence locale requise;
fournisseur quantique français seulement piste documentaire à statut unverified.
Vous ne connaissez pas le nombre attendu de propositions/abstentions.

Renvoyer un tableau JSON strict, une entrée par ID, exactement ces champs :

- id : ID public inchangé;
- action : propose ou abstain;
- problem, formulation, solver : objets ci-dessous, ou tous null si abstention;
- reason : justification brève en français ou anglais, incluant ce qui manque
  en cas d'abstention. Ne fournir aucune solution prétendument exécutée.

Problem MIS : family="mis", n, edges (chaque arête [i,j], i<j), weights,
objective="maximize_weight", domain="binary", constraints="independent".
Formulation MIS : kind="qubo", linear liste de n entiers, quadratic liste de
[i,j,coefficient entier] avec i<j sans doublons, constant entier, sense
"minimize" ou "maximize". Métadonnée penalty optionnelle entière et cohérente
avec chaque coefficient quadratique si fournie. Les constantes ou échelles
positives équivalentes sont permises; préserver tous les optima demandés.

Problem optique : family="photon", a,b,phi copiés, input=[1,0], modes=2,
loss=0, observable="probabilities". Formulation optique : kind="linear_optics",
a,b,phi, phase_mode=1, input_mode=0, order="R_b P R_a", global_phase=0,
coherent=true, output="probabilities". Paramètres réels finis; convention et
ordre doivent correspondre à la demande. Les changements explicitement
équivalents pour la réponse testée sont permis mais doivent être justifiés.

Solver : local_solver="exhaustive_qubo" (MIS) ou "single_photon_amplitudes"
(optique), quantum_provider="Pasqal" ou "Quandela" respectivement, ou null
si aucune piste annoncée; hardware_status="unverified", execution_kind="local".
Ne pas inventer de compilation, d'accès ou de résultat physique.

Pendant génération : lire les consignes obligatoires de projet et le fichier
public assigné; ne lire ni vérité terrain, annotation, code du moteur,
résultats/rapports d'audit, autre candidat ou dossier non assigné. Ne pas utiliser
de calculateur, recherche web, API ou outils d'inférence supplémentaires. Vous
pouvez écrire uniquement la réponse JSON et un bref relevé des lectures/outils
effectivement utilisés dans les chemins assignés. Aucune correction après score.
Ces règles ne constituent pas une isolation technique de fichiers.
