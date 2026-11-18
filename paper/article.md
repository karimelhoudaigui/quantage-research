# Formulation et réparation de programmes binaires par contre-exemples

QuantAge — étude contrôlée, 15 novembre 2026. Document de travail; maturité pour soumission non établie.

## Résumé

Nous étudions si un retour de vérification améliore les formulations explicitement produites par un agent. L'agent reçoit une sélection pondérée avec exclusions et plusieurs contraintes de budget, cardinalité, obligation, interdiction ou implication. Il propose toutes les variables, les coefficients de l'objectif et les contraintes. Un compilateur algébrique générique traduit sa proposition sans compléter les clauses manquantes. Un vérificateur exhaustif recherche des contre-exemples sur le cube binaire, relativement à une référence annotée séparément. Un nouveau test de vingt problèmes compare génération directe avec deux candidats, auto-révision et révision guidée par vérificateur, à deux appels et plafond de sortie identiques. Les combinaisons de contraintes du test sont absentes des huit cas de développement. Le direct obtient 15/20 formulations fidèles, l'auto-révision 12/20 et le guidé 13/20. Le gain guidé contre auto est de 1 cas; le critère H19 est non satisfait. Deux solveurs classiques réellement exécutés, DFS exhaustif et HiGHS, sont comparés sur les modèles candidats. L'étude repose sur une référence structurée fiable, un seul petit modèle et un corpus de convenance. Elle ne démontre pas une compréhension générale du texte, une méthode de synthèse nouvelle ou un avantage quantique.

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

Les calculs sont entiers exacts. Ce critère accepte les contraintes redondantes ou réordonnées mais rejette un objectif multiplié par une constante positive, même si les optimiseurs sont conservés. La colonne « Équiv. optimisation » exige conjointement le même domaine faisable et le même ensemble complet d'optimiseurs ; l'égalité des seuls optimiseurs est un diagnostic distinct, plus faible. La fidélité stricte exige en outre l'identité de toutes les valeurs d'objectif sur le cube. Une instance infaisable peut passer avec une autre contradiction suffisante : ce certificat extensionnel ne prouve pas la présence structurelle de chaque clause, ni un modèle paramétrique correct après changement de données. Les scores faisables et infaisables sont donc séparés.

## Boucle exécutée

Le générateur propose un modèle complet. Le vérificateur parcourt les 2^n affectations et renvoie au plus trois témoins distincts dans l'ordre lexicographique. Pour chaque affectation, un désaccord de faisabilité a priorité sur l'objectif. Le modèle reçoit les booléens ou deux valeurs d'objectif, sans nom de clause, coefficient corrigé ni modèle de référence. Une erreur de format reçoit un message constant; l'absence de témoin aussi.

L'agent utilise ce retour avec la requête et sa réponse précédente pour proposer un nouveau modèle complet. Le comparatif C19 fixe une seule révision et continue même après une initiale fidèle afin de mesurer les régressions. Le contrôleur local permet un arrêt dès certification; toute démonstration sur développement reste distincte du test comparatif.

La référence annotée est lue par le processus de vérification, jamais par l'inférence. Le guidé ne reçoit que le feedback minimal. Cette séparation des entrées n'est pas une sandbox OS spécifique au gold. La boucle suppose donc un contrat structuré fiable : elle ne certifie pas automatiquement le sens de tout texte. La disponibilité et le coût d'une telle référence sont des limites centrales.

## Protocole et gel

Un rôle auteur distinct construit vingt nouveaux cas de test. Un second rôle annote les vingt textes sans ouvrir les labels auteur ni leur générateur; accord 20/20 avant génération, originaux conservés. Les huit anciens cas de développement C16 sont réutilisés comme développement C19, sans nouvelle prétention de test. Ces rôles distincts ne constituent pas une annotation humaine aveugle ou une indépendance de modèle démontrée.

Les signatures de développement sont B, L, U, M, F, I, BI, LM. Le test contient dix signatures inédites dans tous les labels C15/C16, deux instances par signature : BFILM, BFIM, BFIMU, BFIU, FILM, FILMU, FILU, FIMU, FLMU, ILMU. Il contient cinq instances pour chacune des tailles 4–7, dix textes français, dix anglais et trois références infaisables. Tous les graphes étiquetés sont distincts de l’historique C15/C16 et entre eux, sans prétention d’unicité à isomorphisme près. Les deux langues ne sont pas des traductions appariées : leurs données diffèrent. Les mêmes primitives sont enseignées dans les instructions. Le corpus est synthétique et de convenance : aucune inférence de population ni absence de contamination du pré-entraînement n'est prouvée.

