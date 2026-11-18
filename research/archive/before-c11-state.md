# État cumulatif — 13 novembre 2026

L'objectif opérationnel de cette campagne est réalisé dans une portée bornée : une chaîne hybride compréhension → formulation → sélection est exécutable et évaluée sur de vraies réponses d'un LLM pour deux familles. La fiabilité générale des agents scientifiques reste une question de recherche. Le test réservé comporte encore une erreur; la correction ultérieure est explicitement du développement.

L'utilisateur a autorisé la recherche publique après l'échec du quota natif. C07 a acquis des archives ouvertes et un checkpoint local; C08–C10 ont produit les preuves et le prototype. Aucun chemin privé n'est désormais attendu. Ne pas recommencer la recherche de traces ou les expériences déjà vérifiées.

Base Git : fee83eb4575198e3e142d41c621300b4d11361d8. Arbre local modifié, sans commit ni push. Les sources et résultats hashés des expériences sont conservés. Ne pas modifier un fichier référencé par un manifest; créer une nouvelle version et un nouveau cycle.

## Résultats établis et portée

- C01, runs/20261113-c01-foundation : 1 199 évaluations MIS pondéré (1 194 distinctes) et 125 circuits idéaux à un photon; accord des optima et probabilités avec les oracles. 36 346 états binaires, erreur optique maximale 2.22e-16; glouton sous-optimal sur quatre évaluations, écart maximal 2.
- C02, runs/20261113-c02-formulation : 2 225 mutations synthétiques, 795 effectives. Le contrôle faible accepte 267 erreurs. Le zéro de l'oracle complet est relatif à ce même oracle, sans mesure de détection LLM indépendante.
- C03, runs/20261113-c03-routing : 20 propositions manuelles, 14 non justifiées; fausses acceptations 13/4/0 selon les contrôles nom, modalité et portée. Six recommandations admissibles conservées. Recommandation conditionnelle seulement, aucune faisabilité physique prouvée.
- C04, runs/20261113-c04-transfer : défi manuel de 24 requêtes; strict, couverture 6/12 et erreurs 0/12; mots-clés, couverture 12/12 et erreurs 6/12. Les six mauvaises interprétations ont un certificat numérique valide. Pas de test aveugle.
- C05, runs/20261113-c05-semantic-contracts : audit par un auteur distinct, frontière externe explicite. Sur 67 propositions, les 23 acceptations de schéma invalides de verify direct sont corrigées et 11 contrôles conservés. Revue distincte de 109 cas concordante : 81 rejets au schéma, quatre rejets numériques, 24 acceptations attendues. Les résultats de l'ancien pipeline ne sont pas réfutés.
- C06, runs/20261113-c06-native-agents : corpus de 32 requêtes, 16 groupes, annotations relues avant candidats; 19 supportées et 13 abstentions après arbitrage d'une ambiguïté. Baselines strict 0/19 et 0/13; mots-clés 9/19 et 5/13. Les deux tâches natives échouent par quota avant réponse. Cycle historiquement blocked; aucun score natif imputé.
- C07, runs/20261113-c07-public-traces : 12 fichiers publics QCV/PQID à commits fixes, 70 enregistrements PQID dont 51 codes non vides reliés aux payloads. Aucun code d'archive exécuté ni score QuantAge attribué. Checkpoint distinct Qwen2.5-0.5B-Instruct acquis à révision fixe, hash Safetensors conforme au LFS et smoke réel hors ligne réussi.
- C08, runs/20261113-c08-local-agent : 32 réponses réelles sur 16 requêtes de huit groupes. Sur dix supportées et six hors contrat, hybride sans dossier : 5/10 couvertes et 2/6 fausses acceptations; avec dossier : 4/10 et 2/6. Contradictions famille/tâche dans les réponses photoniques, résultat négatif conservé.
- C09, runs/20261113-c09-heldout-guard : 16 réponses réelles sur les huit autres groupes, neuf supportées et sept hors contrat. Schéma non redondant, puis mêmes réponses avec/sans veto fixé avant génération. Sans veto : 7/9 et 3/7; avec veto : 5/9 et 1/7. Deux erreurs retirées au coût de deux acceptations correctes. Une entrée explicitement inconnue reste mal acceptée malgré un certificat numérique valide. Ce résultat réservé reste inchangé.
- C10, runs/20261113-c10-regression-release : correction post-hoc sur les mêmes réponses C09. V3 conserve une erreur; v4 accepte 7/9 supportées et 0/7 hors contrat, avec deux refus de supportées. Ce zéro est une régression connue, pas un nouveau test réservé. Trois intégrations réexécutent le modèle et reproduisent exactement trois textes connus, avec acceptation/refus/refus attendus.

