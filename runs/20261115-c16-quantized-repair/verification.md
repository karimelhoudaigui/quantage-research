# C16 — vérification finale dans le périmètre observé

Revue distincte : research/c16-observed-review.md/json, recherche/c16-observed-audit (chemin exact : research/c16-observed-audit/manifest.json). Le relecteur a utilisé un parseur AST, une énumération et des prédicats séparés du scorer, sans relancer de modèle ni solveur. 26 863 contrôles,63paires HTTP,50profils/100sorties solveurs contrôlées relativement aux domaines annotés séparément. Il est l’auteur du corpus et de travaux antérieurs du driver : absence d’indépendance humaine/de modèle, portée détaillée dans son rapport.

Les63réponses sont16initiales,16directes,16auto,5guidées initiales puis10guidées pour cas jamais tentés. Le54969ba6bb41 a une requête mais aucune réponse : inconnu, jamais régénéré. Direct1/16,auto1/16,guidé1/15 ; guidé final entre1et2sur16 et gain[0,1]. Aucun scénario manquant ne satisfait H16gain≥3.

Unique certificat fidèle79769e445d63 : référence infaisable et candidat contradictoire autrement ; aucune récupération des clauses ou réussite faisable établie. Tous les accords solveurs ne certifient que le candidat. Le manifest de la première partie guidée reste incomplet après ENOSPC ; hashes survivants après incident sont distingués des observations avant/après. Les coûts connus concernent63réponses, pas l’appel interrompu, l’énergie GPU ni la session complète.
