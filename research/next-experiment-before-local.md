# Prochaine expérience prioritaire — proposée, non exécutée

Question : quels faux certificats numériques subsistent lorsque le problème
normalisé est proposé par un vrai LLM, et un vérificateur sémantique indépendant
les distingue-t-il d'une simple critique numérique ? Motivation : les six
intentions modifiées de C04 passent le certificat après la mauvaise normalisation.

Prérequis : quota pour annotateur/relecteur indépendant; endpoint ou traces LLM
réelles autorisées, modèle/version figés, budget externe explicitement permis.
Aucun de ces prérequis ne sera inféré d'une clé éventuellement présente.
Pas de QPU requis. Les contrôles actuels restent des baselines déterministes.

Avant collecte : constituer et figer un corpus inédit de deux familles, avec
annotation indépendante des variables, objectif, contraintes, unités, observable,
ambiguïtés et abstention attendue. Grouper toutes les paraphrases d'une même
intention dans le même split. Réserver tailles et variantes sémantiques;
les cas déjà consultés C01–C04 sont développement, jamais test aveugle.
Fixer effectifs et budget après connaissance des ressources, avant outputs.

Bras : LLM seul; même modèle avec dossier documentaire figé; mêmes propositions
passées aux vérificateurs locaux; contrôle sémantique à partir du texte original.
La dernière comparaison doit utiliser des propositions appariées, sinon la
variation de génération est confondue avec l'effet du vérificateur. Séparer
retrieval et régénération. Conserver tous les échecs et abstentions.

Mesures : fidélité du contrat annoté, validité des optima/probabilités,
fausses acceptations matérielles, couverture/risque sélectif, temps, tokens
et coût complet de chaque bras. Un LLM qui produit un optimum d'un autre
problème reste une erreur sémantique, même avec un certificat numérique.
Ne pas entraîner de politique sur ce test. Pas de revendication quantique.

Action locale immédiate lorsque les sous-agents sont disponibles : revue
indépendante aveugle de core.py, verification.py, des protocoles et données
brutes; ne transmettre aucune conclusion de l'auteur avant la revue.
