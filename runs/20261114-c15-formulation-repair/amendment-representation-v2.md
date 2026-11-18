# Amendement de développement — représentation algébrique, 15 novembre 2026

Les huit vraies propositions de développement v1 sont toutes non conformes
(une tronquée) : arités des vecteurs, listes d'indices confondues avec coefficients,
lignes mal formées ou champs supplémentaires. Leurs bruts/manifest restent intacts.
Aucun test LLM n'a été lancé et les paramètres du corpus de test sont inchangés.

Une seule révision de représentation et de prompt avant test : les contraintes
peuvent être des chaînes linéaires explicites telles que 3*x0+2*x1<=7. L'agent
écrit toujours les variables, coefficients d'objectif et toutes les contraintes.
Un compilateur AST générique exact normalise chaque expression en ligne dense.
Il ne lit ni coûts/poids d'entrée, ni budget, ni cardinalité, ni gold pour ajouter
ou réparer une clause; les erreurs de l'agent restent des erreurs. Aucun eval/exec.
Le parseur accepte aussi le dense historique, sans changer sa signification.

Nouveaux fichiers versionnés repair_language, repair_inference_v2 et
repair_study_v2; les sources des générations v1 restent figées. Les deux
formes alimentent le même noyau ILP/vérificateur/solveurs déjà audités.
Même prompt v2 et même frontend dans tous les bras, mêmes seeds et plafonds
2*384 tokens/appels. Revoir le compilateur indépendamment avant test.

Développement v2 : huit propositions initiales maximum pour contrôler ce format.
Le prompt v2 est ensuite figé, même en cas d'échec; aucune nouvelle adaptation
après lecture des réponses test. Le wrapper unique de fence JSON peut être retiré
explicitement et est signalé; ce n'est pas une correction de coefficient.
Un exemple de boucle CLI sur UN cas de développement, choisi par règle fixée
première ID avec modèle valide mathématiquement faux, peut employer au plus
deux réparations. C'est une démonstration séparée, jamais un score du test
ni une modification de ses budgets à une réparation.

La question primaire reste H15 guidée contre auto sur nouvelles combinaisons,
et non la comparaison v1/v2 qui est du développement consulté. Le certificat
est relatif au contrat structuré annoté; il ne prouve pas la traduction libre
du texte ou une nouveauté de CEGIS. Aucun QPU ou dépense.
