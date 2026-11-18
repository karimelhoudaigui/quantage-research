# P2-RYD-00 — gate de nouveauté et de protocole

**Statut : `blocked` avant gel et avant expérimentation.** Date : 19 novembre 2026. Cycle de cadrage rattaché à `many_body` (dynamique Ising/Rydberg) et à `agent_learning` (formulation et choix de stratégie). Il ne clôt pas C23 et ne consulte aucun jeu réservé.

## A. Question prioritaire et lien à l'article

Question choisie dans `research/backlog.json` : dynamique Ising/Rydberg et validation SDK Pulser, déjà amorcée par C13. C19/H19 demeure une étude de réparation d'ILP classique; C12/C13 valident séparément des SDK, sans évaluer un agent quantique. La question candidate est : un vérificateur indépendant peut-il réduire les acceptations où la description physique, l'IR, l'Hamiltonien et la `Sequence` Pulser divergent, sans parvenir à une sécurité triviale par abstention?

## B. Sources et antériorités

Voir `research/quantum_agents_v2/01_LITERATURE_AND_NOVELTY.md` et `research/sources/index.json`.

- Dalyac et al., arXiv:2607.25834v1, décrit déjà un workflow agentique Pasqal jusqu'aux campagnes QPU et l'importance d'une revue experte.
- Sheng et al., arXiv:2610.25014v1, décrit un LLM humain-dans-la-boucle qui guide des stratégies sur un sous-système de pinces atomiques réel.
- QCoder, QTestBench, Quantum Leap et QEDIA couvrent déjà des aspects de génération, test, audit et vérification de programmes quantiques.
- L'abstract de Dalyac et al. dit 633 articles de corpus; l'introduction HTML v1 dit 526. L'écart est documenté et non résolu; aucun de ces nombres n'est utilisé comme résultat.

Le « workflow agentique quantique » général n'est donc pas une contribution candidate distincte. La sous-question de fidélité physique/SDK est plus étroite mais sa nouveauté reste non démontrée par la recherche ciblée.

## C. Faisabilité matérielle et modèle

C13 fournit un résultat local réutilisable : 162 séquences Pulser 1.7.2/QuTiP 5.2.3 à deux atomes, comparées à un Hamiltonien indépendant; écart probabiliste maximal `0.0004726528`, sous tolérance préenregistrée `0.005`. C13 a aussi observé une durée de 101 ns arrondie à 104 ns et un registre sans layout accepté en simulation alors que `requires_layout=true`. C13 n'est ni un run QPU ni une évaluation d'agent.

Le modèle proposé est restreint à quelques atomes ground–Rydberg, interaction finie `C6/r^6`, pulses globaux constants, état initial en base, évolution idéale sans bruit/modulation et observables de populations. Il exclut expressément calibration, hardware noise, pertes, contrôle local, optimisation de pulse, accès QPU et preuve d'avantage quantique.

## D. IR et contrat de contrôle

Le projet d'IR indépendante du SDK, l'équation du Hamiltonien, les unités, les hypothèses, les niveaux de vérification L1–L7 et les obligations d'abstention sont dans `research/quantum_agents_v2/03_QUANTUM_TASK_SPECIFICATION.md` à `05_VERIFICATION_CONTRACT.md`. Une construction locale acceptée, une simulation, une vérification `Device`, une validation backend et un run QPU restent des niveaux séparés.

Les contrôles 101→104 ns et layout manquant proviennent de C13. Ils peuvent servir uniquement de régressions de développement déjà connues; ils sont exclus de toute évaluation scorée. Il faudra des intentions et transformations inédites, avec références annotées indépendamment, avant une comparaison.

## E. Question et hypothèses

H_A propose qu'à budget et couverture contrôlés les vérificateurs diminuent les fausses acceptations et améliorent la couverture correcte par rapport à des baselines fortes. H_B propose que la baisse d'erreurs soit surtout obtenue par abstention, sans gain de couverture correcte à risque fixé. Les définitions opérationnelles, le critère primaire, le seuil d'effet minimal et les hypothèses de puissance ne sont pas gelés.

## F. Baselines et sélection de solveur

Baselines proposées : parseur/solveur déterministe à domaine explicite, LLM direct, LLM + contrôle de schéma, auto-révision à appels comparables, pipeline avec IR/vérificateurs, et garde-fous sans retour LLM. Aucune n'a été exécutée.

Le choix de solveur n'est pas testable scientifiquement sur une tâche à trois atomes où l'exact est trivial. Il reste exploratoire; un futur protocole devra fournir plusieurs méthodes réellement admissibles pour la même tâche et des régimes de coût différents, avec choix ex ante et coût complet.

## G. Pilote proposé — non gelé

Une tâche de développement illustrative à trois atomes et un pulse constant serait comparée à une matrice dense indépendante de dimension `2^N` et à Pulser local. Le maximum proposé est 300 secondes, une inférence Qwen2.5-0.5B au plus, un cas principal et quelques contrôles; aucun réseau, achat ou QPU. Cette durée est un plafond de conception, pas une exécution ni un quota estimé. Le protocole expérimental détaillé reste dans `research/quantum_agents_v2/09_EXPERIMENT_PROTOCOL.md`.

## H. Relecture et décision

Une revue indépendante de protocole a été demandée. Le sous-agent a échoué avant tout tour de revue avec `400 The requested model is not supported`; aucun rapport indépendant n'existe. L'intégrateur a fait une auto-revue bornée consignée dans `review.md`, qui n'est pas indépendante. Les deux rôles de recherche littérature/matériel avaient aussi échoué dans le contexte précédent. Cette absence est un blocage de processus, non une validation tacite.

## I. Exécution

Aucune implémentation Phase 2, génération LLM, simulation de nouveau cas, dataset ou expérience n'a été exécuté. Aucune graine ni réponse manquante n'est imputée. Aucun test réservé, C23, secret, compte QPU, réseau de modèle ou dépense externe n'a été utilisé. Aucun résultat empirique Phase 2 n'existe.

## J. Claims et manuscrit

Aucun claim de performance ou de nouveauté n'est ajouté comme vérifié. Le registre reçoit seulement un statut `inconclusive` indiquant que la nouveauté et l'évaluation restent non établies. Le manuscrit rappelle que C19 est classique et que le candidat Rydberg reste non testé; ses résultats et dénominateurs restent inchangés.

## K. Gate et suite

Gate de nouveauté : **non passé** pour la question large; **non conclu** pour le sous-angle. Gate de revue indépendante : **non passé**. Gate d'expérimentation : **bloqué**, aucune exécution autorisée par ce cycle. Reprendre uniquement après revue d'antériorité ciblée par une personne/revue indépendante disponible, question et métrique primaire révisées, annotation séparée, cas de développement distincts des sondes C13, protocole gelé et décision humaine. Le corpus C23 reste sans appel; aucun retry C28.
