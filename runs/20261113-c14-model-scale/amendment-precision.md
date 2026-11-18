# Amendement C14 — précision CPU, 14 novembre 2026

Après une vraie réponsefloat16 composée de128exclamations et aucun JSON,
la configuration est interrompue; son manifestfailed et ses traces restent
conservés. Ce n'est pas un résultat de fidélité du modèle. L'origine numérique
est suspectée, pas encore établie avant les contrôles ci-dessous.

Contrôle prospectif : une passeforward sur le même premier prompt enfloat16,
puis une enbfloat16, compter logitsfinis/NaN/inf et argmax, sans génération de
réponse ni label. Budget300s chacune. Les poidsconfig sont bfloat16 et leur
carte officielle permet torch_dtypeauto; c'est une variante CPU à mémoire
comparable àfloat16, pas un nouvel achat ou runtime.

Si et seulement si les logitsbfloat16 sont tousfinis, lancer une nouvelle
matrice32cas dans generation-bfloat16/, avec mêmeinstruction/seed/budget128.
Ajouter vérification de finitude du premierprefill au runner, sans modification
du texte ou de v4. Préenregistrer séparément cette nouvelle configuration,
1650s interne/1800s runner. Aucun changement d'H14, de sélection ou de gold.
Si le diagnosticbfloat16 échoue, arrêter C14avecblocage documenté. Aucun retry
supplémentaire. Toute comparaison reste exploratoire, non causale entre tailles
et précisions; ne jamais supprimer l'échecfloat16.
