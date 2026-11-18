# C11 — état de l’art primaire et positionnement borné

Revue ciblée effectuée le 13 novembre 2026. Skill `mathbox:literature-check`
appliquée; sources primaires rouvertes, sections précisées ci-dessous. Aucun
résultat externe reproduit; aucune affirmation de nouveauté établie.
Les sources de C01–C10 servent de points de départ, sans remplacer la nouvelle
consultation. Les fichiers communs, le manuscrit et les preuves historiques
n’ont pas été modifiés par ce rôle.

## Conclusion utile au protocole

Ajouter un contrôle sémantique, décomposer des agents, mesurer l’abstention ou
orchestrer un workflow quantique ne suffit pas à distinguer QuantAge. Les
travaux récents ci-dessous couvrent déjà ces dimensions. La piste défendable
reste un test borné de propagation des erreurs entre contrats scientifiques,
formulations et vérifications logicielles/matérielles documentées, avec
annotations distinctes et mêmes propositions comparées avant/après contrôle.
Ce positionnement est une proposition à tester, pas une lacune mondiale prouvée.

## Matrice comparative

Les champs sont des résumés des seuls passages consultés. Une absence dans la
colonne matériel signifie «non traité dans les sections vérifiées», pas une
affirmation universelle d’absence dans tous les travaux des auteurs.

