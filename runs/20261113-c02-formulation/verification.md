# C02 — vérification des certificats (auto-revue)

2225 propositions : 175 MIS x7, 125 optiques x8. Les mutations changent
effectivement la sortie contractuelle dans 795 cas. Le contrôle faible
accepte 267 de ces erreurs : 90 MIS (48 pénalités à la frontière,
42 suppressions d'arête) et 177 optiques (27 phases omises, 114 demi-angles,
36 mélanges incohérents). Le vérificateur exhaustif n'en accepte aucune.

Ce dernier chiffre dépend de l'oracle qui définit l'équivalence dans ce test;
ce n'est pas une mesure indépendante de capacité de détection sur du LLM.
Les 1430 autres propositions préservent les sorties de leur instance. Le
vérificateur exhaustif les accepte toutes. L'identité syntaxique rejette
notamment 175 changements de constante, 175 rescalings positifs, 125 phases
globales et 125 inversions d'ordre optique, bien que les sorties soient
identiques dans le contrat. Tous les détails par opérateur sont dans metrics.json.

Point négatif utile : inverser R(a) et R(b), changer le signe de phi ou déplacer
la phase sur l'autre mode conserve ici les probabilités. Ce test ne certifie
donc ni l'ordre physique du circuit ni les amplitudes complexes. La quantité
p0 est symétrique en a et b et dépend de cos(phi). Un observable insensible
à ces transformations ne peut les distinguer. Ne pas les compter comme des
erreurs manquées pour l'objectif «probabilités de sortie».

Contre-exemple K2 P=1 conservé dans raw.jsonl : première solution 01 correcte,
mais présence de 11 infaisable parmi les minimiseurs. Preuve et test unitaire
de frontière dans C01. Erreur optique et tolérance de C01 inchangées.
Pas de nouvelle calibration, données d'apprentissage ou appel externe.
Commandes, hashes et version dans results/manifest.json; données brutes
permettent de refaire les agrégats sans relancer le générateur.

Vérification indépendante indisponible (quota). Les opérateurs ont été
préenregistrés avant le run, choisis sur le domaine de développement.
