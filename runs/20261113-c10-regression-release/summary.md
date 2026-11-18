# C10 terminé — prototype local utilisable

CLI : .venv-local-llm/bin/python -m quantage.local_agent_cli --request
examples/freeform-photon.json --record-dir REPERTOIRE_NEUF.
La chaîne génère un vrai contrat local, formule, vérifie et choisit la référence
locale avec candidat français non validé. Les demandes explicitement ambiguës
testées sont refusées, traces conservées.

Régression finale v4 : 7/9 supportés et 0/7 hors contrat acceptés sur les mêmes
propositions C09 connues. La première correction v3 à 1 erreur est conservée;
le résultat réservé C09 à 1 erreur ne devient pas zéro après coup.
Trois smokes reproduisent les textes de génération et passent les contrôles
d'intégration. La prochaine expérience scientifique doit utiliser de nouveaux
groupes indépendamment annotés. Aucun résultat de fiabilité générale ou QPU.