| Travail | Problèmes / méthode | Mesure ou certificat | Limite décisive pour QuantAge |
|---|---|---|---|
| [nl4opt](https://proceedings.mlr.press/v220/ramamonjison23a/ramamonjison23a.pdf) | LP word problems; entities then meaning representation, with gold entities supplied to formulation subtask | Micro F1 for entities; canonical declaration matching for formulations | Gold entities simplify generation; not a certificate of natural-language faithfulness |
| [optimus](https://arxiv.org/html/2407.19633v4) | MILP; modular parameter/clause extraction, mathematical model, solver code and correction | Execution plus optimum/solution agreement when references exist; objective-only checks on some datasets | Assumes sufficiently complete descriptions; variable-space comparison can reject valid reparameterizations |
| [opti-agent-bench](https://arxiv.org/html/2607.10768v1) | Industrial optimization; understanding, modeling, implementation and reporting; ORAC task/evaluation validity | Severity-weighted rubrics and cross-module consistency; automated execution mixed with LLM judging | Rubric scores and evaluator judgments are not formal semantic certificates |
| [opt-verifier](https://arxiv.org/html/2605.29556v1) | Optimization modeling; structure distillation and model back-translation plus solution interpretation | Solving accuracy; structure consistency and solution validity guide refinement | LLM judgments can err; no theorem that all omitted constraints are detected |
| [verisimpl](https://arxiv.org/html/2607.20474v2) | Optimization; solver-derived simplified queries compared with LLM reasoning from original description | Self-verification precision; coverage denominator is correctly answered cases, unlike selective coverage | Diagnostic agreement is probabilistic; paper includes false-positive cases |
| [sover](https://arxiv.org/html/2609.00728v1) | Pairs of formal optimization models with proposed variable/parameter mapping; Z3 or tolerance-aware dReal | Cross-feasibility and objective-order checks, with explicit inconclusive outcome | Mapping and supported logic are assumptions; this does not certify free NL-to-model translation |
| [selective](https://papers.neurips.cc/paper/2017/file/4a8423d5e91fda00bb7e46540e2b0cf1-Paper.pdf) | Classifier and selection function; separate calibration and test under distributional assumptions | Coverage E[g]; selective risk E[loss*g]/E[g]; confidence-controlled risk selection | Population guarantees need stated sampling/calibration assumptions; handpicked paired challenges do not inherit them |
| [satzilla](https://ml.informatik.uni-freiburg.de/wp-content/uploads/papers/08-JAIR-Satzilla.pdf) | SAT solver portfolio selected using empirical hardness/performance models | Runtime and competition scoring; feature/pre-solver costs and ideal oracle comparison | Requires measured candidate performances; naming a provider is not algorithm selection evidence |
| [scienceagentbench](https://arxiv.org/html/2410.05080v3) | Scientific coding tasks extracted from peer-reviewed work with expert validation | Valid execution, task-specific success, code similarity and API cost; some outputs judged by LLM | Execution and scientific success differ; expert validation not replaced by code similarity |
| [qfaas](https://clouds.cis.unimelb.edu.au/papers/QFaaS.pdf) | Serverless hybrid quantum/classical applications and backend orchestration | Backend score uses transpiled depth, workload and backend metrics; framework evaluations | Operational routing does not certify fidelity of a scientific intention |
| [qaos](https://arxiv.org/html/2610.05304v1) | Quantum chemistry research workflow; graph of specialist nodes, fixed plan and interface checks | Case-study reference agreement and methodological deviations from specified model | Human-approved plan and small case study; does not establish general agent reliability |
| [weaver](https://dse.in.tum.de/wp-content/uploads/2025/01/Weaver-CGO-25.pdf) | Retargetable digital quantum compilation with FPQA instructions and pulse-to-gate checking | Functional equivalence after modeled hardware transformations; compilation/performance estimates | Digital/equidistance assumptions; cannot be treated as validation of arbitrary analog Pasqal programs |
| [giallar](https://www.cs.columbia.edu/~rgu/publications/pldi22-tao.pdf) | Compiler passes using symbolic circuits, restricted loop templates and verified rewrite library | SMT proof obligations and semantics preservation; counterexamples on failed obligations | Supported representation/loops/rewrite rules required; pulse-level and some approximate passes outside scope |
| [qedia](https://arxiv.org/html/2610.17708v1) | Quantum/classical programs specified using mechanized Hoare logic and prover agents | Lean kernel, axiom/build checks plus statement-faithfulness review | Kernel validity is relative to specified statements; human/LLM statement review remains separate |

QuantAge C01–C10 : deux petits contrats, MIS pondéré et photonique idéale à un
photon; LLM local compact et formulation déterministe, oracle numérique puis
veto sémantique lexical. Les résultats C09 sont conservés; C10-v4 est adapté
après leur consultation. Ni certificat de fidélité libre, ni généralisation
à un domaine inédit, ni validation de programme Pulser/Perceval ne sont établis
par ces expériences. Cette colonne QuantAge provient de l’état et des résumés
du dépôt, pas des sources externes.

## Références et consultation traçable

- **nl4opt** — Rindranirina Ramamonjison et al., *NL4Opt Competition: Formulating Optimization Problems Based on Their Natural Language Descriptions*. PMLR 220:189–203, PDF 2023; competition NeurIPS 2022. [Texte primaire](https://proceedings.mlr.press/v220/ramamonjison23a/ramamonjison23a.pdf). Passages : §2, §2.1, pp.191–193. Classical LP; no French-QPU constraints checked. Benchmark and winning systems reported; not reproduced here.
- **optimus** — Ali AhmadiTeshnizi et al., *OptiMUS-0.3: Using large language models to model and solve optimization problems at scale*. arXiv:2407.19633v4, 2026-06-26. [Texte primaire](https://arxiv.org/html/2407.19633v4). Passages : §3, §4.1–4.4, §5.1, §5.3. Classical solver APIs; hardware admissibility outside checked scope. Multi-model baselines and ablations reported; not reproduced.
- **opti-agent-bench** — Yongchang Fu, Xinjie Huang, Chengjun Dai, Chengzhe Feng, Junshao Zhang, Hong Zhu, *Opti-Agent-Bench: Benchmarking End-to-End Optimization R&D Agents on Real-World Business Problems*. arXiv:2607.10768v1, 2026-07-12. [Texte primaire](https://arxiv.org/html/2607.10768v1). Passages : §4.2, §5, §7.2–7.3. Classical optimization; French neutral-atom/photonics constraints not assessed in consulted sections. End-to-end and partial pipeline evaluations reported; no replication here.
- **opt-verifier** — Haoyang Liu et al., *Opt-Verifier: Unleashing the Power of LLMs for Optimization Modeling via Dual-Side Verification*. arXiv:2605.29556v1, 2026-05-28; ICML 2026 bibliographic landing page verified. [Texte primaire](https://arxiv.org/html/2605.29556v1). Passages : §4.1–4.4, §5 metrics, appendix A.3 identified. Classical solver setting; no checked French-QPU layer. Baselines, component ablations and verifier analysis reported; not reproduced.
- **verisimpl** — Sumaya Abdul Rahman, Seckhen Ariel Andrade Cuellar, Ghani Raissov, Mohammad Raza, *VeriSimpl: Robust Optimization Modeling from Natural Language using Simplification-based Verification*. arXiv:2607.20474v2, 2026-09-22. [Texte primaire](https://arxiv.org/html/2607.20474v2). Passages : §2, §3, §4.2, appendix B headings. Classical optimization queries; no French-QPU admissibility claim extracted. Multiple LLMs and benchmark experiments reported; no replication.
- **sover** — Swapnil Bhattacharyya, Mayank Baranwal, *SOVER: Formal Certification of Optimization Reformulations via LLM-Assisted SMT Verification*. arXiv:2609.00728v1, 2026-09-01. [Texte primaire](https://arxiv.org/html/2609.00728v1). Passages : §3, §4.2–4.4, §5. Formal optimization reformulation; no hardware execution guarantee. Finite reformulation benchmarks reported; proofs and software not independently reproduced.
- **selective** — Yonatan Geifman, Ran El-Yaniv, *Selective Classification for Deep Neural Networks*. NeurIPS 2017, archival PDF. [Texte primaire](https://papers.neurips.cc/paper/2017/file/4a8423d5e91fda00bb7e46540e2b0cf1-Paper.pdf). Passages : §2, §3, §5. General prediction, unrelated to QPU validity. Classification experiments reported; used for definitions only.
- **satzilla** — Lin Xu, Frank Hutter, Holger H. Hoos, Kevin Leyton-Brown, *SATzilla: Portfolio-based Algorithm Selection for SAT*. JAIR 32:565–606, 2008. [Texte primaire](https://ml.informatik.uni-freiburg.de/wp-content/uploads/papers/08-JAIR-Satzilla.pdf). Passages : §1.2, §2, §3.5, §5. Classical SAT portfolio; no quantum applicability asserted. Competition evaluation and ablations reported; not reproduced.
- **scienceagentbench** — Ziru Chen et al., *ScienceAgentBench: Toward Rigorous Assessment of Language Agents for Data-Driven Scientific Discovery*. arXiv:2410.05080v3, 2025-03-31; ICLR 2025. [Texte primaire](https://arxiv.org/html/2410.05080v3). Passages : §2 annotation/evaluation, §3, appendix E.2. Multi-discipline scientific workflows; no French-QPU guarantee extracted. Multiple models/frameworks and error analysis reported; not reproduced.
- **qfaas** — Hoa T. Nguyen, Muhammad Usman, Rajkumar Buyya, *QFaaS: A serverless function-as-a-service framework for quantum computing*. Future Generation Computer Systems 154:281–300, 2024; DOI 10.1016/j.future.2024.01.018. [Texte primaire](https://clouds.cis.unimelb.edu.au/papers/QFaaS.pdf). Passages : §4.2, invocation algorithm, §5.3. Multiple SDK/provider backends; no Pasqal/Quandela access inferred. Framework use cases and evaluations reported; not run here.
- **qaos** — Dikshant Dulal, Maxence Grandadam, Maciej Koch-Janusz, Mykola Maksymenko, *Demonstration of a Structured Agentic Workflow for Applied Quantum Computing Research*. arXiv:2610.05304v1, 2026-10-04. [Texte primaire](https://arxiv.org/html/2610.05304v1). Passages : §1–2, §3–5, appendix A headings and code availability. Quantum algorithm prototyping with classical references, not proof of French-QPU compatibility. Proton-transfer demonstration and baseline-agent comparisons reported; not reproduced.
- **weaver** — Oğuzcan Kırmemiş, Francisco Romão, Emmanouil Giortamis, Pramod Bhatotia, *Weaver: A Retargetable Compiler Framework for FPQA Quantum Architectures*. CGO 2025 archival author PDF, DOI 10.1145/3696443.3708965. [Texte primaire](https://dse.in.tum.de/wp-content/uploads/2025/01/Weaver-CGO-25.pdf). Passages : §3, §6, §7. Explicit neutral-atom architecture model, not automatic equivalence to Pasqal devices. Compiler evaluation reported; no replication.
- **giallar** — Runzhou Tao et al., *Giallar: Push-Button Verification for the Qiskit Quantum Compiler*. PLDI 2022 author archival PDF. [Texte primaire](https://www.cs.columbia.edu/~rgu/publications/pldi22-tao.pdf). Passages : §1, §4, §6 requirements, §7. Digital circuit compiler correctness, not experimental calibration or natural-language semantics. Compiler-pass verification/bugs reported; artifact not executed.
- **qedia** — Yuanjie (Collin) Ren, Zhicheng Zhang, Junyi Liu, Jinzheng Li, Yidi Qi, Mingsheng Ying, *QEDIA: Quantum Program Verification in Lean*. arXiv:2610.17708v1, 2026-10-13. [Texte primaire](https://arxiv.org/html/2610.17708v1). Passages : §5.1–5.2, §6 overview. Formal quantum programs, no physical device validation implied. Verified examples reported; theorem/library build not independently replayed.

Authentification : pages d’éditeur, arXiv versionné ou dépôt des auteurs.
Extraction : sections de méthode, métriques et limites indiquées; lectures
ciblées, pas revendication de lecture intégrale. Application : analogies
méthodologiques; les théorèmes et chiffres sources ne sont pas transposés
comme résultats QuantAge. Classification de chevauchement : `partial or
adjacent result only`. Aucun «apparently new» n’est retenu.

## Définitions à figer

Pour un corpus de N cas et une règle accept_i, publier au minimum :
couverture = somme accept_i / N; risque sélectif = erreurs acceptées /
somme accept_i (non défini si aucun accepté); couverture sur seuls cas
supportés; rétention des bonnes acceptations entre deux bras appariés.
Conserver les effectifs et distinguer hors-portée, ambigu et mal formalisé.

**Attention VeriSimpl :** §4.2 définit sa couverture comme cas entièrement
vérifiés / cas correctement répondus. Elle ne correspond pas au dénominateur
acceptés / tous les cas utilisé en prédiction sélective. Ne pas comparer ses
chiffres à notre couverture sans recalcul depuis les données adéquates.

Une borne de risque de population exige une calibration et des hypothèses
d’échantillonnage; des groupes synthétiques choisis et appariés ne deviennent
pas i.i.d. par le seul calcul d’un intervalle binomial. Pour C11, privilégier
effectifs finis, différences appariées par groupe et limites de conception.

SATzilla motive une autre distinction : sélectionner une étiquette de solveur
sans mesures des candidats n’évalue pas un portfolio. Si une expérience de
sélection est entreprise, mesurer références candidates, regret et coût de
sélection, puis comparer meilleur solveur unique et oracle de portefeuille.

Un succès de build, une équivalence mathématique, une conformité à un objet
Device documenté et un accès QPU sont quatre affirmations distinctes. Giallar
et QEDIA vérifient relativement à une sémantique/spécification; leur existence
ne certifie pas le passage non formel intention → spécification. Weaver repose
sur une abstraction digitale FPQA, pas sur un modèle analogique Pasqal universel.

## Hypothèses falsifiables proposées

### H11-1 — priorité 1

On frozen unseen semantic groups, the existing semantic-plus-numeric acceptance rule lowers accepted contract errors relative to numeric verification alone while retaining at least 80% of the latter arm’s correctly accepted supported cases.

Falsification : Either the paired accepted-error count is not lower or correct-answer retention is below 0.80; report an inconclusive finite result separately from population claims.

Protocole : Same actual model proposals, immutable inputs, independent gold; no rewriting verifier after inspecting test outputs.

Limites : Potentially useful finite evidence, not novel selective prediction theory; use per-group paired outcomes.

### H11-2 — priorité 2

Documentation-backed SDK/device checks reject constructible but unsupported quantum programs that pass abstract mathematical validation, with no loss on a separately established valid control set.

Falsification : No additional inadmissible case detected, or valid controls incorrectly rejected.

Protocole : Disjoint cases with explicit source-bound device specs; distinguish model equivalence, SDK acceptance, documented compatibility and QPU execution.

Limites : SDK/device checks establish only their documented abstraction; no QPU permitted.

### H11-3 — priorité 3

A frozen clause-grounded semantic verifier retains at least 80% of its development correct-acceptance rate under new genres and language paraphrases while reducing paired error acceptance relative to a keyword rule.

Falsification : Held-out retention below 0.80 or no paired error reduction; analyze by family and genre.

Protocole : Reserve entire base-intention groups and paraphrase genres; two families share error types; no label access by evaluated agent.

Limites : Threshold is proposed before C11, not a source-derived guarantee; new family generalization requires an actual additional family.

Les seuils de 80 % sont des critères de décision proposés avant C11, pas des
résultats ni des garanties issus de la littérature. L’intégrateur doit choisir
les hypothèses réellement exécutables et les fixer avant toute génération.

## Recherche, exclusions et limites

Recherche web en anglais sur les requêtes enregistrées dans le JSON, horizon
13 novembre 2026; ouverture des textes primaires et suivi de quelques références
du workflow QAOS. Pas de revue systématique, de graphe complet des citations ou
de recherche d’antériorité exhaustive. Les résultats externes ne sont pas
reproduits. Les deux fichiers de ce rôle sont des données documentaires.

Échecs d’accès documentés : premier miroir SATzilla (502), premier PDF Weaver
(404), PDF final Opt-Verifier sur GitHub (type non pris en charge). Des versions
primaires alternatives ont été lues; la version finale ICML d’Opt-Verifier est
authentifiée bibliographiquement mais son PDF n’est pas prétendu lu.

Repérages supplémentaires : *Discovering formally verified quantum programs
with AI*, [arXiv:2611.09822v2](https://arxiv.org/html/2611.09822v2), 9 novembre
2026, passages spécification/limites effectivement ouverts; l’article insiste
sur le choix humain d’une spécification et les contraintes physiques encore à
formaliser. Sans audit des preuves ni bibliothèque exécutée ici, aucune de ses
améliorations chiffrées n’est utilisée dans la matrice ou comme résultat QuantAge.

Prochaine action : figer C11 sur des groupes inédits après annotation distincte,
comparer les mêmes sorties avec/sans contrôles, puis éprouver une couche SDK
avec portée documentaire explicite. Aucune garantie de publication.
