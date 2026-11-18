# C16 — moteur quantifié et réparation multi-contraintes

Préenregistrement du 15 novembre 2026, avant toute inférence C16.
La route a été définie avant acquisition; cette mise en forme lisible intervient
après son lancement, sans changement du comparatif.
Question : le retour d'un vérificateur améliore-t-il la fidélité des formulations
LLM sur des combinaisons de contraintes réservées au test ?

## Motif et portée

C15 conserve seize réponses de développement : aucune fidèle, une seule valide
au schéma en v2. Son test initial est arrêté pour ressources avec une réponse
sur seize et quinze absentes. Ce n'est pas une comparaison des méthodes.
C16 change runtime, quantification et taille du modèle; il ne mesure pas
isolément l'effet de la quantification ou de la grammaire. C15 reste immuable.

## Acquisition et faisabilité

Acquérir le binaire officiel llama.cpp b12359 macOS arm64 au SHA-256 publié
et le seul fichier officiel Qwen2.5-1.5B-Instruct-GGUF q4_k_m, à commit et
LFS SHA-256 épinglés. Conserver métadonnées, commandes et hashes observés.
Metal est une accélération classique locale, jamais un dispositif quantique.
Aucun secret, achat externe, entraînement ou QPU.

Préflight sur les deux premiers identifiants de développement, choisis sans
scores : un appel initial chacun, 384 nouveaux tokens, contexte 2048, au plus
180 secondes par appel. Deux appels maximum, sans retry. Si échec de mémoire,
temps ou décodage, arrêter et conserver les traces. Si viable, compléter
les huit initiales de développement, sans les compter une seconde fois.
L'instruction algébrique C15 v2 sert de base. Au plus une révision de prompt
sur développement avant test, avec source et raison archivées. Aucune
complétion canonique de coefficients ou de clauses.

## Nouveau corpus et oracle

Huit nouveaux cas de développement et seize nouveaux cas de test, français et
anglais équilibrés, n=4..7, exclusions et familles B,L,U,M,F,I. Développement :
primitives seules ou doubles; test : seize signatures de trois à six familles,
disjointes du développement. Nouvelles données, textes et identifiants : aucun
cas C15 test réutilisé. Trois cas test infaisables. Chaque famille change le
domaine faisable si elle est supprimée sous les autres contraintes.

Auteur distinct, annotation indépendante des textes publics avant lecture
du gold auteur. Conserver originaux, désaccords, arbitrage et hashes. Les rôles
LLM ne sont pas des annotateurs humains aveugles ou des modèles indépendants
démontrés. Corpus synthétique de convenance.

Même vérificateur entier C15 : faisabilité et valeurs d'objectif sur toutes
les 2^n affectations; feedback fermé d'au plus trois témoins distincts
lexicographiques, priorité faisabilité par témoin. Aucun nom de clause,
coefficient corrigé ou modèle de référence transmis à l'inférence.
La référence structurée est supposée fiable : pas de certificat général du
sens d'un texte libre. Rapporter aussi l'équivalence finie d'optimisation.

## Comparatif à figer avant test

Une initiale partagée, puis trois seconds appels : direct indépendant,
auto-révision sans oracle, guidée par feedback minimal. Deux appels par
bras et cas, 384 nouveaux tokens chacun, contexte maximal 2048, sans retry.
Température 0.2, top-k 50, top-p 1; graine dérivée de SHA256(ID), décalage
0 pour l'initiale et +1 pour chacun des trois seconds appels.

Même grammaire JSON dans les trois bras : exactement cinq champs et tableau
de chaînes pour les contraintes. Elle impose une forme, sans lire poids,
coûts, arêtes ou gold pour remplir coefficients, relations ou clauses.
Variables et objectif restent écrits par le LLM. Même compilateur linéaire
C15 v2. Déclarer toute aide structurelle supplémentaire de la grammaire.

Direct : validité de schéma puis moyenne des log-probabilités traitées,
égalité à l'initiale. Auditer la convention API et EOS; si ces scores sont
indisponibles, amender le sélecteur avant tout test. Auto et guidée : seconde
si schéma valide, sinon initiale valide, sans choix par le certificat final.
Les initiales fidèles continuent pour mesurer les régressions. Direct ne
voit jamais la première réponse; auto n'a aucun feedback de référence;
guidée ne reçoit que le feedback minimal.

H16 : au moins trois formulations fidèles de plus pour guidée qu'auto sur
seize et au plus une régression guidée. Secondaires : réparations de format
et mathématiques, désaccords faisabilité/objectif, tous les optima, strates
langue et faisable/infaisable, tokens et temps effectifs. Aucun intervalle
de population sur ce corpus.

Quatre phases de seize appels : 64 physiques et 96 attribuables aux trois
bras isolés. Limite 1650 secondes internes et 1800 secondes runner par phase.
Conserver partiels et absents sans imputation. Geler code, instructions,
corpus, labels et graines avant la première génération de test.

## Solveurs et restitution

DFS exhaustif et SciPy/HiGHS réellement exécutés sur chaque candidat valide.
Comparer statuts et valeurs entières; admettre des solutions distinctes
optimales. Choix ex post du plus rapide, coût des deux rapporté. Accord
de solveurs ne signifie pas fidélité; utilisable pour le problème initial
exige aussi le certificat. Aucun routage appris ou lien automatique de
l'ILP à un dispositif Pasqal.

Après revue indépendante, actualiser article, claims, état, journal et
handoff, même si résultat négatif ou bloqué. Les résultats C01–C15 sont
motivation; ils ne démontrent pas la réussite de la méthode.
