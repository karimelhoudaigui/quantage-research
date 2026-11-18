# Revue finale de la voie locale C07–C10

Objectif opérationnel : chaîne compréhension→formulation→sélection réellement
exécutée et évaluée sur deux familles avec preuves, article et état à jour.
Il est désormais réalisé dans une portée de prototype hybride borné; cela
n'établit pas la fiabilité générale d'agents scientifiques ou une nouveauté.

C07 authentifie les fichiers publics et le checkpoint par source, version,
licence et hash. Identités de modèles des archives déclarées par les auteurs;
aucune exécution de leurs codes. Le modèle local distinct est effectivement
chargé et observé sans API fournisseur. Poids Safetensors, pas code distant,
runtime hors ligne; versions, tokens, temps et traces conservés.

C08 : 32 générations sur 16 requêtes, deux conditions; résultat négatif de
schéma et de fidélité conservé. C09 : 16 autres requêtes dans groupes disjoints;
veto fixé avant réponses, encore une erreur et deux faux refus. C10 : correction
après consultation, donc régression explicitement rétrospective. Première v3
à une erreur conservée; v4 n'écrase ni son score ni le résultat réservé.
Les 48 réponses portent sur 32 requêtes uniques, pas 48 observations indépendantes.

Vérification : scripts/audit_local_agents.py réagrège les décisions et dénominateurs,
recalcule les optima MIS et probabilités depuis les problèmes enregistrés,
vérifie absence de fausse promesse QPU, intégrité des manifests, répartition des
groupes et totaux de tokens. Trois replays CLI sur cas connus ont le même texte
brut et les statuts attendus. Ce sont des intégrations, pas de nouveaux tests.

Indépendance : preuve du composant numérique C05 et labels/relecture C06 par
rôles distincts réutilisés. L'acquisition, les nouveaux prompts, veto et scores
sont auto-revus; quota natif toujours absent. Pas d'indépendance de modèle ou
d'annotation humaine aveugle démontrée. Les raisons libres du LLM ne sont pas
évaluées comme preuves; le générateur ne lit aucun gold et ne génère pas les
coefficients dans ces bras hybrides.

Relecture Mathbox proofread-math : parties modifiées des deux articles, chiffres,
IDs, notations, références et distinction réservé/développement. Pas de changement
de jeton mathématique aux équations originales. Contrôle statique LaTeX seulement;
pas de compilateur ni PDF validé. Commandes et résultats finaux dans
research/local-agent-validation.json.

Limite résiduelle : veto lexical borné, nouveaux synonymes et négations possibles;
absence de compatibilité physique vérifiée; coût machine/énergie et coût complet
de cette session non mesurés. Un zéro sur régression connue n'est pas un taux
populationnel. Nouveau protocole sur groupes encore inédits requis pour la
recherche suivante, avec v4 figé avant génération.