C15 avait conservé seize réponses de développement, aucune fidèle, puis un test initial interrompu pour ressources avec une réponse et quinze absentes. Sa question comparative reste non résolue; ces absents ne sont pas des refus. C16 avait tenté 64 appels et conservé 63 réponses, une observation guidée restant inconnue après saturation disque. Direct et auto donnaient 1/16 fidèle, guidée entre 1 et 2 sur seize : le gain maximal de un restait inférieur au seuil de trois, sans imputation. Le seul certificat observé concernait une référence infaisable. C17 (2B non-thinking) donne deux schémas valides mais aucune fidélité; C18 (même 2B thinking) atteint deux fois 1024 tokens sans réponse finale admissible. C19 change de modèle et de grammaire, sans isoler causalement ces facteurs. Ses deux premiers appels de développement précèdent une révision des chaînes vers une grammaire linéaire générique; six autres appels complètent le développement sans répéter les premiers. Le test utilise ensuite une seule version figée. Les gabarits de corpus réfutés et corrections mathématiques avant inférence sont documentés, sans sélection par les scores du modèle. Aucun échec n’est effacé.

La grammaire impose les cinq champs dans l'ordre formulation, variables, sense, objective, constraints; les constantes binary_ilp et max sont fixées par le langage de sortie. Les indices, coefficients, nombre de lignes et contenu de chaque expression restent produits par le modèle. Cet apport structurel n'est pas crédité comme une découverte autonome de la famille de formulation. Aucun prompt, coefficient, parseur ou sélecteur n'est modifié après la première réponse de test.

Les méthodes partagent la même proposition initiale. Chacune dispose de deux appels par cas, plafonnés à 512 nouveaux tokens, contexte total maximal 4096, dont 3583 pour l’entrée avec réserve complète de sortie :

| Méthode | Information du second appel | Choix final sans gold |
|---|---|---|
| Direct, deux candidats | Requête et instructions seules; autre graine | Validité de schéma, puis moyenne log-proba des tokens traités; égalité à la première; si les deux sont invalides, le choix reste invalide |
| Auto-révision | Requête, proposition initiale, consigne générique | Seconde si valide au schéma; sinon première valide; si les deux sont invalides, seconde invalide |
| Guidée | Même historique et retour minimal du vérificateur | Même règle que l'auto-révision |

Le score direct utilise la probabilité du jeton choisi rapportée par l'API épinglée, après ses traitements d'échantillonnage, EOS compris. L'acceptation ou le rééchantillonnage par la grammaire peut modifier la normalisation selon la branche du runtime. Ce score reste une heuristique de sélection, pas une vraisemblance brute ou une probabilité conditionnelle globale à la grammaire. Une révision conforme mais fausse peut remplacer une proposition correcte; aucune sélection par le certificat final ne masque cette régression. La comparaison primaire est guidée contre auto, avec le même sélecteur.