Total scientifique C08/C09 : 48 générations sur 32 requêtes uniques, pas 48 observations indépendantes. Deux familles : MIS à poids entiers positifs sur au plus 12 sommets, photonique idéale à deux modes avec un photon d'entrée en mode 0. Les données numériques restent structurées; le LLM propose un contrat compact, la formulation et la référence sont déterministes. Aucun bras de génération complète des coefficients ou de politique apprise exécuté.

Registre : 14 claims, 11 verified dans leurs périmètres finis et trois refuted, tous conservés. Neuf cycles complete et C06 blocked historique. Complete signifie cycle terminé, pas hypothèse confirmée ni programme scientifique achevé.

## Utilisation et preuves

Commande réelle depuis la racine, avec un répertoire de traces neuf :

~~~bash
.venv-local-llm/bin/python -m quantage.local_agent_cli --request examples/freeform-photon.json --record-dir /tmp/quantage-demo-neuf
~~~

Le CLI génère un contrat local, applique le veto v4, préserve les données, formule, vérifie et résout avec une référence locale. Code 0 : accepté par le prototype; code 2 : abstention. semantic_certificate reste false. Le candidat français conserve hardware_readiness=unverified et qpu_submitted=false. Une QUBO n'est pas automatiquement réalisable sur Pasqal; aucun résultat simulé n'est présenté comme un run QPU.

Poids publics ignorés par Git dans research/external/models/, environ 1 Go. Environnement isolé .venv-local-llm/, dépendances dans requirements-local-llm.txt. Révision du checkpoint : 7ae557604adf67be50417f59c2c2f167def9a775. Python 3.9.6, torch 2.8.0, Transformers 4.45.2, CPU float32, quatre threads, greedy, seed 20261113. Aucun code distant, pickle de modèle ou authentification fournisseur; inférence hors ligne.

Messages, réponses, fins, tokens, temps, commandes, versions, empreintes et commit de départ figurent dans les generation/ et results/ des cycles. C08 : 26 788 tokens d'entrée, 2 015 de sortie, 378.40 s avec chargement; C09 : 6 702, 842 et 130.58 s. Achat externe nul; coût machine/énergie et coût complet de session non mesurés. Le smoke C07 et les trois intégrations C10 sont séparés des 48 générations scientifiques.

quantage/core.py, verification.py et contracts.py restent figés. scripts/audit_results.py contrôle les quatre premiers jeux; audit_continuation.py rejoue les 109 cas de revue comme données, sans exécuter replay_source; audit_local_agents.py réagrège les scores locaux, recalcule les solutions numériques, contrôle groupes, tokens et empreintes. Vérifications finales et relecture : research/local-agent-validation.json et research/local-agent-review.md. Article cumulatif : paper/article.md et paper/main.tex.

## Limites et prochaine action

Les revues C05 et annotations C06 ont des auteurs distincts; elles ne sont pas aveugles et leur indépendance de modèle n'est pas démontrée. Le quota a ensuite empêché les bras natifs. Les nouveaux prompts, veto, métriques et intégrations ont été vérifiés séquentiellement par l'intégrateur; aucune revue indépendante nouvelle n'est revendiquée. Les raisons libres du LLM ne sont pas certifiées.

Corpus synthétique apparié, sans population naturelle ni intervalle de généralisation justifié. C08 et C09 ont des cas différents : pas d'effet causal isolé du changement de schéma entre étapes. Groupes disjoints de génération, sans preuve d'absence de contamination du pré-entraînement. Le veto lexical peut manquer des clauses ou refuser des synonymes. Ni nouveauté, ni avantage quantique, ni compatibilité physique, ni calibration probabiliste établis.

Aucune dépense externe, soumission QPU, publication, push ou message externe automatique. Aucun secret lu ou copié. Aucun SDK quantique exécuté. Aucun compilateur LaTeX disponible : contrôle statique des sources, pas de PDF validé.

Prochaine expérience scientifique proposée, non exécutée : nouveaux groupes annotés et relus séparément, veto v4 et protocole figés avant génération, comparaison des mêmes réponses avec/sans veto. Tous les groupes C06 sont désormais développement pour les versions futures. Priorité à une revue indépendante du veto lorsque disponible. Voir research/next-experiment.md; les autres axes demeurent au backlog, sans résultat inventé.
