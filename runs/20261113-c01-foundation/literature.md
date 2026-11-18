# Revue ciblée — consultation du 13 novembre 2026

Auto-revue : agent littérature interrompu par quota; sources rouvertes par
l'intégrateur. Pas de recherche exhaustive ni d'affirmation de nouveauté.

- AhmadiTeshnizi et al., *OptiMUS-0.3*, arXiv:2407.19633v4,
  26 juin 2026, §§4.1–4.4 et 5.3 effectivement consultés dans le HTML primaire :
  https://arxiv.org/html/2407.19633v4. Le système décompose la modélisation et
  traite les erreurs d'extraction, de formulation et de code. Notre découpage
  est adjacent à ces travaux; ce cycle n'en reproduit aucune performance LLM.
- Ramamonjison et al., *NL4Opt Competition*, PMLR 220:189–203, PDF 2023
  (compétition NeurIPS 2022), §§1–2 :
  https://proceedings.mlr.press/v220/ramamonjison23a/ramamonjison23a.pdf.
  Entités sémantiques et représentation intermédiaire sont déjà des objets
  d'évaluation. La page bibliographique affiche 2022, le PDF 2023 : nous
  retenons l'année imprimée du volume, sans assimiler compétition et parution.
- Andrew Lucas, *Ising formulations of many NP problems*, Frontiers in Physics
  2:5 (2014), §4.2, DOI 10.3389/fphy.2014.00005 :
  https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2014.00005/full.
  Le cas non pondéré se traduit par P>1. L'extension pondérée ci-dessous est
  justifiée directement, sans l'attribuer à cette section du texte.
- Heurtel et al., *Perceval*, Quantum 7:931 (2023), version primaire
  arXiv:2204.00602v3, §§3.2.4, 4.1, 4.2 :
  https://arxiv.org/html/2204.00602. Les imperfections et la post-sélection
  doivent être explicitées; les probabilités multiphotoniques impliquent des
  permanents avec facteurs de normalisation. Notre banc se limite à un photon.

Contrat mathématique : pour un ensemble sélectionné non indépendant, retirer
un sommet i incident à au moins une arête sélectionnée change Q de
w_i-P d_i<0 lorsque P>max w. Tout minimiseur est donc indépendant. Sur les
indépendants Q=-poids, donc l'ensemble des minimiseurs est exactement celui
des optima contraints. Cette preuve locale utilise poids positifs et arêtes
simples non orientées; P=max w n'est pas une condition suffisante générale.
Sur K2 non pondéré avec P=1, 10, 01 ET 11 minimisent Q=-1.

La rotation optique utilise une convention réelle explicite; la documentation
Perceval v1.3, «Beam Splitter conventions», donne Ry(theta) avec demi-angle.
Notre R(a) correspond à Ry(2a), pas au BS par défaut Rx.
Source : https://perceval.quandela.net/docs/v1.3/reference/components/unitary_components.html.
Cette traduction est documentaire; aucun SDK n'a été installé ou exécuté.

Application : équivalence MIS vérifiée dans son contrat; modèle optique
conditionnel aux hypothèses idéales; adaptation matérielle non établie.
Recherche limitée aux requêtes OptiMUS/NL4Opt, Ising independent set,
documentation officielle Pulser/Perceval. Pas de suivi exhaustif des citations.