Modèle original [Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507), uniquement non-thinking selon sa carte. Conversion communautaire [bartowski Q4_K_M](https://huggingface.co/bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF), révision `ae44f08e1392f39c0e474af10c3ff8355c8b6688`, SHA-256 `2fde00ce69dd4899c70d020845e2638353015bba0fdf161b3eb965f2bca4464e` ; sa conversion n’est pas reproduite. Moteur officiel [llama.cpp b12359](https://github.com/ggml-org/llama.cpp/releases/tag/b12359), commit `b1b770d90d94cad9e9ea5b993bdbc383a522fb28`, Metal MTL0 sur Apple M2, quatre threads CPU. Les logs doivent confirmer les couches déchargées et un buffer Metal positif; ce placement n’est pas une preuve d’exécution exclusivement GPU. Température 0.7, top-p 0.8, top-k 20. Graine initiale dérivée du SHA-256 de l’identifiant; seconds appels au décalage +1. Messages, tokens, paramètres et hashes avant/après sont conservés. Chaque phase est bornée à 1800 secondes et chaque complétion à 180 secondes, sans retry ni imputation. Le premier lancement s’arrête avant toute inférence faute de réserve disque. Un second incident arrête l’auto-révision après treize réponses et avant l’appel suivant ; seuls les sept cas jamais appelés sont poursuivis avec les mêmes sources et graines. L’union 13 + 7 est contrôlée contre les 20 paires HTTP, sans répétition. Un nettoyage borné de fichiers Git temporaires classés déchets, anciens et fermés accompagne la continuation ; les objets valides et références restent intacts.

H19 exige au moins quatre formulations fidèles de plus pour guidée qu'auto sur vingt cas, et au plus une régression guidée parmi les initiales fidèles. Ce seuil décrit le test fini, sans faire des vingt cas un échantillon représentatif.

## Résultats de formulation et réparation

Développement C19 : 7/8 schémas valides et 5/8 formulations fidèles, avec deux réponses sous grammaire de chaînes libres puis six sous grammaire linéaire générique. Ces huit réponses restent séparées du test et ne mesurent pas une grammaire uniforme.

| Méthode | Schéma valide /20 | Fidèle /20 | Équiv. optimisation /20 | Utilisable /20 |
|---|---|---|---|---|
| Initiale, un appel | 20 | 13 | 13 | 13 |
| Direct, deux candidats | 20 | 15 | 15 | 15 |
| Auto-révision | 20 | 12 | 13 | 12 |
| Guidée | 20 | 13 | 14 | 13 |

H19 : critère non satisfait. Gain guidé contre auto : 1 cas, pour un seuil de quatre ; 1 régression guidée, maximum une. Parmi les 7 erreurs initiales, 1 réparation mathématique atteint la fidélité complète. Aucune réparation de format n'est observée.

Le direct à deux candidats obtient 15/20, soit deux de plus que le guidé. Sur les dix-sept références faisables : initiale 10, direct 12, auto 9, guidé 10 ; les trois références infaisables passent dans les quatre méthodes. Aucun résultat n'est perdu ou imputé dans C19. Tous les 80 appels terminent sur EOS et respectent le schéma, loin du plafond pour beaucoup de réponses : les limites mesurées concernent les formulations et leur révision, pas seulement le format.

Analyse descriptive après test : sept initiales sont fausses, dont deux budgets omis, une implication omise, une implication au mauvais indice, une cardinalité minimale omise, une maximale omise, et une implication inversée avec exclusion ajoutée. La guidée répare la cardinalité minimale, mais recopie exactement les six autres modèles initiaux faux malgré leurs témoins. Auto et guidée changent en outre un poids de 46 à 48 dans un modèle initialement correct (64 désaccords sur le cube), malgré le retour sans contre-exemple. Les optimiseurs restent ici identiques : l'accord sur le seul optimum aurait caché cette régression. Ces catégories sont explicatives et post-hoc, pas des métriques préenregistrées supplémentaires.

| Strate | Direct fidèle | Auto fidèle | Guidée fidèle |
|---|---|---|---|
| Langue : français (n=10) | 9 | 7 | 8 |
| Langue : anglais (n=10) | 6 | 5 | 5 |
| Référence : faisable (n=17) | 12 | 9 | 10 |
| Référence : infaisable (n=3) | 3 | 3 | 3 |

Les désaccords d'objectif sont mesurés sur tout le cube. Un rejet de schéma peut porter sur la syntaxe, les types, les indices ou les dimensions; il n’est pas nécessairement cosmétique. Une réponse invalide n'a aucune affectation comparée; ses désaccords numériques ne sont pas des zéros de justesse.

| Méthode | Désaccords faisabilité | Désaccords objectif | Affectations comparées | Régressions |
|---|---|---|---|---|
| Initiale, un appel | 17 | 0 | 1200 | 0 |
| Direct, deux candidats | 9 | 0 | 1200 | 0 |
| Auto-révision | 17 | 64 | 1200 | 1 |
| Guidée | 16 | 64 | 1200 | 1 |

### Exemple descriptif : réparation mathématique

Cas 66f7838312e1, choisi après scoring par le premier identifiant admissible; cet exemple ne constitue pas une nouvelle évaluation.

Composer une sélection pour le lot de décision C19-9. Les 4 expériences ont pour indices 0 à 3. Définir x_i dans {0,1}, où 1 indique que l'indice i est retenu. L'objectif est le maximum de la somme des weights des éléments retenus. Chaque paire de edges est une incompatibilité : ses deux indices ne peuvent pas être retenus ensemble. Le nombre d'éléments retenus est au moins 2. L'indice 2 doit obligatoirement être retenu. L'indice 3 est interdit dans la sélection. Retenir l'indice 0 impose aussi de retenir l'indice 1 ; la réciproque n'est pas imposée. Les conditions énumérées sont exhaustives; aucune autre restriction n'est demandée.

Données : poids `[24,33,24,21]`, coûts `[38,13,29,32]`, exclusions `[[0,3],[1,3]]`.

Initiale :

- Variables : `[0,1,2,3]`.
- Objectif : `[24,33,24,21]`.
- Contrainte : `"x0+x3<=1"`.
- Contrainte : `"x1+x3<=1"`.
- Contrainte : `"x2==1"`.
- Contrainte : `"x3==0"`.
- Contrainte : `"x0-x1<=0"`.

Révision guidée produite :

- Variables : `[0,1,2,3]`.
- Objectif : `[24,33,24,21]`.
- Contrainte : `"x0+x3<=1"`.
- Contrainte : `"x1+x3<=1"`.
- Contrainte : `"x2==1"`.
- Contrainte : `"x3==0"`.
- Contrainte : `"x0-x1<=0"`.
- Contrainte : `"x0+x1+x2+x3>=2"`.

Retour effectivement transmis : `{"kind":"counterexamples","witnesses":[{"expected_feasible":false,"kind":"feasibility","proposed_feasible":true,"x":[0,0,1,0]}]}`.

Verdict final guidé : fidèle sur le cube fini.

## Solveurs et décision

Chaque modèle final valide est réellement traité par DFS exhaustif et scipy.optimize.milp/HiGHS, SciPy 1.13.1, limite de deux secondes. Les solutions HiGHS arrondies sont recontrôlées dans les contraintes entières. Les valeurs optimales et statuts sont comparés; des solutions distinctes mais également optimales sont admises. Une infaisabilité concordante ne crée pas de solution.

Le système choisit le solveur concordant le plus rapide **après avoir exécuté les deux**. Ce profilage inclut le coût complet; ce n'est pas un routeur appris ni une accélération nette. Les solveurs ne reçoivent que le candidat. Leur accord peut résoudre précisément un modèle infidèle; utilisable pour le problème initial exige aussi la fidélité. Les portefeuilles et la sélection d'algorithmes ont une littérature classique, notamment [SATzilla](https://doi.org/10.1613/jair.2490); notre étiquette du plus rapide après exécution des deux solveurs n'est pas une sélection prédictive par instance.

80 profils candidats, soit 160 appels solveurs réellement exécutés; 80 profils concordants. Choix observés : {"enumeration_dfs": 71, "scipy_highs_milp": 9}. Temps total des profils : 1.221463 s; somme des seuls temps sélectionnés : 0.012508 s. Un candidat identique sélectionné dans plusieurs bras peut être exécuté plusieurs fois; ces profils ne sont pas des observations indépendantes. Les timers incluent la validation et les imports différés : le premier profil supporte notamment le premier import de NumPy/SciPy. La limite de deux secondes porte sur HiGHS, pas sur ces imports.

## Budget et coûts

Le budget comparable porte sur deux appels et au plus 1024 nouveaux tokens par bras et cas. Les entrées guidées sont plus longues : tokens et temps effectifs peuvent différer. Le test partage physiquement les initiales : 80 appels distincts, contre 120 attribuables à trois bras isolés. Ces deux comptabilités restent distinctes.

| Périmètre | Appels | Tokens entrée | Tokens sortie | Temps réponses (s) |
|---|---|---|---|---|
| Direct, deux candidats | 40 | 27274 | 4667 | 371.18 |
| Auto-révision | 40 | 30325 | 4582 | 373.77 |
| Guidée | 40 | 31438 | 4593 | 382.08 |
| Physique test | 80 | 61763 | 9260 | 748.06 |

Les sommes de temps écoulé par réponse incluent la requête au serveur et son traitement, hors chargement. Les cinq processus d’inférence (deux pour l’auto-révision interrompue puis poursuivie) totalisent907,255 s, dont 102,438 s de chargement, et 241,568 s de CPU client et serveur. Le CPU du parent qui nettoie les fichiers temporaires n’est pas compris dans ces chiffres. Le chargement supplémentaire de l’auto-révision est conservé ; ces durées ne sont pas des mesures de latence isolées.

Les CPU par réponse sont ceux du client Python uniquement; le CPU serveur est mesuré par phase après son arrêt et conservé séparément. Ils ne mesurent ni l'énergie GPU ni le coût complet de session. Vérification, deux solveurs, développement et annotation ont aussi un coût; annotation, énergie et session complète ne sont pas chiffrées. Aucune dépense externe ou soumission QPU.

## Restrictions quantiques et étude initiale

L'ILP générale est résolue classiquement. Budget, cardinalité et implication ne donnent pas automatiquement un Hamiltonien réalisable sur atomes neutres. Passer à QUBO exige des pénalités et auxiliaires justifiés, puis un plongement et des contrôles compatibles avec un dispositif précis. Max-Cut classique et Quantum Max-Cut restent distincts. SpinPulse n'est pas présenté comme bruit Pasqal.

C12/C13 sont des validations logicielles séparées, pas une évaluation de la réparation C19 ni une condition QPU pour une contribution sur les agents. Perceval 1.3.1 : 486 évaluations idéales à trois modes/deux photons, 2916 probabilités, erreur maximale auteur 2.22e-16 et revue orthogonale 3.33e-16. Pulser 1.7.2/QuTiP 5.2.3 : 162 programmes à deux atomes, écart maximal de probabilité 4.73e-4 sous 0.005. L'accord Hamiltonien initial ne prouve pas l'identité des trajectoires. Une durée de 101 ns est arrondie à 104 ns; un registre sans layout accepté localement n'est pas une acceptation backend. Aucun run QPU. La [documentation Pulser v1.8.0 sur le matériel](https://docs.pasqal.com/pulser/v1.8.0/hardware/) décrit encore des contrôles de géométrie, canaux, impulsions et layout distincts de l’acceptation d’une formulation abstraite ; cette version documentaire n’est pas la version1.7.2 exécutée dans C13. Le [manuel Perceval v1.3](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html) distingue simulation locale et exécution distante sur QPU ou simulateur. Aucun de ces manuels ne valide nos ILP générales sur un dispositif précis.

Les conventions et équations historiques restaurées restent dans paper/archive/c11-c14-corrected-before-repair.md. Une corruption réelle d'antislashs dans le générateur avait abîmé les commandes et tronqué le Hamiltonien; ce n'était pas uniquement le copier-coller. Sources corrompues conservées, cinq expressions restaurées et régressions de conservation ajoutées. Les tableaux et displays multilignes sont testés. Une compilation locale Tectonic 0.17.0 et une extraction PDFKit vérifient désormais le PDF ; le contrôle visuel porte sur les équations, les tableaux et l’exemple. Cette vérification de rendu ne remplace pas une revue scientifique. Les premières alertes de fonte et de débordement de code ont été corrigées dans un renderer C19 séparé, sans changer les sources historiques.

## Limites et interprétation

L'étude observe ce que le modèle formule et répare effectivement, dans la portée d'un checkpoint, d'une graine par condition et de petites instances. Les combinaisons sont inédites mais les primitives connues. Aucun transfert à la chimie, l'ordonnancement, la photonique ou aux grands graphes n'est établi. Les coûts et plafonds de sortie affectent les résultats; les échecs de format sont séparés.

Le vérificateur coûte exponentiellement et suppose la référence correcte. Il juge une instance, pas un théorème général. Un domaine vide peut masquer des clauses manquantes. L'évaluation principale C19 porte sur un seul modèle de 4B, une seule graine et un petit corpus, ce qui limite sa maturité; le Qwen2.5-1.5B historique C14 a été arrêté pour problèmes numériques/coût, avec 31 observations absentes jamais imputées. Le pilote posthoc C27 sur un modèle 8B est un cas de développement distinct et ne remplace pas une confirmation sur plusieurs modèles et un nouveau corpus réservé.

La conservation des erreurs et la revue distincte renforcent la traçabilité sans établir la nouveauté. Le résultat principal doit être lu avec les réparations, régressions et coûts, y compris si H19 échoue.

## Pilote posthoc C27 (hors évaluation principale)

Après C19, un unique appel local de second patch a repris un état de développement déjà observé dans C24/C22. Ce n'est ni un nouveau cas ni un test réservé : l'état initial et le premier patch n'ont pas été rééchantillonnés. La génération Qwen3-8B-Q4_K_M sous llama.cpp b12359 a traité 1 795 tokens d'entrée et produit 143 tokens jusqu'à EOS. Le préremplissage a pris 131,23 s (13,68 tokens/s) et la génération 10,84 s (13,10 tokens/s); ces observations d'un appel, sans comparaison contrôlée, ne constituent pas une mesure de débit généralisable. Flash Attention était activé et les caches K/V étaient `q8_0`; les journaux rapportent Metal et 37/37 couches déchargées, sans établir une exécution exclusivement GPU.

Un replay littéral de la lignée C19 → C22 → C24 → C27 puis une vérification entière des 16 affectations trouve un désaccord de faisabilité avant C27 et aucun désaccord de faisabilité ou d'objectif après. DFS exhaustif et SciPy HiGHS concordent ensuite sur l'optimum 78 et la solution `[1,1,0,0]`. Les détails, commandes, versions et empreintes sont dans `runs/20261117-c27-quantized-kv-v2/verification.json`; la réponse brute et le manifeste d'exécution restent conservés dans le même cycle.

Cette observation posthoc, n=1, ne modifie aucun dénominateur C19 et n'établit ni généralisation, ni effet causal du cache quantifié, ni nouveauté méthodologique. La réponse était complète avant l'arrêt du serveur; le serveur a nécessité une terminaison forcée après l'attente TERM, puis a été reap avec statut `-9`. La cause de son arrêt tardif n'est pas établie. À la clôture de C27, C23 restait sans appel : le prérequis C25 avait échoué et C27 utilisait une configuration différente. L'amendement prospectif et le résultat C28 sont décrits ci-dessous.

## Pilote de viabilité C28 (hors évaluation principale)

Après autorisation prospective, C28 a tenté une seule génération initiale sur un cas n=7 de développement non-C23, sous la configuration du driver C23 : Qwen3-8B-Q4_K_M, llama.cpp b12359, 6144 tokens de contexte, 30 couches Metal demandées, Flash Attention `auto` et caches K/V `f16` par défaut. La requête contenait 740 tokens. Le runtime a chargé Metal et déchargé 30/37 couches; ses journaux signalent le prétraitement des 640 premiers tokens à 126,05 s puis l'initialisation du sampler, mais la requête n'a pas rendu de réponse complète avant sa limite de 180 s. Le driver a conservé zéro réponse complète et aucun fichier de réponse HTTP; le nombre de tokens éventuellement produits mais non transmis reste inconnu. Le serveur a été reap avec statut `-9`; aucun marqueur explicite d'OOM n'apparaît, ce qui ne prouve pas une marge mémoire.

Le critère C28 échoue : aucune proposition complète et parser-valide n'a été obtenue. Conformément au protocole, il n'y a pas de retry et aucun appel au corpus réservé C23. Ce pilote opérationnel n'évalue pas la fidélité mathématique, ne modifie pas les résultats ou dénominateurs C19 et ne démontre ni une impossibilité matérielle générale ni une performance de population. Le résultat principal C19 reste inchangé.

## Reproductibilité

Le dossier runs/20261115-c19-instruct-repair conserve protocole, amendement, publics, annotations, adjudication, gel et phases séparées. La version active scripts/run_c19_phase_v2.py utilise le gel v2 et des destinations neuves sans écrasement ; scripts/run_c19_comparison_v2.py s’arrête au premier échec. La continuation scripts/continue_c19_comparison.py conserve les treize réponses auto d’origine et les sept restantes, puis le score lit test-self-union-v2/driver/raw.jsonl. Les réponses et manifestes d’origine restent accessibles séparément. La version v1 est un lancement avorté avant tout appel, conservé comme incident. Les commandes originales et entrées hashées sont dans chaque manifest. verification.md relie les annotations et oracles indépendants, les audits du compilateur et les contrôles des traces. Une revue distincte a signalé et fait corriger deux contrôles du scorer avant gel (moyenne NaN, réserve de contexte). Les annotations ont été figées avant accès au gold auteur ; une énumération séparée contrôle domaines, optima et nécessité des familles. Le recalcul final, distinct du scorer et fondé sur l’oracle séparé, contrôle23 506 contrôles, 80 paires HTTP et 160 sorties de solveurs. Son auteur a aussi construit le corpus : cette revue n’est donc ni aveugle ni indépendante de l’auteur des données. Le rapport final précise la portée exacte de chaque revue. L’auteur historique du compilateur a relu cette partie lui-même : cette relecture n’est pas indépendante. Les fixtures logicielles ne sont jamais des performances LLM.

Le manuscrit est reconstruit depuis les résultats par `scripts/build_c19_paper.py`. `scripts/check.py` contrôle registres et handoffs, pas la vérité scientifique. Les prototypes historiques restent identifiés séparément de la version active. Les cycles négatifs sont conservés.
