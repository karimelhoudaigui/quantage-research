# Audit du dépôt et de la reprise

Point de départ : fee83eb4575198e3e142d41c621300b4d11361d8, arbre propre,
aucun run. check.py initial passe avec zéro claim; dry-run initial imprime
une commande sans la lancer. Code scientifique absent au départ.

Environnement constaté : Python 3.9.6 (/usr/bin/python3), bibliothèque standard;
commande `python` et `pdflatex` absentes du PATH. README utilisait `python` et
annonçait 3.10+; les commandes documentées deviennent python3, compatibilité
testée 3.9.6. Aucun téléchargement de dépendances ni lecture de secrets.

Corrections du runner : import sans effet de bord, validation explicite des
handoffs (pas des assert désactivables par -O), arrêt sur blocage, contrôle du
dernier run du runner avant reprise, messages exploitables pour verrou/arbre
sale, suppression du verrou sur erreur, arrêt du groupe de processus POSIX
sur timeout/interrupt. Les anciens artefacts d'échec sont conservés. Le
contrôle des claims valide types, chemins confinés au dépôt et rapport pour
claim vérifié; il ne certifie pas la vérité scientifique.

Vérification de reprise : tests de logiciel avec exécuteur injecté, sans
appeler Codex. Deux cycles simulés suivis d'une reprise d'un cycle conservent
trois handoffs distincts. Blocage, fichier manquant, timeout, arbre sale et
verrou arrêtent correctement. Popen/killpg mockés dans le test de terminaison.
Ce test ne prouve pas la terminaison réelle de tous les descendants d'un outil
externe dans chaque environnement. Aucun run Codex imbriqué n'a été lancé.

Le runner reprend le contexte par state/backlog/claims et les runs, pas par
un état caché du modèle. Les cycles manuels de cette campagne ont leurs
completion.json et passent check.py; le contrôle des prompt.md concerne les
invocations du runner lui-même. Un précédent run interrompu doit être examiné
et terminé ou explicitement résolu avant une nouvelle invocation.

Pas de commit, push, publication ou message externe. Un lancement futur du
runner exige d'abord revue et commit par l'utilisateur. Le verrou préexistant
n'est jamais supprimé automatiquement. Les durées bornent les invocations,
pas leurs tokens ni leur coût de raisonnement.

Tests et commandes finales : research/validation.json. Compilation LaTeX
indisponible; source relue et structure vérifiée, PDF non produit.
