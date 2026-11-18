# Revue ciblée de nouveauté et d'antériorités

## Conclusion

Ni le test C19 ni le pilote C27 ne justifient une revendication large de nouveauté. C19 est une comparaison exploratoire étroite de formulations complètes et d'une révision; il ne montre pas que le guidage dépasse l'auto-révision ou le direct. C27 est une réparation de développement n=1, sans cas réservé ni effet causal isolé. Le sélecteur qui nomme le solveur concordant le plus rapide après les avoir tous deux exécutés n'est pas un routeur prédictif.

## Travaux primaires proches

- La synthèse guidée par contre-exemples est antérieure : Solar-Lezama et al., “Combinatorial Sketching for Finite Programs,” ASPLOS 2006, [PDF auteur](https://people.csail.mit.edu/asolar/papers/Solar-LezamaTBSS06.pdf); Solar-Lezama, “The Sketching Approach to Program Synthesis,” APLAS 2009, [Springer](https://doi.org/10.1007/978-3-642-10672-9_3). La boucle LLM étudiée ne bénéficie pas des garanties de progression de CEGIS.
- AhmadiTeshnizi et al., *OptiMUS-0.3*, [arXiv:2407.19633v4](https://arxiv.org/abs/2407.19633v4), couvre modélisation, résolution et auto-réflexion d'erreurs.
- Liu et al., *Opt-Verifier: Unleashing the Power of LLMs for Optimization Modeling via Dual-Side Verification*, ICML 2026, [arXiv:2605.29556v1](https://arxiv.org/abs/2605.29556v1), est proche du thème général de vérification des modèles d'optimisation produits par LLM.
- Abdul Rahman et al., *VeriSimpl*, ICML 2026, [arXiv:2607.20474v2](https://arxiv.org/abs/2607.20474v2), et Bhattacharyya & Baranwal, *SOVER*, EMNLP 2026 Findings, [arXiv:2609.00728v1](https://arxiv.org/abs/2609.00728v1), examinent diagnostics générés par solveurs et vérifications formelles.
- Madaan et al., “Self-Refine: Iterative Refinement with Self-Feedback,” NeurIPS 2023, [proceedings](https://proceedings.neurips.cc/paper/2023/hash/91edff07232fb1b55a505a9e9f6c0ff3-Abstract-Conference.html), établit l'antériorité de l'itération avec feedback LLM; le bras auto C19 n'en est pas une reproduction complète.
- Xu, Hutter, Hoos & Leyton-Brown, “SATzilla: Portfolio-based Algorithm Selection for SAT,” *Journal of Artificial Intelligence Research* 32 (2008), 565–606, [DOI](https://doi.org/10.1613/jair.2490), est un antécédent de sélection algorithmique par portefeuille, plus large que le gagnant rétrospectif C19/C27 après exécution des deux solveurs.

## Formulation défendable

La seule formulation défendable est descriptive : sur un cas de développement réutilisé à quatre variables, un appel guidé supplémentaire a corrigé un désaccord de faisabilité antérieur; l'énumération exhaustive a trouvé l'accord sur les 16 affectations relativement au contrat annoté. Ce constat n'établit ni une contribution CEGIS nouvelle, ni une amélioration statistique, ni une nouveauté mondiale.

Cette revue est ciblée sur les antériorités les plus proches identifiées; elle n'est pas exhaustive. Elle ne constitue pas une garantie de nouveauté ou de publiabilité.
