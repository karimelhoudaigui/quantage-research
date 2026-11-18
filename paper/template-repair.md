# Formulation et réparation de programmes binaires par contre-exemples

QuantAge — étude contrôlée, 15 novembre 2026. Document de travail; maturité pour soumission non établie.

## Résumé

Nous étudions si un retour de vérification améliore les formulations explicitement produites par un agent. L'agent reçoit une sélection pondérée avec exclusions et plusieurs contraintes de budget, cardinalité, obligation, interdiction ou implication. Il propose toutes les variables, les coefficients de l'objectif et les contraintes. Un compilateur algébrique générique traduit sa proposition sans compléter les clauses manquantes. Un vérificateur exhaustif recherche des contre-exemples sur le cube binaire, relativement à une référence annotée séparément. Un nouveau test de seize problèmes compare génération directe avec deux candidats, auto-révision et révision guidée par vérificateur, à deux appels et plafond de sortie identiques. Les combinaisons de contraintes du test sont absentes des huit cas de développement. {{ABSTRACT_RESULTS}} Deux solveurs classiques réellement exécutés, DFS exhaustif et HiGHS, sont comparés sur les modèles candidats. L'étude repose sur une référence structurée fiable, un seul petit modèle et un corpus de convenance. Elle ne démontre pas une compréhension générale du texte, une méthode de synthèse nouvelle ou un avantage quantique.

## Question, motivation et antériorités

La question primaire est : **le retour d'un vérificateur améliore-t-il la fidélité des formulations sur des combinaisons de contraintes non vues au développement, à budget d'appels comparable ?** Les cycles initiaux C01–C14 motivaient cette question : ils validaient des formulations déjà codées ou rejetaient des variantes, sans montrer que l'agent pouvait intégrer lui-même de nouvelles combinaisons de clauses. Dans C11, le veto lexical réduisait les mauvaises acceptations de 44 à 12 mais les bonnes de 55 à 23. Le critère de rétention échouait. Ce résultat est une étude des limites, pas une solution efficace.

