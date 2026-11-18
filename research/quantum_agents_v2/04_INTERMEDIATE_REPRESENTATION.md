# Représentation intermédiaire scientifique — proposition

La représentation est une interface inspectable indépendante du SDK. Elle est provisoire jusqu'à revue des rôles formalisme, matériel et vérification.

## Champs attendus

1. `schema_version`.
2. `physical_system`: nombre d'atomes, niveaux, registre et coordonnées avec unités, hypothèses d'indiscernabilité/non-interaction si pertinentes.
3. `initial_state`: état de chaque atome ou état quantique défini, ordre de base.
4. `hamiltonian`: convention de signe, drive, désaccord, phase et loi d'interaction; `C6`/version Device si nécessaire.
5. `controls`: canal, global/local, créneaux, début/fin, durée demandée et arrondie, unités, continuité/modulation.
6. `observable`: distribution, valeur attendue ou probabilité, opérateur et post-traitement demandé.
7. `constraints`: appareil virtuel/documenté, limites prises en compte, temps/mémoire/précision, disponibilité des ressources.
8. `missing_information`: champs manquants et décision attendue (question, hypothèse explicitement autorisée, abstention).
9. `strategy`: algorithme/SDK, version, raison ex ante, préconditions, ressources estimées et niveau de preuve.
10. `claims`: séparations entre modèle vérifié, validation mathématique, séquence SDK, simulation, conformité Device et statut QPU.

## Unités et forme

Le parseur ne doit pas inférer silencieusement les unités. Les quantités sont normalisées dans des unités canoniques explicites et la valeur d'origine est conservée. Durée demandée et durée effective doivent être différentes si le SDK normalise; la différence interdit d'annoncer fidélité exacte sans autorisation sémantique documentée.

Le JSON doit avoir des clés fermées, types stricts, dimensions cohérentes et champs obligatoires conditionnels. Nombres non finis, clés inconnues, état de mauvaise longueur et indices hors plage sont refusés explicitement. Les champs absents ne reçoivent pas de defaults physiques implicites.

## Variantes et statut

Une IR valide n'est pas un certificat de fidélité au texte. Le registre de référence et la vérification sémantique sont distincts du parseur. Le code n'est pas commencé tant que le protocole n'est pas relu.
