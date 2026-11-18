# C04 — couverture sémantique et abstention à code figé

Préenregistrement après C03, avant génération/exécution C04. Parent : C03
results/manifest.json. Git fee83eb et changements locaux hashés. Question
prioritaire : agent_learning, généralisation du contrat à l'entrée.

Hypothèse : le contrôle strict protège contre les intentions non supportées,
mais perd la couverture des paraphrases; une règle par mots-clés augmente la
couverture en acceptant aussi des changements d'objectif/observable.

Code core.py et verification.py figé depuis C01. 24 requêtes annotées avant
exécution : 6 canoniques (3 MIS de tailles 7,8,8, poids 1..5, seed 20261114;
3 circuits à angles aléatoires idéaux), 6 paraphrases équivalentes EN/FR
appariées aux précédentes, 6 intentions modifiées (objectif/contraintes ou
observable/bruit) sur les mêmes données, 6 schémas/données invalides.
Les étiquettes portent sur l'équivalence du contrat complet, pas seulement
sur le fait qu'une réponse donnée pourrait être une réponse valide plus forte.

Baselines : pipeline contrôlé figé; canonicalisation par mots-clés puis même
pipeline/vérificateur. Aucun LLM simulé. Le second est un parseur naïf explicite.
Métriques : couverture des 12 contrats équivalents, acceptations erronées des
12 autres, faux refus par sous-groupe, fidélité mathématique APRÈS parsing,
temps et coûts locaux. Recalcul exact des nouvelles tailles via oracle.

Séparation : C01–C03 développement; tailles 7–8 et textes C04 non utilisés
pour changer le moteur. Corpus de défi écrit par l'auteur connaissant le
parseur : pas un test aveugle ni un échantillon de population naturelle.
Pas d'apprentissage. Les paires sémantiques partagent leurs données, à déclarer.

Budget Python standard <=60 s, seed 20261114 pour génération. Zéro dépense
externe ni QPU, pas de test LLM disponible. Revue non indépendante.
Commande : python3 -m quantage.transferstudy --cases RUN/cases.json
--output RUN/results; provenance v2 avec seed/générateur et empreintes.
