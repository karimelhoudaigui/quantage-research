# C15 — formulations et réparations guidées par contre-exemples

Préenregistrement du 14 novembre 2026 avant toute génération C15 de test.
Priorité utilisateur : élargir ce que l'agent formule, au-delà du refus de variantes MIS.

## Question et portée
Le retour d'un vérificateur améliore-t-il la fidélité des formulations explicites
sur des combinaisons de contraintes non rencontrées au développement ?
La sélection pondérée porte sur n=4..7 items binaires, poids/coûts entiers,
exclusions, budget, cardinalité inférieure/supérieure, obligations, interdictions,
implications. Les paramètres de contraintes se trouvent dans le texte public,
pas dans les données numériques. L'agent produit lui-même chaque coefficient,
relation et borne d'une ILP; aucun compilateur canonique ne complète ses clauses.

## Corpus et séparation
Auteur distinct c15_corpus : 8 cas développement, 16 test, FR/EN et tailles
équilibrés. Développement : B,L,U,M,F,I,BL,UF ; test : 16 signatures inédites
de 3 à 6 familles. Trois cas test infaisables, score séparé. Les cas test et
labels sont revus indépendamment avant inférence, originaux/désaccords conservés.
Ce sont des rôles LLM distincts, pas des humains aveugles ni une indépendance
de modèle prouvée. L'auteur connaît les bilans historiques, pas le futur code.
Aucun C01–C14 n'est un nouveau test pour cette méthode. Pas de preuve de
non-contamination du pré-entraînement; généralisation limitée aux combinaisons.

## Formulation et certificat
Exactement {formulation:"binary_ilp", variables:[0,...,n-1], sense:"max",
objective:[coeff_i], constraints:[[coeff_vector,"<="|">="|"==",rhs],...]}.
Chaque variable est binaire; liste explicite et correspondance aux indices public.
Objectif et coefficients entiers; <=32 lignes, coefficients/bornes bornés.
Toutes les 2^n affectations sont examinées : même faisabilité ET mêmes valeurs
d'objectif sur tout le cube. Contraintes redondantes/réordonnées admises. Rapporter aussi, séparément, égalité des ensembles faisables et des ensembles d’optimiseurs (équivalence finie d’optimisation), pour distinguer une échelle d’objectif équivalente du critère strict de valeurs.
Ce certificat strict rejette les échelles/constantes, même si les optima coïncident;
ce n'est pas un test de toute équivalence ILP. Pas de preuve de texte libre :
le vérificateur utilise un contrat structuré de référence annoté séparément.

Retour au modèle : erreur de schéma, ou au plus trois affectations distinctes
lexicographiques. Pour chaque x, priorité faisabilité avant objectif si les
deux diffèrent. Retour booléens de faisabilité ou deux valeurs scalaires,
jamais les coefficients, noms de clauses ni modèle corrigé de référence.
Une absence de témoin est signalée sans transmettre de modèle canonique.

## Comparaisons et budget
Même proposition initiale partagée, tirée une fois par cas pour réduire la variance.
Direct best-of-two : seconde génération indépendante du même prompt, autre seed,
sans voir la première dans son prompt et sans charger son fichier; choix par validité de schéma puis moyenne log-proba
des tokens générés, tie à la première. Aucun label/verdict pour ce choix.
Auto-correction : seconde génération voit la première et une consigne générique
de révision, sans oracle. Guidée : même historique et retour du vérificateur.
Auto et guidée : seconde si schéma valide, sinon première valide, sans utiliser
le certificat final pour sélectionner. Aucun retry supplémentaire.
Le modèle peut ainsi régresser; mesurer ce risque. La sélection directe différente
est explicite; la comparaison causale primaire est guidée contre auto (même règle).

Deux appels et plafond 2*384 nouveaux tokens par bras/cas; contexte <=4096.
Les tokens d'entrée, de sortie et temps réels restent mesurés et peuvent différer.
Coût déployé attribuable (deux appels par bras) séparé du coût physique de
l'expérience : une initiale partagée + trois secondes =64 appels test, pas96.
Tous les messages enregistrés. Même checkpoint Qwen2.5-0.5B de C07,
float32 CPU4threads, Transformers4.45.2/torch2.8, sampling temperature0.2,
top_p1, seeds déterministes par ID; même seed seconde pour les trois bras.
Format JSON uniquement; pas de réparation automatique par le contrôleur.
Le système finit après une réparation, puis certifie; ce cycle n'étudie pas
un nombre illimité d'itérations. Prompt pédagogie de primitives isolées et
exemple de format fixé; pas d'exemple à3+familles avant test.

## Hypothèses et métriques
H15 primaire : au moins3 formulations fidèles de plus pour guidée qu'auto sur16,
et pas plus d'une régression parmi les cas initialement fidèles.
Secondaires : direct best-of-two, taux réparation sur erreurs initiales,
régressions, erreurs de schéma vs erreurs mathématiques, proportion
d'affectations avec faisabilité/objectif incorrects. Scores séparés faisables/
infaisables; égalité extentionnelle sur une instance infaisable n'établit pas
la qualité structurelle de toutes les clauses ou un modèle paramétrique.
Le zéro d'erreur final est une propriété finie relative au contrat annoté,
pas une fiabilité générale. Corpus synthétique de convenance, pas de CI populationnel.

## Solveurs et décision
Deux solveurs réellement exécutés sur chaque modèle final valide : DFS exhaustif
et scipy.optimize.milp/HiGHS (limite2s). Compiler le candidat LLM seulement.
Comparer faisabilité entière et valeur optimale, pas égalité de x quand
optima multiples. Choix ex post du plus rapide concordant, avec temps sélectionné
ET coût total des deux exécutions/contrôles. Aucun portfolio appris ni gain
de routage préalable revendiqué. Désaccord/statut limite = anomalie explicite.
Le certificat original est séparé; on ne choisit pas un solveur par gold.
Pas de QPU ni d'extension matérielle nouvelle dans ce cycle.

## Phases, ressources et gel
Développement : jusqu'à8 propositions pour contrôler le pipeline, au plus une
révision de prompt sur développement; jamais réviser après lecture de test.
Geler code, instructions, seeds et labels avant la première génération test.
Chaque phase d'inférence <=1650s internes/1800s runner; arrêter sur échec/limite,
conserver partiels sans compter absents comme échecs/abstentions artificiels.
Quatre phases test (initial/direct/self/guided), chacune16 appels maximum.
Les feedbacks sont calculés dans un processus distinct qui lit le gold; l'inférence
ne reçoit que publics, historiques autorisés et feedbacks minimaux.
Métadonnées complètes, hashes avant/après, bruit absent, coût externe0.
Aucun entraînement, code candidat exécuté, secret, API payante, publication ou QPU.

Le protocole est une hypothèse et un plan jusqu'à l'exécution; résumé et handoff
seront écrits à partir des bruts. C01–C14 et les sources abîmées sont préservés.
