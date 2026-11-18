# C15 — revue indépendante de formulation et du protocole comparatif

Date : 2026-11-14. Auteur : sous-agent formulation, distinct de l'intégrateur.
Portée : schéma et mécanisme communiqués par l'intégrateur avant exécution C15;
pas de code C15 ni de sorties LLM audités dans cette version du rapport.
Lectures : AGENTS.md, README.md, agents/orchestrator.md,
agents/formulation.md, research/state.md, research/backlog.json,
research/claims.json, config/policy.json et résumés C11/C14.
Compétences : mathbox:proof-audit et mathbox:proofread-math.
Une distinction de rôle ne garantit pas une indépendance de modèle ou humaine.

## Question et verdict

Question prioritaire : une réparation LLM recevant un contre-exemple fini améliore-t-elle
la formulation explicite de sélections pondérées avec exclusions, budget et
cardinalité, par rapport à deux propositions directes et à une autocorrection,
sous le même plafond d'appels et de tokens générés ? Cette question répond à
agent_learning; elle dépasse les formulations déterministes de C11 sans
réutiliser C11 comme test aveugle. Les clauses budget/cardinalité sont dans le
domaine pris en charge et ne constituent pas des motifs de refus.

**Verdict principal : conditionnel à un contrat structuré fidèle et à une
implémentation exhaustive conforme.** L'implication mathématique du certificat
est correcte. Aucune performance expérimentale, généralisation sémantique ou
nouveauté n'est établie par cette revue préalable.

La proposition initiale retenait systématiquement le dernier essai direct,
sans exploiter la qualité de la première proposition. **Point corrigé lors du
préenregistrement communiqué ensuite** : sélectionner entre deux générations
indépendantes par validité syntaxique puis log-probabilité moyenne des tokens
générés; départager en faveur de la première. Cette sélection est autonome,
sans label ni vérificateur sémantique, mais reste une heuristique.

## Contrat mathématique

Les données publiques donnent une liste ordonnée de n items, leurs poids
entiers w_i, les exclusions E, et les clauses actives. Pour une sélection
x dans {0,1}^n, la sémantique canonique est

\[
 f(x)=\sum_{i=0}^{n-1}w_i x_i,\qquad
 F(x)=\bigwedge_{\{i,j\}\in E}(x_i+x_j\leq1)
       \land [\sum_i c_i x_i\leq B]
       \land [L\leq\sum_i x_i\leq U].
\]

Les crochets désignent seulement les clauses actives. Une cardinalité exacte
k signifie L=U=k; une borne absente ne doit pas être inventée. Le budget et la
cardinalité interagissent normalement avec les exclusions. Le problème peut
être infaisable; ce statut est un résultat mathématique distinct d'un refus du
LLM. Fixer avant génération les domaines des coûts/poids, les bornes valides et
la politique sur une clause contradictoire avec les données structurées.

Schéma compact transmis par l'intégrateur, adéquat sous ces conventions :

```json
{"formulation":"binary_ilp","variables":[0,1],"sense":"max","objective":[5,3],"constraints":[[[1,1],"<=",1]]}
```

Le schéma impose exactement les six champs montrés. `binary_ilp` déclare le
domaine binaire de toutes les variables; `variables` vaut exactement
`[0,...,n-1]`, avec x_i associé à l'item d'indice i dans l'entrée publique.
Chaque contrainte est un triplet `[a,relation,b]` de sens
`sum_i a[i]*x_i relation b`; `relation` vaut `<=`, `>=` ou `==`.
Les coefficients et membres droits sont entiers, sans conversion implicite;
les booléens JSON ne sont pas des coefficients entiers admissibles. La longueur
des vecteurs est n. Le plafond annoncé est 32 contraintes. C15 prévoit n≤7,
inclus dans le domaine général proposé n≤8. Les variables auxiliaires et les
changements de codage des items sont exclus du contrat de cette expérience.

La proposition contient les coefficients eux-mêmes. Le programme ne doit ni
construire les contraintes manquantes à partir des données ni remplacer des
coefficients fautifs. Rejeter un schéma invalide, avec son diagnostic de format,
reste permis. Conserver exactement le texte brut et toute extraction JSON;
ne pas créditer la réparation par un parseur comme une réparation du LLM.

