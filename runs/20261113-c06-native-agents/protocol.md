# C06 — vraies propositions d'agents natifs

Préenregistrement avant toute génération de candidats. Base : C05, commit
fee83eb4575198e3e142d41c621300b4d11361d8 et fichiers locaux hashés.
Question agent_learning : sur des requêtes inédites annotées séparément,
comment fidélité, couverture et décisions de solveur diffèrent-elles entre
règles et agents avec/sans dossier documentaire et vérificateur numérique ?

Corpus : public_cases.json écrit par le rôle problème/matériel, sans consulter
de candidat ni le nouveau module de validation. 32 cas (16 MIS, 16 optiques),
16 groupes appariés opaques. Deuxième rôle distinct relit private_gold.json
avant génération. Un désaccord de direction implicite «optimiser» sera résolu
explicitement et versionné avant le premier candidat; les versions et labels
originaux sont conservés. Les labels finaux sont private_gold.v2.json.

Hypothèse : le modèle natif peut couvrir des paraphrases refusées par le
contrôle exact; un vérificateur numérique ne peut à lui seul garantir le sens
du texte. Pas d'hypothèse d'amélioration obligatoire ni de chiffre attendu.

Génération : quatre tâches de sous-agents en contextes neufs (fork_turns=none),
deux familles x deux bras, un seul lot de 16 cas par tâche, sans régénération
après score. Bras A : instructions de schéma/périmètre seulement; bras B :
mêmes instructions + dossier de formules et sources matérielles. Les agents
lisent les consignes de projet nécessaires et leurs seuls cas publics; ils
ne doivent consulter ni gold, code du moteur, résultats, autres candidats ou
outils de calcul/recherche pendant génération. Cette restriction est une
instruction, pas une isolation filesystem : la limite sera déclarée.

Propositions réellement générées par l'outil natif de collaboration, fichiers
bruts conservés avec prompt exact, tâche, hashes et observation des heures.
Identité exacte/version du modèle, température, seeds d'inférence, tokens et
facturation non exposés : null/inconnus, jamais inventés. Une tâche d'agent
n'est pas assimilée à un appel unique d'API. Aucune API payante, QPU ou boucle
Codex imbriquée. Des coûts/quota de la session peuvent être consommés.

Sortie obligatoire par cas : id, action propose/abstain, problem, formulation,
solver et reason. Schéma explicite dans generation_instructions.md. Pour les
deux bras, mêmes propositions évaluées après frontière de types/données/routage
puis avec vérification numérique, sans modification/régénération. Les règles
strictes et mots-clés de C04 sont des références. Aucun apprentissage.

L'évaluation hors ligne utilise les labels uniquement pour compter fidélité
de contrat/action et faux refus; les gold ne sont jamais lus par la chaîne
d'exécution. Une proposition sur une intention non supportée reste erreur
même si sa solution est numériquement exacte pour son problème normalisé.
La vérification des paramètres originaux et des domaines est obligatoire dans
tous les bras avant exécution; seules des routines locales bornées sont appelées.

Métriques par famille et bras : demandes supportées couvertes, fausses
acceptations hors contrat, risque parmi les acceptations, action fidèle,
schema/données/routage rejetés, validité numérique et différence appariée
avant/après oracle. Conserver chaque proposition, chaque sortie et raison.
Sans score de confiance, pas de courbe de calibration. Corpus fini de défi,
labels de rôles utilisant potentiellement le même modèle; pas généralisation
statistique, test aveugle humain ou nouveauté. Aucun intervalle de population.

Budget génération : quatre tâches bornées par la session, pas de retry en
boucle; échec/quota conservé comme ressource manquante sans sortie inventée.
Scoring Python <=60 s, MIS n<=6 et modèle optique idéal deux modes/un photon.
Commandes, versions, hashes et manifest v2 pour scoring. Clôture après revue
indépendante des labels et de l'évaluation; le résultat peut être négatif.
