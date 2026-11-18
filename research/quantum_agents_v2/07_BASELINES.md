# Baselines du benchmark — exigences

Baselines futures prévues pour les mêmes cas de test, mêmes versions/modèles et budgets comparables :

| Baseline | Définition forte et équitable | Ce qu'elle contrôle |
|---|---|---|
| A — déterministe spécialisé | Parseur et solveur exact, avec grammaire de demandes supportées annoncée. Il traite correctement les cas dans son domaine et s'abstient hors-domaine/ambigus. | Valeur d'un pipeline spécialisé sans LLM; aucune baseline volontairement faible. |
| B — LLM direct | Un LLM local, même prompt d'entrée, produit l'IR/réponse sans retour d'un vérificateur. | Capacité brute d'interprétation, à version et budget figés. |
| C — LLM + validation schéma | Même sortie LLM que B; ne garder que contrôles structurels/typage. | Effet du schéma et des erreurs de format. |
| D — auto-révision | Même LLM, second appel générique, appels totaux appariés au système de vérification. | Bénéfice d'une révision simple vs feedback spécialisé. |
| E — IR + vérificateurs + feedback | Parse → math/units → SDK/Device → diagnostics minimaux → révision bornée → acceptation/clarification/abstention. | Architecture ciblée; ne peut pas avaliser le gold lui-même. |
| F — garde-fous sans retour LLM | Réception d'une IR directe puis vérifications indépendantes et acceptation/refus; aucun « réparer automatiquement » | Valeur d'un contrôleur de sécurité par rapport à la génération d'agent. |

Tous les bras utilisent des données brutes conservées, un oracle externe au générateur, un plafond d'appels identique ou un coût total comparable, et des dénominateurs distincts pour supporté, ambigu, contradictoire et hors-domaine. Les versions C19 ne sont pas des baselines quantitatives de la tâche quantique.

## Limite du pilote

Un unique essai local de développement sur Qwen2.5-0.5B pourrait tester la chaîne de chargement, l'IR et les journaux. Il n'est pas un comparatif de ces baselines et ne permet pas de trancher H_A/H_B. Le seuil et la sélection du modèle pour un jeu réservé exigent une validation humaine et un protocole ultérieur.