Les contraintes redondantes, équivalentes ou réordonnées sont admissibles si
leur conjonction a la même table de vérité. En revanche, ce contrat impose les
valeurs d'objectif strictes, pas seulement l'ensemble des optima : les
changements d'échelle, de constante ou de sens d'optimisation sont exclus même
quand ils préservent les solutions. Ne pas annoncer une reconnaissance de
toutes les formulations ILP mathématiquement équivalentes.

## Certificat et contre-exemple

Le vérificateur doit parcourir exactement tous les éléments de {0,1}^n,
sans les filtrer par la faisabilité du modèle proposé. Il compare séparément
F(x) et F_hat(x), puis f(x) et f_hat(x), avec arithmétique entière exacte.
Comparer l'objectif sur tout le cube, même pour les points infaisables,
est le choix strict déclaré par l'intégrateur. Il reste non vacu pour une
instance infaisable et détecte des coefficients que l'ensemble faisable ne
permettrait pas d'identifier. Cette exigence est plus forte que l'équivalence
opérationnelle sur l'ensemble faisable.

Graphe de dépendances : annotation de l'intention → contrat structuré public
→ évaluateur canonique; proposition brute → validation de schéma → évaluateur
ILP proposé; leurs tables indépendantes → comparaison exhaustive → certificat.
La dernière flèche ne prouve pas les deux premières. Éviter toute dépendance de
l'évaluateur canonique au compilateur ILP ou au même constructeur de contraintes.

Matrice des obligations :

| Obligation | Statut de cette revue |
| --- | --- |
| Domaines, ordre des items, signes et sens définis | passé sous le schéma ci-dessus |
| Même F et même f sur le cube impliquent mêmes valeurs/solutions optimales | passé mathématiquement |
| Exhaustivité réelle, n borné, aucune affectation omise | conditionnel à l'implémentation |
| Arithmétique entière et absence de correction silencieuse | conditionnel à l'implémentation |
| Fidélité du contrat public à toute la phrase libre | non établi; revue d'annotation requise |
| Exécution et contrôle indépendant des sorties finales | non abordé ici |

En effet, les ensembles faisables sont identiques si les indicatrices F le
sont. Sur cet ensemble commun, les objectifs sont identiques; l'argmax et la
valeur optimale le sont donc. Si cet ensemble est vide, les deux problèmes sont
infaisables. L'inverse est faux : deux modèles peuvent avoir le même optimum
et des faisabilités différentes. Une unique solution numériquement correcte
ne remplace donc pas ce certificat de formulation.

Ordre conseillé, à geler avant sorties : erreur de schéma d'abord; sinon témoins
de faisabilité dans l'ordre lexicographique des vecteurs; sinon témoins
d'objectif; sinon succès. L'intégrateur a ensuite annoncé jusqu'à trois témoins
sur des affectations distinctes, sans nom de clause ni modèle corrigé. Le plafond,
l'ordre exact des types de divergence et la déduplication par affectation doivent
figurer dans le protocole. Exemples de retours autorisés :

```json
{"kind":"feasibility","x":[1,1],"expected":false,"proposed":true}
{"kind":"objective","x":[0,1],"expected":3,"proposed":2}
```

Ne transmettre ni nom de clause fautive, ni vecteur correct, ni modèle canonique,
ni ensemble de solutions optimales. Un diagnostic de format identifie seulement
le champ illisible ou sa forme attendue. Le succès peut être indiqué sans
divulguer de solution. Les nombres `expected` sont une information volontaire
de l'oracle : la méthode doit être décrite comme guidée par un oracle structuré,
et non comme un LLM ayant découvert seul toute la sémantique du texte.

Sondes minimales à inclure dans l'audit indépendant : omission d'une exclusion
détectable en x=(1,1); omission d'un budget de 1 avec coûts (1,1) au même point;
omission d'une borne de cardinalité minimale 1 détectable en x=(0,0);
égalité de cardinalité 1 remplacée par ≤1 détectable en x=(0,0);
objectif (2,3) remplacé par (3,2) détectable en x=(0,1).
Ces exemples sont des obligations de test proposées, pas des résultats C15.
Ajouter les cas n minimal, aucun conflit, budget nul, clauses inactives,
cardinalité impossible, contraintes redondantes, optima multiples, et ordre des
items permuté avec leurs données.

