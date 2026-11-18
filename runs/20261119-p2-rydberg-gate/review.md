# Auto-revue du gate P2-RYD-00

**Auteur/relecteur : intégrateur. Indépendance : non.** La tentative de revue indépendante par sous-agent a échoué avant de lire les documents (`400 The requested model is not supported`). Ce rapport est une analyse interne et ne remplace pas l'avis demandé.

## Objections bloquantes

1. **Nouveauté.** La question large « agent qui formule et sélectionne pour atomes neutres » recouvre directement Dalyac et al. (arXiv:2607.25834v1), et la littérature voisine couvre le guidage de stratégie, les tests de code quantique et les audits de benchmark. Le candidat plus précis « fidélité intention physique → IR → Pulser/Device, abstention et oracle indépendant » est plausible, mais la recherche ciblée ne démontre ni sa nouveauté ni son intérêt minimal.
2. **Indépendance absente.** Pas de reviewer distinct; donc pas de protocole approuvé. Les deux sous-agents littérature/matériel précédemment sollicités ont aussi échoué avant rapport.
3. **Critère primaire et puissance.** H_A/H_B sont des orientations concurrentes; seuils, risque accepté, effet minimal, groupe statistique, taille et intervalle d'incertitude manquent. Un seul exemple de développement n'est pas une évaluation.
4. **Réemploi C13.** Les contrôles 101→104 ns et layout manquant sont des sondes déjà connues dans C13. Ils ne peuvent pas alimenter un score de nouveauté ou de généralisation. Il faut les garder seulement en tests de régression et réserver des cas/transformations distincts pour toute étude scorée.
5. **Sélection de solveur.** Exact dense vs simulation Pulser sur 2–3 atomes ne fournit pas de portefeuille comparatif ni de décision discriminante; ne pas prétendre avoir testé le routeur.

## Cohérence technique bornée

- Le Hamiltonien proposé correspond à la verticale C13 et la dimension dense `2^N` est praticable pour une petite instance; les conventions, unités et l'ordre de base devront néanmoins être testés par tests analytiques pour `N>2`.
- Un succès de construction Pulser/`AnalogDevice` n'établit pas l'admissibilité de backend/layout, le bruit réel ou un run QPU.
- La tolérance C13 `0.005` ne peut pas être transférée automatiquement à une nouvelle géométrie/taille/observable; elle requiert une justification.
- Le pipeline agentique du dépôt n'implémente pas une traduction IR Rydberg; un pilote LLM exige du code nouveau et un contrat de sortie vérifié. Ce code n'a pas été créé.
- Les fichiers C13 sont des données de développement historiques; aucune simulation ou génération n'a été relancée.

## Décision de l'auto-revue

Ne pas implémenter ni exécuter le pilote dans cette tentative. Clore le gate comme `blocked`; préserver les brouillons pour revue ultérieure. Aucun article ne peut présenter l'hypothèse comme résultat. Le test réservé reste non utilisé.
