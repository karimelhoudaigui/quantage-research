# C09 — test par groupes réservés, sans modification après score

16 appels réels,16 cas dans huit groupes non générés C08; huit cas par famille,
neuf supportés et sept hors contrat. Même checkpoint,32+16=48 réponses primaires
sur 32 requêtes uniques au total C08/C09. Aucun entraînement. Greedy et corpus
figés;842tokens de sortie et6702d'entrée,130.583753125s avec chargement,
117.956992s CPU processus. Toutes les générations se terminent sur EOS.

| Méthode | Supportés couverts /9 | Hors contrat acceptés /7 | Risque parmi acceptations |
|---|---:|---:|---:|
| Strict |0|0|non défini|
| Mots-clés |6|4|4/10|
| Proposition v2 + données/numérique |7|3|3/10|
| Même proposition + veto textuel |5|1|1/6|

Le veto bloque deux acceptations erronées mais perd deux acceptations valides.
Les deux synonymes non reconnus sont greatest value (direction maximale) et
distribution (probabilités). Une entrée explicitement non spécifiée reste
acceptée car le garde cherche seulement la présence de mode0. Son certificat
numérique est valide pour l'entrée choisie silencieusement : pas fidélité du
texte. La raison du modèle dit pourtant que l'information manque, tout en
proposant l'exécution. Ce résultat n'est pas corrigé dans C09.

Sans veto : MIS 4/4 supportés et 2/4 hors contrat acceptés; photon 3/5 et 1/3.
Avec veto : MIS 3/4 et 0/4; photon 2/5 et 1/3. Donc le schéma non redondant permet
bien l'exécution des deux familles, mais ne prouve pas la fiabilité générale.
15 propositions conformes, aucune abstention conforme; une abstention brute
porte un task non nul et est rejetée au schéma. Les refus du contrôleur ne
sont pas crédités comme décisions correctes du modèle.

Les groupes C08 et C09 sont disjoints; sélection et labels préexistent aux
générations. L'intégrateur connaît le corpus, les labels viennent de rôles
d'agents et aucune indépendance de modèle/humaine n'est prouvée. Les métriques
et le nouveau veto sont auto-vérifiés. Les sorties et manifests restent figés.

Suite : C10 corrige le prototype sur ces données connues, avec résultat de
régression explicitement rétrospectif. Ne pas utiliser C10 pour remplacer le
résultat réservé C09 ou affirmer un taux populationnel nul.