## Fuites, circularité et comparaison des bras

Le gold et les annotations privées servent à l'évaluation finale, jamais au
choix d'une proposition, d'un modèle, d'un seed, d'un décodage ou d'un solveur.
Le prompt ne reçoit pas de champs tels que `expected_model`, `gold_constraints`,
`correct_solver` ou `optimal_solution`. Les données publiques et leur ordre
restent identiques dans les trois bras. Inspecter les prompts sérialisés, pas
seulement le générateur de prompts. Ne pas choisir le sous-ensemble après
observation des sorties; séparer groupes d'instances, paraphrases et nouvelles
combinaisons de clauses avant la génération.

Partage de la première réponse entre bras : bon appariement causal si sa seed
et son prompt sont identiques et gelés. Le premier appel partagé est imputé à
chaque bras dans son budget de déploiement, mais n'est physiquement compté qu'une
fois dans le registre d'expérience. Les appels directs indépendants utilisent
des contextes sans accès au candidat opposé, ni au vérificateur, et des seeds
distinctes. Avec 16 cas, une initiale partagée et trois seconds appels donnent
64 appels physiques, contre 96 appels imputés aux trois politiques déployées.
Ces nombres décrivent le plan annoncé, pas des générations observées ici.

Pour une sélection directe autonome sans troisième appel, une option est de
choisir parmi les propositions de structure valide celle ayant la meilleure
log-probabilité moyenne par token généré, calculée avec les scores de génération
déjà disponibles; départager par l'indice. Ce score est une heuristique,
longueur/schéma sensibles, et ne mesure pas la vérité. Il ne consulte aucun
label ni le vérificateur sémantique. Ce choix a été retenu dans la version
préenregistrée communiquée après la première revue. Le score de la première
proposition doit aussi être publié, avec les scores de sélection utilisés.

L'autocorrection voit le premier candidat et une invitation générique à
vérifier/réparer. Le bras guidé voit le même candidat et les témoins définis
ci-dessus. Tous produisent une seconde proposition explicite; une première
proposition correcte peut régresser et cette régression doit être comptée.
Pas de sélection finale du meilleur des deux par comparaison au gold.

Le choix final communiqué conserve la seconde proposition des bras auto/guidé
si sa structure est valide, sinon revient à la première si sa structure l'est.
Cette même règle de repli syntaxique isole le contenu du feedback; elle ne
sélectionne pas en fonction du résultat sémantique final. La comparaison primaire
annoncée est guidé contre autocorrection; le direct à deux candidats est
secondaire. Même si le premier modèle est correct, le guidé reçoit seulement
l'absence de contre-exemple et l'invitation à préserver le modèle, puis emploie
son second appel prévu. Les régressions restent possibles et mesurables.

Les plafonds annoncés (deux appels par politique, max_new_tokens=384 par appel,
contexte plafonné à 4096) définissent un budget alloué égal. Les quantités
d'entrée et le coût réel divergent : la seconde requête guidée contient un
témoin et les bras de réparation voient le premier texte. Rapporter par bras
tokens d'entrée/sortie, temps, appels réellement terminés et coût du
vérificateur. Ne pas dire que les coûts réels sont identiques. Les sorties
manquantes restent manquantes, et les troncatures sont séparées des erreurs
sémantiques. Le temps CPU et les groupes limitent la portée des comparaisons.

## Solveurs exécutables et vérification indépendante

Le solveur reçoit l'ILP proposé, jamais une ILP canonique substituée. Une
énumération DFS complète des feuilles binaires, sans pruning non prouvé,
produit un optimum exact de ce modèle avec arithmétique entière. L'oracle de
vérification doit utiliser une autre voie (par exemple produits cartésiens ou
masques entiers) et les données canoniques. Une solution d'une ILP incorrecte
reste marquée numériquement valide pour le modèle et sémantiquement incorrecte.

