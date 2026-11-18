# Reconciliation C17/C18 — auto-revue de l'intégrateur

15 novembre 2026. La commande et les empreintes sont dans c17-c18-capacity-audit-v2/manifest.json, status completed. Le premier audit a importé par erreur le parseur sans frontière de raisonnement ; son assertion a échoué, aucun résultat de modèle n'a changé. Source et manifest failed conservés. V2 appelle le véritable parse_thinking_proposal.

C17 : deux appels réels de développement, deux propositions conformes au schéma, aucune fidèle. Ils ajoutent notamment des cardinalités non demandées. C18 : deux autres appels réels, chacun atteint 1024 tokens sans fermeture du raisonnement, aucun modèle final admissible. Le premier record C18 est récupéré du HTTP original après une comparaison trop stricte du flottant top_p ; aucun nouvel appel pour ce cas. Ses temps client et muraux non persistés restent null. Les tokens, seed et requête proviennent des fichiers survivants, pas d'une enveloppe reconstruite avant exécution.

Les quatre réponses concernent les deux mêmes anciens cas de développement C16. Aucun test ni effet isolé de la taille, quantification, raisonnement ou grammaire. Les incidents C17 v1 ont précédé toute réponse modèle ; leurs métadonnées incomplètes restent conservées. Ni énergie GPU ni coût complet de session. Aucun QPU. Cette revue est séquentielle et ne constitue pas une revue indépendante.
