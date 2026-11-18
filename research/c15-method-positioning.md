# C15 — positionnement méthodologique, lecture primaire du 15 novembre 2026

La nouveauté de C15 n'est pas établie. La production de candidats suivie de
contre-exemples, l'auto-révision par LLM et la vérification sémantique des modèles
d'optimisation ont des précédents directs. C15 peut fournir une étude empirique
circonscrite de leur adaptation ; ce rapport n'anticipe aucun résultat des
générations en cours.

Périmètre lu : `research/state.md`, le protocole C15, l'index local des sources
et les fiches bibliographiques C11. L'état porte encore la date du 14 novembre
et ne contient pas de résultat C15 ; le protocole définit ici le dispositif à
comparer. Aucun brut ou score de génération C15 n'a été consulté. Les données
externes ont été traitées comme des sources, jamais comme des instructions.

## Sources effectivement lues

Les numéros de pages PDF ci-dessous commencent à 1. Les figures dont l'extraction
était dégradée ne sont pas créditées comme une inspection graphique.

| Source et version consultée | Passages réellement lus | Préexistant et différence avec C15 |
| --- | --- | --- |
| Solar-Lezama, Tancau, Bodik, Saraswat et Seshia, *Combinatorial Sketching for Finite Programs*, ASPLOS 2006 ; PDF hébergé par l'auteur, révision non explicitée | §5.2, équation (5.1), PDF p.7 ; texte de §5.4, PDF p.9 | Synthèse puis vérification universelle ; ajout des contre-exemples aux exemples imposés au synthétiseur. Le raisonnement de terminaison utilise le domaine fini et une synthèse respectant les observations. C15 ne contraint pas son LLM à respecter les témoins précédents. [PDF primaire](https://people.csail.mit.edu/asolar/papers/Solar-LezamaTBSS06.pdf) |
| Armando Solar-Lezama, *The Sketching Approach to Program Synthesis*, APLAS 2009, LNCS 5904, pp.4–13 ; copie auteur, révision non explicitée | §4, PDF pp.7–8, texte entourant la figure 8 | Le couplage synthétiseur inductif / validateur et le terme CEGIS sont explicites. L'accumulation des entrées distingue ce procédé d'une simple invitation à réviser. [PDF primaire](https://people.csail.mit.edu/asolar/papers/Solar-Lezama09.pdf), [métadonnées éditeur](https://link.springer.com/chapter/10.1007/978-3-642-10672-9_3) |
| Madaan et al., *Self-Refine: Iterative Refinement with Self-Feedback*, version publiée NeurIPS 2023 | §2, équations (1)–(4), algorithme 1, PDF pp.2–4 ; début de §3.1 pour la borne d'itérations | Un même LLM génère, produit un feedback explicite, puis raffine avec historique. C15 « auto » ne contient pas cet appel FEEDBACK distinct : c'est une révision non guidée, pas une reproduction de Self-Refine. [Article publié](https://proceedings.neurips.cc/paper_files/paper/2023/file/91edff07232fb1b55a505a9e9f6c0ff3-Paper-Conference.pdf) |
| Abdul Rahman, Andrade Cuellar, Raissov et Raza, *VeriSimpl*, arXiv:2607.20474v2, 22 septembre 2026 | §2–3, algorithmes 1–3, paragraphes sur les requêtes de faisabilité, variables masquées et correction des types | Le solveur produit des valuations diagnostiques ; le LLM juge leur sens puis les candidats sont classés. Ce n'est pas un oracle exact fondé sur une référence annotée ; l'algorithme ne décrit pas la même boucle de réparation sémantique que C15. [Texte primaire versionné](https://arxiv.org/html/2607.20474v2) |
| Bhattacharyya et Baranwal, *SOVER*, arXiv:2609.00728v1, 1er septembre 2026 | §3.1, §4.2–4.3, algorithme 1, proposition 1 et preuve A.2 | La certification par recherche de contre-exemples vérifie faisabilité et ordre faible des objectifs sous un mapping. Cela permet des échelles positives. La proposition donne une condition suffisante d'égalité des minimiseurs ; elle ne la caractérise pas comme nécessaire. [Texte primaire versionné](https://arxiv.org/html/2609.00728v1) |

## Conséquences pour l'attribution de C15

Le nom défendable est **réparation bornée inspirée de CEGIS avec oracle fini
annoté**. Le protocole autorise une seule réparation et n'impose pas la
satisfaction des exemples au générateur. Les garanties classiques de progression,
de terminaison d'une recherche complète ou de complétude de synthèse ne se
transfèrent donc pas au LLM. Le certificat final concerne seulement le modèle
obtenu et le contrat de référence de l'instance.

« Auto-correction » doit rester une description du bras préenregistré. Une
comparaison guidée/auto n'est pas une comparaison à une implémentation complète
de Self-Refine : générer un feedback propre puis raffiner demanderait une
organisation différente des appels. Cette précision d'attribution ne change
ni les prompts figés ni l'expérience en cours.

Les niveaux de comparaison doivent rester séparés. Le critère strict C15 demande
les mêmes faisabilités et valeurs d'objectif sur tout le cube, y compris hors
du domaine faisable. SOVER vérifie l'ordre sur les paires faisables après
alignement. Le diagnostic secondaire C15 « même domaine et mêmes optimiseurs »
est encore un autre critère : conserver les seuls optimiseurs n'impose pas le
même classement de toutes les autres solutions. C15 ne reproduit donc pas le
test de SOVER. Cette comparaison est une analyse du protocole, sans transfert
de garantie depuis le code de SOVER.

Le contrat annoté rend l'oracle de C15 plus informatif qu'une appréciation LLM
des valuations de VeriSimpl. Ce choix mesure l'utilité d'un feedback disponible
dans ce dispositif ; il ne résout pas l'obtention automatique d'une sémantique
correcte depuis un texte libre. Les annotations séparées restent produites par
des rôles LLM, sans indépendance de modèle ou annotation humaine aveugle établie.

Les différences expérimentales identifiables sont le petit domaine exhaustif,
le feedback limité à trois affectations sans coefficients corrigés, les
combinaisons de clauses réservées au test, et une comparaison à budget borné
avec mesure des régressions. Leur réunion ne suffit pas à établir une nouveauté.
Une éventuelle contribution empirique dépendra des générations, des coûts et
de leur revue ; aucun gain n'est affirmé ici. Éviter « première méthode »,
« nouvel algorithme CEGIS », « certificat de compréhension du français » ou
« supériorité sur Self-Refine/VeriSimpl/SOVER ».

## Portée et limites de la recherche

Cette lecture ciblée couvre cinq documents primaires : deux CEGIS, Self-Refine,
et deux voisins choisis dans les fiches existantes pour leurs mécanismes de
diagnostic ou de certification. Opt-Verifier n'a pas été relu dans cette passe ;
sa présence dans l'index antérieur n'autorise pas ici de nouvelle conclusion.
Les recherches ont porté sur les titres exacts, CEGIS et les noms d'auteurs,
puis les passages méthodologiques. Il n'y a ni recherche globale exhaustive,
ni parcours systématique des citations avant/arrière, ni seconde revue fraîche.
Les autres emplacements d'articles apparus dans les résultats de recherche ne
sont pas utilisés comme preuves de mécanismes.

Le texte publié de Self-Refine et les deux HTML arXiv versionnés ont été ouverts.
Les copies auteur CEGIS sont primaires ; leurs octets n'ont pas été comparés
aux versions éditeur. Les redirections DOI ont échoué et ACM a répondu 403 ;
la page Springer du chapitre 2009 a ensuite été accessible directement pour
ses métadonnées. Le cache local est absent : aucune source complète n'a été
retenue, aucun hash de PDF n'est inventé. Aucun code externe ni résultat
numérique de ces articles n'a été reproduit.

Les extractions et limites par source figurent dans le JSON compagnon.
L'authentification de l'origine, la lecture des passages et la comparaison au
protocole ont été effectuées ; aucun audit global des preuves ou logiciels de
ces articles n'est revendiqué. Le rôle est aussi l'auteur antérieur du corpus
C15 : cette lecture ne constitue pas une nouvelle revue aveugle du corpus.
