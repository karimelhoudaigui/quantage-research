# C09 — contrat sans champ redondant et veto sémantique sur groupes réservés

Préenregistrement avant génération C09. C08 est conservé sans modification :
32 réponses, dont contradictions family/task de toutes les requêtes optiques;
deux intentions MIS incorrectes acceptées par chaque bras avec certificat fini.
Le dossier ajoute du coût sans gain de couverture observé sur ce pilote.

Question : sur les groupes C06 non présentés au modèle en C08, une proposition
sans famille redondante permet-elle d'exécuter les deux familles, et un veto
textuel borné réduit-il les acceptations hors contrat ? Hypothèses testables,
pas résultat anticipé. Ne pas confondre cohérence de schéma avec compréhension.

Séparation : tous les cas dont group_id n'est pas sélectionné C08. Soit huit
groupes,16cas, sans filtrage sur labels. Le checkpoint n'a jamais vu ces textes
en C08 et n'est pas entraîné. Les annotateurs/rédacteur ont accès au corpus
historique : cette séparation de générations par groupe n'est pas un test
humain aveugle ou un échantillon naturel. C08 est développement pour cette
révision de méthode; ne pas réunir les deux en un score aveugle.

Même Qwen2.5-0.5B-Instruct, révision7ae557604adf67be50417f59c2c2f167def9a775,
CPUfloat32, quatre threads, torch2.8.0, Transformers4.45.2, seed20261113,
greedy, max_new_tokens128, un appel par cas, pas de documentation supplémentaire.
Budget1200s. Aucun appel fournisseur, achat, QPU ou code distant.

Schéma exact : {action,task,reason}, task=maximum_weight_independent_set ou
ideal_single_photon_probabilities pour propose, null pour abstain. Le
contrôleur déduit la famille du task, copie les données et utilise la même
formulation déterministe. Pas de réparation des traces C08, pas de family
corrigé après coup. JSON intégral ou un seul bloc JSON englobant accepté;
aucun eval ou réparation des valeurs. Les réponses invalides sont conservées.

Interventions appariées sur chaque même réponse C09 : (A) types/données et
certificat numérique seulement; (B) ajout d'un veto textuel déterministe.
Règles figées AVANT les réponses : MIS exige direction maximum, poids et
incompatibilités explicites; refuse minimisation, comptage, cardinalité,
taille imposée et sommet obligatoire connus. Photon exige probabilités,
contexte idéal/cohérent et mode0; refuse amplitudes demandées, degrés,
post-sélection et phase explicitement mode0. Les données hors contrat restent
refusées par le contrôleur. Les règles sont un garde borné, pas un théorème
d'entailment sémantique universel; faux refus et erreurs résiduelles mesurés.
Le code ne doit contenir ni ID de cas, ni label, ni phrase spécifique C09.

Baselines strict/mots-clés sur le même jeu réservé. Mesures : couverture sur
contrats supportés, fausses acceptations, refus de format/données/veto,
acceptations de mauvais contrats avec certificat numérique, différence
appariée avant/après veto, par famille; tokens et temps réellement observés.
Les refus du contrôleur ne sont pas attribués à une bonne abstention du LLM.
Pas de nouvelle génération après score et pas d'ajustement des règles sur C09.
Scoring séparé<=60s, données manquantes non imputées.

Revue de calcul C05 indépendante réutilisée; génération/règles/métriques C09
auto-vérifiées, quota de sous-agents indisponible. Le résultat conclut seulement
sur ce pilote, jamais à une fiabilité générale, nouveauté ou avantage quantique.