La boucle proposition, contre-exemple et révision a des précédents établis dans la synthèse guidée par contre-exemples : [Solar-Lezama et al., ASPLOS 2006](https://people.csail.mit.edu/asolar/papers/Solar-LezamaTBSS06.pdf) et [Solar-Lezama, APLAS 2009](https://people.csail.mit.edu/asolar/papers/Solar-Lezama09.pdf). Notre générateur stochastique n'accumule pas une contrainte de synthèse dont la satisfaction assurerait une progression; il peut ignorer un témoin et régresser. Aucune garantie de complétude de CEGIS n'est transférée au LLM.

[Self-Refine, NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/file/91edff07232fb1b55a505a9e9f6c0ff3-Paper-Conference.pdf) étudie l'amélioration avec retour produit par le modèle. Notre auto-révision à un appel supplémentaire n'est pas sa reproduction : elle ne génère pas un feedback dans un appel distinct. [OptiMUS](https://arxiv.org/html/2407.19633v4), [Opt-Verifier](https://arxiv.org/html/2605.29556v1), les valuations de diagnostic de [VeriSimpl](https://arxiv.org/html/2607.20474v2) et les obligations formelles de [SOVER](https://arxiv.org/html/2609.00728v1) sont des travaux proches. L'identité des valeurs et la conservation des optimiseurs sont déjà distinguées dans la littérature. La revue ciblée figure dans research/c15-method-positioning.md; elle n'établit pas l'absence d'antériorité. La contribution candidate est l'évaluation contrôlée des formulations complètes et de leurs réparations.

## Problème et sémantique évaluée

Une requête comprend un texte français ou anglais et des données JSON : nombre d'items, poids, coûts et exclusions. Les paramètres des clauses supplémentaires se trouvent dans le texte. Les variables binaires sont indexées de zéro à $n-1$ :

$$f(x)=\sum_{i=0}^{n-1}w_i x_i,\qquad x\in\{0,1\}^n.$$

Selon le texte, le domaine satisfait les exclusions, un budget, des cardinalités, des obligations, des interdictions et des implications :

$$x_i+x_j\leq1\ ((i,j)\in E),\qquad \sum_i c_i x_i\leq B,\qquad L\leq\sum_i x_i\leq U.$$

$$x_i=1\ (i\in M),\qquad x_i=0\ (i\in Z),\qquad x_i-x_j\leq0\ ((i,j)\in I).$$

Les lignes absentes du texte ne sont pas ajoutées. Une instance contradictoire exige une formulation complète, pas un refus de tâche. Les familles optionnelles sont B, L, U, M, F et I; les exclusions sont présentes dans chaque problème. F désigne ici la famille interdiction; le domaine faisable est noté D.

Le modèle émet exactement cinq champs : formulation, variables, sense, objective et constraints. Chaque poids, indice, coefficient et borne est écrit par le LLM. Le compilateur utilise un AST restreint aux entiers, variables, additions, soustractions et multiplications par constantes. Il n'exécute aucun code candidat, ne lit aucune référence et ne complète aucune clause. La proposition originale et la forme compilée sont conservées. Le format dense initial reste accepté sans changement.

Le certificat primaire exige l'égalité du domaine faisable et de l'objectif sur tout le cube :

$$\forall x\in\{0,1\}^n:\quad [x\in\widehat D]=[x\in D]\ \land\ \widehat f(x)=f(x).$$

Les calculs sont entiers exacts. Ce critère accepte les contraintes redondantes ou réordonnées mais rejette un objectif multiplié par une constante positive, même si les optimiseurs sont conservés. Nous rapportons séparément l'égalité des domaines et de tous les ensembles d'optimiseurs. Une instance infaisable peut passer avec une autre contradiction suffisante : ce certificat extensionnel ne prouve pas la présence structurelle de chaque clause, ni un modèle paramétrique correct après changement de données. Les scores faisables et infaisables sont donc séparés.

## Boucle exécutée

Le générateur propose un modèle complet. Le vérificateur parcourt les 2^n affectations et renvoie au plus trois témoins distincts dans l'ordre lexicographique. Pour chaque affectation, un désaccord de faisabilité a priorité sur l'objectif. Le modèle reçoit les booléens ou deux valeurs d'objectif, sans nom de clause, coefficient corrigé ni modèle de référence. Une erreur de format reçoit un message constant; l'absence de témoin aussi.

L'agent utilise ce retour avec la requête et sa réponse précédente pour proposer un nouveau modèle complet. Le comparatif C16 fixe une seule révision et continue même après une initiale fidèle afin de mesurer les régressions. Le contrôleur local permet un arrêt dès certification; toute démonstration sur développement reste distincte du test comparatif.

La référence annotée est lue par le processus de vérification, jamais par l'inférence. Le guidé ne reçoit que le feedback minimal. Cette séparation des entrées n'est pas une sandbox OS spécifique au gold. La boucle suppose donc un contrat structuré fiable : elle ne certifie pas automatiquement le sens de tout texte. La disponibilité et le coût d'une telle référence sont des limites centrales.

## Protocole et gel

Un rôle auteur distinct construit huit cas de développement et seize cas de test. Un second rôle annote les 24 textes sans ouvrir les labels auteur ni leur générateur; accord 24/24 avant génération, originaux conservés. Ces rôles distincts ne constituent pas une annotation humaine aveugle ou une indépendance de modèle démontrée.

Les signatures de développement sont {{DEV_SIGNATURES}}. Le test contient seize signatures de trois à cinq familles, toutes absentes du développement et des signatures C15, avec 4–7 items, huit textes français, huit anglais et trois références infaisables. Les mêmes primitives sont enseignées dans les instructions. Le corpus est synthétique et de convenance : aucune inférence de population ni absence de contamination du pré-entraînement n'est prouvée.

C15 avait conservé seize réponses de développement, aucune fidèle, puis un test initial interrompu pour ressources avec une réponse et quinze absentes. Sa question comparative reste non résolue; ces absents ne sont pas des refus. C16 utilise un nouveau corpus et un moteur quantifié. Deux appels de préflight précèdent l'unique révision des consignes et de l'ordre des champs; six autres appels complètent le développement sans répéter les premiers. Les huit cas ne constituent donc pas une estimation sous un prompt uniforme. Le test utilise ensuite une seule version figée. La première garde de placement GPU avait arrêté le serveur avant toute génération faute de logs suffisants; cette erreur d'instrumentation et ses sources sont conservées séparément. Aucun échec ou proposition n'est effacé.

La grammaire impose les cinq champs dans l'ordre formulation, variables, sense, objective, constraints; les constantes binary_ilp et max sont fixées par le langage de sortie. Les indices, coefficients, nombre de lignes et contenu de chaque expression restent produits par le modèle. Cet apport structurel n'est pas crédité comme une découverte autonome de la famille de formulation. Aucun prompt, coefficient, parseur ou sélecteur n'est modifié après la première réponse de test.

Les méthodes partagent la même proposition initiale. Chacune dispose de deux appels par cas, plafonnés à 384 nouveaux tokens, contexte total maximal 2048, dont 1663 pour l’entrée avec réserve complète de sortie :

| Méthode | Information du second appel | Choix final sans gold |
|---|---|---|
| Direct, deux candidats | Requête et instructions seules; autre graine | Validité de schéma, puis moyenne log-proba des tokens traités; égalité à la première |
| Auto-révision | Requête, proposition initiale, consigne générique | Seconde si valide au schéma; sinon première valide |
| Guidée | Même historique et retour minimal du vérificateur | Même règle que l'auto-révision |

Le score direct utilise la probabilité du jeton choisi rapportée par l'API épinglée, après ses traitements d'échantillonnage, EOS compris. L'acceptation ou le rééchantillonnage par la grammaire peut modifier la normalisation selon la branche du runtime. Ce score reste une heuristique de sélection, pas une vraisemblance brute ou une probabilité conditionnelle globale à la grammaire. Une révision conforme mais fausse peut remplacer une proposition correcte; aucune sélection par le certificat final ne masque cette régression. La comparaison primaire est guidée contre auto, avec le même sélecteur.

Checkpoint officiel [Qwen2.5-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/tree/91cad51170dc346986eccefdc2dd33a9da36ead9), révision 91cad51170dc346986eccefdc2dd33a9da36ead9, Q4_K_M, SHA-256 6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e. Moteur officiel [llama.cpp b12359](https://github.com/ggml-org/llama.cpp/releases/tag/b12359), build 1.0.0-dev, commit b1b770d90d94cad9e9ea5b993bdbc383a522fb28, Metal MTL0 sur Apple M2, quatre threads CPU. Les logs confirment 29 couches sur 29 déchargées sur GPU. Ce placement n'est pas une preuve d'exécution exclusivement GPU. Le résultat porte sur cette configuration complète, sans isoler l'effet de taille, quantification, runtime ou grammaire. Température 0.2, top-p 1, top-k 50. La graine initiale est dérivée du SHA-256 de l'identifiant; les seconds appels utilisent tous le décalage +1. Messages, tokens, temps et hashes avant/après sont conservés. Chaque phase est bornée à 1800 secondes, sans retry ni imputation.

H16 exige au moins trois formulations fidèles de plus pour guidée qu'auto sur seize cas, et au plus une régression guidée parmi les initiales fidèles. Ce seuil décrit le test fini, sans faire des seize cas un échantillon représentatif.

## Résultats de formulation et réparation

{{DEVELOPMENT}}

{{MAIN_TABLE}}

{{PRIMARY_RESULT}}

{{STRATA_TABLE}}

Les désaccords d'objectif sont mesurés sur tout le cube. Un rejet de schéma peut porter sur la syntaxe, les types, les indices ou les dimensions; il n’est pas nécessairement cosmétique. Une réponse invalide n'a aucune affectation comparée; ses désaccords numériques ne sont pas des zéros de justesse.

{{ERROR_TABLE}}

{{WORKED_EXAMPLE}}

## Solveurs et décision

Chaque modèle final valide est réellement traité par DFS exhaustif et scipy.optimize.milp/HiGHS, SciPy 1.13.1, limite de deux secondes. Les solutions HiGHS arrondies sont recontrôlées dans les contraintes entières. Les valeurs optimales et statuts sont comparés; des solutions distinctes mais également optimales sont admises. Une infaisabilité concordante ne crée pas de solution.

Le système choisit le solveur concordant le plus rapide **après avoir exécuté les deux**. Ce profilage inclut le coût complet; ce n'est pas un routeur appris ni une accélération nette. Les solveurs ne reçoivent que le candidat. Leur accord peut résoudre précisément un modèle infidèle; utilisable pour le problème initial exige aussi la fidélité.

{{SOLVER_RESULTS}}

## Budget et coûts

Le budget comparable porte sur deux appels et au plus 768 nouveaux tokens par bras et cas. Les entrées guidées sont plus longues : tokens et temps effectifs peuvent différer. Le test partage physiquement les initiales : 64 appels distincts, contre 96 attribuables à trois bras isolés. Ces deux comptabilités restent distinctes.

{{COST_TABLE}}

Les sommes de temps écoulé par réponse incluent la requête au serveur et son traitement, hors chargement. Les CPU par réponse sont ceux du client Python uniquement; le CPU serveur est mesuré par phase après son arrêt et conservé séparément. Ils ne mesurent ni l'énergie GPU ni le coût complet de session. Vérification, deux solveurs, développement et annotation ont aussi un coût; annotation, énergie et session complète ne sont pas chiffrées. Aucune dépense externe ou soumission QPU.

## Restrictions quantiques et étude initiale

L'ILP générale est résolue classiquement. Budget, cardinalité et implication ne donnent pas automatiquement un Hamiltonien réalisable sur atomes neutres. Passer à QUBO exige des pénalités et auxiliaires justifiés, puis un plongement et des contrôles compatibles avec un dispositif précis. Max-Cut classique et Quantum Max-Cut restent distincts. SpinPulse n'est pas présenté comme bruit Pasqal.

C12/C13 sont des validations logicielles séparées, pas une évaluation de la réparation C15 ni une condition QPU pour une contribution sur les agents. Perceval 1.3.1 : 486 évaluations idéales à trois modes/deux photons, 2916 probabilités, erreur maximale auteur 2.22e-16 et revue orthogonale 3.33e-16. Pulser 1.7.2/QuTiP 5.2.3 : 162 programmes à deux atomes, écart maximal de probabilité 4.73e-4 sous 0.005. L'accord Hamiltonien initial ne prouve pas l'identité des trajectoires. Une durée de 101 ns est arrondie à 104 ns; un registre sans layout accepté localement n'est pas une acceptation backend. Aucun run QPU.

Les conventions et équations historiques restaurées restent dans paper/archive/c11-c14-corrected-before-repair.md. Une corruption réelle d'antislashs dans le générateur avait abîmé les commandes et tronqué le Hamiltonien; ce n'était pas uniquement le copier-coller. Sources corrompues conservées, cinq expressions restaurées et régressions de conservation ajoutées. Les tableaux et displays multilignes sont testés. Sans compilateur LaTeX disponible, aucun manuscrit PDF compilé ou inspecté n'est déclaré.

## Limites et interprétation

L'étude observe ce que le modèle formule et répare effectivement, dans la portée d'un checkpoint, d'une graine par condition et de petites instances. Les combinaisons sont inédites mais les primitives connues. Aucun transfert à la chimie, l'ordonnancement, la photonique ou aux grands graphes n'est établi. Les coûts et plafonds de sortie affectent les résultats; les échecs de format sont séparés.

Le vérificateur coûte exponentiellement et suppose la référence correcte. Il juge une instance, pas un théorème général. Un domaine vide peut masquer des clauses manquantes. Le petit modèle et l'absence de baseline forte limitent la maturité; le Qwen2.5-1.5B historique C14 a été arrêté pour problèmes numériques/coût, avec 31 observations absentes jamais imputées. Une confirmation requiert plusieurs modèles et un nouveau corpus réservé.

La conservation des erreurs et la revue distincte renforcent la traçabilité sans établir la nouveauté. Le résultat principal doit être lu avec les réparations, régressions et coûts, y compris si H16 échoue.

## Reproductibilité

Le dossier runs/20261115-c16-quantized-repair conserve protocole, amendement, publics, annotations, adjudication, gel et phases séparées. scripts/run_c16_phase.py lance une phase avec runner borné dans une destination neuve, sans écrasement. Les commandes originales et entrées hashées sont dans chaque manifest. verification.md relie les annotations et oracles indépendants, les audits du compilateur et les contrôles des traces. Une revue distincte a signalé des défauts du nouveau driver avant son gel. Le quota des sous-agents s'est ensuite épuisé : les dernières corrections, les scores et ce manuscrit ont une auto-revue de l'intégrateur, sans prétention de revue indépendante finale. Les fixtures logicielles ne sont jamais des performances LLM.

Le manuscrit est reconstruit depuis les résultats par scripts/build_repair_paper.py. scripts/check.py contrôle registres et handoffs, pas la vérité scientifique. Les prototypes historiques restent identifiés séparément de la version active. Les cycles négatifs sont conservés.