SciPy HiGHS MILP est disponible dans l'environnement inspecté. L'adaptation
impose `c=-objective`, `integrality=1`, bornes [0,1] explicites, et traduit les
trois relations en bornes de LinearConstraint. Fixer time_limit et
mip_rel_gap=0; conserver status/message et contrôles de solution. Une solution
flottante arrondie est contrôlée en arithmétique entière; un timeout ne prouve
pas l'optimalité. Le manuel officiel confirme ces conventions et les statuts.
[Documentation SciPy 1.13.1](https://docs.scipy.org/doc/scipy-1.13.1/reference/generated/scipy.optimize.milp.html).

Le portfolio finalement annoncé exécute les deux solveurs sur chaque modèle
final de structure valide, puis sélectionne le plus rapide parmi les résultats
concordants. La concordance compare la faisabilité entière et la valeur
optimale pour le modèle candidat, pas l'égalité des vecteurs solutions : des
optima multiples peuvent légitimement produire des vecteurs distincts. Ce
contrôle ne consulte pas le contrat canonique. Un désaccord ou un statut de
limite est conservé comme anomalie, sans sélection silencieuse par le gold.

Ce portfolio est un diagnostic après profilage. Le coût réel comprend les deux
exécutions et le contrôle; le temps du solveur sélectionné est rapporté
séparément et ne remplace pas ce coût. Un temps unique est instable. Ne pas
revendiquer un routage préalable qui évite le solveur lent, une politique
apprise ou une supériorité universelle. Fixer les frontières de chronométrage
et préciser si le démarrage/import est inclus. Le portfolio et les
vérifications finales sont invisibles aux bras direct/autocorrection; le
certificat sémantique demeure une étape distincte.

Préflight effectué par ce sous-agent, sans écriture de code, poids ou secret;
il ne constitue pas une expérience LLM C15. Commande et sortie brute ci-dessous
servent de provenance locale de ce test unique.

```sh
python3 -B - <<'PY'
import itertools, json, platform, scipy
from scipy.optimize import Bounds, LinearConstraint, milp
w = [5, 4, 3]
A = [[1, 1, 0], [4, 3, 2], [1, 1, 1]]
lb = [-float('inf'), -float('inf'), 2]
ub = [1, 5, 2]
feasible = [(sum(a*b for a,b in zip(w,x)), x) for x in itertools.product((0,1), repeat=3) if x[0]+x[1] <= 1 and 4*x[0]+3*x[1]+2*x[2] <= 5 and sum(x)==2]
res = milp(c=[-a for a in w], integrality=[1,1,1], bounds=Bounds([0,0,0],[1,1,1]), constraints=LinearConstraint(A, lb, ub), options={'time_limit':2.0,'mip_rel_gap':0.0})
print(json.dumps({'python':platform.python_version(),'scipy':scipy.__version__,'enumeration_optimum':max(feasible)[0],'enumeration_optimizers':[list(x) for v,x in feasible if v==max(feasible)[0]],'highs_status':int(res.status),'highs_x':res.x.tolist() if res.x is not None else None,'highs_max_objective':float(-res.fun) if res.fun is not None else None}))
PY
```

```json
{"python":"3.9.6","scipy":"1.13.1","enumeration_optimum":7,"enumeration_optimizers":[[0,1,1]],"highs_status":0,"highs_x":[0.0,1.0,1.0],"highs_max_objective":7.0}
```

Ce test valide une disponibilité/exécution minimale, pas le futur adaptateur
C15, ni toutes ses relations ou sa gestion des cas infaisables. Aucun QPU,
compatibilité Pasqal, bruit ou avantage quantique n'en découle.

## Suite nécessaire et relecture

Avant génération : figer sélection directe et schéma; relire les nouveaux
groupes/combinaisons; préserver les annotations avant accès aux sorties;
préenregistrer protocole, seeds et plafonds. Après implémentation : audit
indépendant des deux évaluateurs, des 2^n affectations et des témoins, puis
audit des prompts et du routage. Après sorties : matrice format/faisabilité/
objectif/certification/solution par bras, gains et régressions appariés par
groupe, coûts réels et données manquantes. Aucun quota indisponible constaté
pour ce sous-agent; l'historique des quotas C11/C14 reste inchangé.

Relecture mathématique de ce seul fichier : domaines, indices, signes,
cardinalité exacte, ensemble vide, convention max/min et frontières de la
garantie relus. Modifications de jetons mathématiques après rédaction : aucune.
Question restante principale : fidélité de la traduction texte→contrat public;
ni le certificat fini ni le témoin ne ferment cette obligation.
