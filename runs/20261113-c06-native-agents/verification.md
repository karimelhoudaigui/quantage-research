# C06 — vérification des données, résultat partiel et blocage

Corpus indépendant de l'intégrateur : 32 cas, deux familles, 16 groupes
appariés. Le premier annotateur a fourni 20 propositions/12 abstentions.
Le second rôle a relu les textes avant candidats : 31 accords, un désaccord
sur «optimiser» sans direction. L'arbitrage conserve le texte et les labels
originaux; private_gold.v2.json porte 19 propositions supportées et 13
abstentions. Pas d'annotation humaine aveugle, même modèle possible.

Les deux tâches natives sans dossier ont échoué par quota avant réponse;
aucun fichier candidat créé. Le bras documenté n'a pas été lancé après ce
blocage. generation_record.json conserve tâches, prompts, statut observé,
empreintes et métadonnées inconnues. Les performances des bras manquants sont
absentes, pas imputées à zéro ni à des abstentions. Aucun mock de candidat.

Le scoring baselines prévu au protocole a été exécuté : strict, couverture
0/19 et fausses acceptations 0/13; mots-clés, couverture 9/19, fausses
acceptations 5/13, risque parmi les 14 acceptations 5/14. Les 14 réponses
acceptées par mots-clés ont un certificat numérique valide; les cinq erreurs
de contrat subsistent. Pas d'intervalle de population pour ce corpus fini.

Question centrale de C06 bloquée : zéro réponse d'agent candidat évaluée.
Le logiciel de scoring est testé avec fixtures explicitement marquées hors
preuves scientifiques, dont trace manquante, ID dupliqué et certificat
numérique d'un mauvais contrat. Les gold ne sont pas importés par
quantage/agent_pipeline.py; ils sont utilisés uniquement hors ligne pour les
métriques dans quantage/evaluation.py.

Choix utilisateur : réutiliser des sorties existantes. Recherche du dépôt et
recherche Drive «QuantAge» sans trace trouvée. Chemin/lien demandé et attendu;
aucun identifiant, modèle, prompt ou token inventé. Une source reçue sera
conservée immuable, puis son protocole rétrospectif distingué d'une génération
prospective. Les baselines actuelles restent hashées et ne seront pas écrasées.
