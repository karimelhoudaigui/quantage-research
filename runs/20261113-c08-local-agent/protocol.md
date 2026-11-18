# C08 — agent hybride à LLM local, cas figés de deux familles

Préenregistré avant toute génération de candidat sur ce corpus. Base C07,
Git fee83eb avec arbre modifié. Le test de faisabilité C07 a seulement demandé
{"ready":true}; aucune requête de recherche n'y a été montrée au modèle.

Question agent_learning : un agent hybride dont la compréhension est proposée
par un LLM local couvre-t-il les paraphrases et abstient-il les tâches hors
contrat, au-delà des deux baselines déterministes ? Hypothèse discriminante :
couverture et erreurs peuvent différer; aucun seuil de réussite ni gain du
dossier documentaire n'est présupposé. Un résultat négatif est un résultat.

Population finie : C06 public_cases.json et private_gold.v2.json déjà figés,
19 tâches supportées/13 abstentions, annotations/relecture par rôles distincts.
Sélection avant génération : quatre premiers group_id lexicographiques par
famille (déterminée par schéma numérique n ou photons), toutes leurs requêtes,
soit huit groupes appariés et 16 cas. Aucun filtrage par label ou résultat.
Conserver le sous-ensemble et ses hashes avant run. Les groupes non sélectionnés
restent hors expérience; tous les cas C06 déjà conçus par des agents, pas des
humains aveugles. L'intégrateur connaît le protocole/annotations, le modèle ne
lit ni labels, sorties de référence, code, filesystem ou outils.

Modèle : Qwen/Qwen2.5-0.5B-Instruct, révision
7ae557604adf67be50417f59c2c2f167def9a775, Safetensors au SHA-256 acquis.
Transformers4.45.2, torch2.8.0, Python3.9.6, CPUfloat32, quatre threads.
Modèle local sans apprentissage, sans API payante, sans réseau pendant le run,
sans code distant ou poids pickle. Greedy do_sample=false, seed20261113,
max_new_tokens192 par requête, un appel de génération observé par couple cas/bras.

Le LLM propose un contrat compact : JSON exact {action, family, task, reason}.
action = propose/abstain; family = mis/photon; task =
maximum_weight_independent_set / ideal_single_photon_probabilities pour une
proposition, null pour abstention. Il doit reconnaître ambiguïtés, contraintes
supplémentaires, unités, observable et données invalides; pas inventer de résultat.
La donnée est copiée depuis l'entrée par le contrôleur, pas réécrite par le LLM.
Le contrôleur transforme une proposition conforme en problème normalisé,
formule déterministement, applique C05 et sélectionne la référence locale avec
Pasqal/Quandela comme simple piste unverified. Ceci n'est PAS un bras où le
LLM invente tous les coefficients; la décomposition fait partie de la méthode.

Bras A : instruction de périmètre et schéma compact. Bras B : même instruction
+ documents.md de C06 (formules et sources), sans exemple de réponse au test.
Ordre fixe : A puis B par cas, cas triés par ID; pas de nouvelle génération après
score. Comparer aussi strict et mots-clés sur exactement les mêmes cas.
Même budget de sortie par bras; le dossier ajoute des tokens d'entrée et ce
surcoût sera compté. Pas de prétention à budget de raisonnement égal.

Parser : JSON intégral exact, éventuellement un unique bloc de code JSON
englobant tout le texte. Pas de regex réparant les valeurs, de eval ou de
reconstruction d'une réponse absente. JSON invalide/tronqué, champs inconnus
ou tâche inconnue entraînent refus explicite. Conserver texte brut et parse.

Métriques : couverture sur supportées; fausses acceptations hors contrat;
abstentions explicites, refus de format/contrôleur; erreurs de compréhension
qui passent le certificat numérique; différence appariée A/B; par famille.
Rapporter nombre de générations, tokens réellement tokenisés/générés, durée
CPUprocessus/mur, chargement, fichiers modèle, versions, paramètres et coûts
externes0; coût matériel/énergie non mesuré. Pas de score de confiance, pas
d'intervalle de population ni affirmation statistique sur ce petit corpus.

Budget total : maximum1500s pour génération,192tokens par réponse,32réponses
au plus, arrêt sur exception ou dépassement. Une limite ne devient pas une
abstention scientifique. Scoring séparé <=60s sur les lignes réellement
terminées; aucun remplacement des manquantes. Revue numérique réutilise C05
indépendant; collecte et métriques C08 seront auto-vérifiées, quota natif absent.
Préserver les traces même si le modèle échoue. Aucun QPU/soumission/publication.
