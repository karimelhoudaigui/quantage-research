# C15 — vérification et limites

Les annotations des24cas concordent entre auteur et relecteur avant inférence.
Oracles indépendants : research/c15-annotation-review.md et c15-annotation-oracle.
Cœur dense et feedback : research/c15-code-review.md et c15-code-audit-v3.
Représentation algébrique, boucle et scorer : research/c15-v2-review.md,
c15-language-loop-audit et c15-study-audit-v2 (fixtures explicitement synthétiques).
Traces réelles et test partiel : research/c15-observed-review.md,
c15-observed-audit-v2. Leurs manifests completed attestent les calculs bornés,
pas une fiabilité générale ou une performance de réparation.

Résultat réel :16dev, aucune fidèle; une valide incorrecte (23F, objectif
correct, optimum31contre17). Test initial1observée/15absentes, arrêt SIGTERM
pour ressources et manifest failed. Ne pas transformer les absents en refus.
H15 reste inconclusive faute de comparatif complet. Les solveurs exécutés
sur le candidat de développement concordent, sans justifier le problème initial.

Les manifestes historiques de prototype dont les entrées ont changé sont
vérifiables dans des racines isolées avec leurs sources EXACTES authentifiées :
research/c15-code-audit-v2/source-snapshot et
research/c15-study-audit/source-snapshot. Ils ne certifient pas la v2 active.
Les versions actives ont leurs propres audits et source snapshots.

Le certificat évalue domaine faisable et objectif sur le cube entier,
relativement au contrat structuré annoté. Il n'est pas un oracle général du
texte; une contradiction alternative peut masquer des clauses sur les cas
infaisables. Graines/tokens/messages/propositions brutes conservés. Le décalage
UTCv1 est une limite de chronologie, non effacé par un hash valide.

Aucune génération de coefficients par le contrôleur, code candidat exécuté,
dépense externe, QPU, push ou publication. Le bruit Pasqal n'est pas simulé.
