# C22 — pilote partiel, résultat inconnu conservé

Poids officiels Qwen3-8B-Q4_K_M acquis et hashés, runtime b12359. Une réponse connue sur les deux prévues, aucune formulation entièrement fidèle dans cette réponse. Le patch du cas 417127d82203 remplace littéralement l’implication par `x2 - x1 <= 0` : le sens est corrigé, mais une exclusion inventée rejette encore [1,1,0,0]. Le domaine candidat a une affectation contre deux pour la référence ; optimum 33 contre 78.

La tentative sur 29507bb778cc n’a aucune réponse ni métadonnée finale conservée. Cause, tokens consommés/générés et coûts restent inconnus, jamais zéro ; aucun rééchantillonnage. Un premier lancement avait échoué avant serveur à la garde disque. La réponse connue porte un runner result-missing dû à la déclaration erronée de fichiers 001 pour un seul cas ; le brut 000 et ses métadonnées sont présents. Le manifeste original n’est ni réparé ni remplacé.

Le préfixe natif de pensée est fermé et vide ; 37/37 couches sont effectivement déportées sur Metal pour la réponse connue. Cela ne démontre ni pensée latente absente, ni exécution uniquement GPU, ni fit à contexte 6144. Réponse connue : 1537 tokens d’entrée, 106 de sortie, 20,372 s ; phase 50,097 s, acquisition 64,563 s. Coût de la tentative inconnue et énergie indisponibles.

La revue bornée research/c22-observed-review.md/json/.audit confirme 223 contrôles et explicite son absence d’indépendance des données. Aucun nouveau modèle/solveur n’y est lancé. Ce pilote n’est pas un nouveau test et n’établit aucun gain de taille isolé. Suite : seconde réparation du seul cas observé, avec état matérialisé et provenance des réponses réelles.
