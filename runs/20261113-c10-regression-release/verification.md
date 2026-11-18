# C10 — prototype livré, régressions et intégrations séparées du test réservé

Régression v3 post-hoc : 7/9 supportés, 1/7 hors contrat accepté. Les deux faux
refus de synonymes et le cas d'entrée inconnue sont corrigés, mais un objectif
explicitement non décidé est désormais accepté parce que greatest est reconnu.
Cette nouvelle erreur et les fichiers v3 restent dans results/manifest.json.

Le module v4 donne priorité aux clauses de direction explicitement non résolue.
Deuxième régression sur les mêmes propositions C09, sans génération ni label
modifié : 7/9 contrats supportés acceptés, 0/7 hors contrat accepté, deux refus de
supportées. Par famille : MIS 4/4 et 0/4; photon 3/5 et 0/3. Les modèles numériques
acceptés sont vérifiés comme précédemment. Ce résultat est du développement
après consultation des cas et des réponses, PAS un nouveau test réservé.
Le résultat primaire C09 reste 5/9 et 1/7 avec son veto d'origine.

Trois intégrations CLI réexécutent réellement le checkpoint sur des cas connus
C09 : une photonique valide, une entrée inconnue (version v3), un objectif
inconnu (version v4). Les trois textes bruts sont exactement reproduits sur cette
machine/configuration. Statuts attendus 0/2/2, acceptation/refus/refus. Ce sont
des smokes/régressions, pas trois nouveaux cas indépendants ni une garantie de
reproductibilité inter-matériels. Logs, paramètres et sorties dans cli-* et
cli-integration*.json; source v3 du CLI archivée avant mise à jour.

Le CLI final quantage.local_agent_cli utilise v4, checkpoint local à révision
fixe et données originales. Répertoire de traces neuf obligatoire, historique
conservé, aucune lecture de gold ni réseau au runtime; aucune permission QPU.
Les raisons textuelles du modèle ne sont pas certifiées, et le veto lexical
reste un contrôle borné. Il peut manquer d'autres négations ou refuser d'autres
synonymes. Ne pas confondre zéro erreur sur la régression connue et fiabilité
scientifique générale; nouveaux groupes/annotations seront requis ensuite.

L'audit des composants mathématiques C05 est indépendant d'auteur; les nouveaux
veto, métriques et intégrations sont auto-vérifiés, quota natif indisponible.
scripts/audit_local_agents.py réagrège les résultats sans importer les modèles,
revérifie optima/probabilités, groupes disjoints, tokens, manifests et l'absence
de fausse promesse matérielle. Vérifications finales : research/local-agent-validation.json.
