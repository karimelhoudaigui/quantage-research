# Portée des certificats et transfert des contrôles dans des workflows quantiques

QuantAge — étude empirique et document de travail, 14 novembre 2026. La maturité pour soumission n'est pas établie.

## Résumé

Nous étudions la fidélité de la chaîne intention scientifique, problème formalisé, formulation et exécution locale. Un certificat numérique relatif à un problème normalisé et l'acceptation d'un programme par un SDK répondent à des questions différentes de la fidélité à l'intention. Nous testons un contrôleur lexical figé sur 128 nouvelles requêtes appariées de MIS pondéré et de photonique idéale, annotées par deux rôles distincts avant génération. Deux modèles locaux produisent 256 réponses. Le veto réduit les mauvaises acceptations de 44 à 12, mais ne conserve que 23 des 55 bonnes acceptations de la référence numérique : le critère préenregistré de rétention échoue. Le second modèle ne produit aucun contrat conforme; le consensus refuse tout. Des expériences séparées exécutent réellement Perceval et Pulser face à des oracles construits indépendamment. Elles établissent une conformité logicielle finie sous leurs tolérances, avec des limites de portée et un arrondi temporel observé. Aucun run QPU, avantage quantique, nouveauté générale ou fiabilité populationnelle n'est établi.

## Question scientifique et positionnement

Notre question principale est : un contrôle sémantique figé réduit-il les erreurs acceptées sur de nouveaux groupes sans perdre une part excessive des réponses fidèles ? La seconde question porte sur ce que certifient réellement les frontières numérique, SDK et dispositif documenté. La contribution candidate est un banc apparié qui expose ces frontières et leurs échecs, avec propositions réelles et versions préservées. Son originalité par rapport à l'ensemble de la littérature reste à établir; une architecture modulaire ou un vérificateur ajouté ne constitue pas, à lui seul, une nouveauté.

La revue ciblée couvre 17 sources primaires avec versions et passages consultés dans `research/c11-literature.md` et `research/c11-comparison.json`. Trois sources supplémentaires sont documentées dans `research/c11-literature-extension.json`. Les résultats externes ne sont pas reproduits ici. Les preprints sont distingués des publications archivées.

| Travail primaire | Ce qui est évalué ou certifié | Différence de portée |
|---|---|---|
| [NL4Opt, PMLR 2023](https://proceedings.mlr.press/v220/ramamonjison23a/ramamonjison23a.pdf) et [OptiMUS v4](https://arxiv.org/html/2407.19633v4) | Entités/représentations d'optimisation et pipeline de modélisation/résolution | L'exécution ou l'accord d'une solution ne certifie pas toute clause du texte |
| [Opti-Agent-Bench v1](https://arxiv.org/html/2607.10768v1) | Pipeline complet et cohérence entre modules, rubriques et juges | Les scores de cohérence sont distincts d'une preuve formelle de fidélité |
| [Opt-Verifier v1](https://arxiv.org/html/2605.29556v1) et [VeriSimpl v2](https://arxiv.org/html/2607.20474v2) | Vérifications structure/solution ou simplification et accord de diagnostics | Ces vérifications ont déjà des précédents; leur fiabilité reste conditionnelle |
| [SOVER v1](https://arxiv.org/html/2609.00728v1) | Reformulations avec correspondances proposées, obligations SMT | La certification dépend du mapping et de la logique; le passage libre du texte au contrat reste séparé |
| [Prédiction sélective, NeurIPS 2017](https://papers.neurips.cc/paper/2017/file/4a8423d5e91fda00bb7e46540e2b0cf1-Paper.pdf) | Risque conditionnel à l'acceptation et couverture | Les garanties de population exigent des hypothèses de calibration/échantillonnage absentes de notre défi de convenance |
| [SATzilla, JAIR 2008](https://ml.informatik.uni-freiburg.de/wp-content/uploads/papers/08-JAIR-Satzilla.pdf) | Portfolio fondé sur performances mesurées et coûts de sélection | QuantAge choisit ici des références locales par contrat, pas un portfolio appris dont le regret serait évalué |
| [QAOS v1](https://arxiv.org/html/2610.05304v1) et [QFaaS](https://clouds.cis.unimelb.edu.au/papers/QFaaS.pdf) | Workflows de recherche ou orchestration hybride | L'orchestration quantique structurée a des précédents; aucun droit QPU n'en découle |
| [QCoder, INLG 2025](https://aclanthology.org/2025.inlg-main.43.pdf) | Génération de circuits avec feedback de runtime, portes, profondeur et état | Les contrôles fondés sur simulateur ont déjà un précédent; la portée est liée au benchmark |
| [QTestBench v1](https://arxiv.org/html/2610.13811v1) et [Benchmarking the Quantum Leap v1](https://arxiv.org/html/2610.28678v1) | Tests générés face à des checkers indépendants; audit des évaluateurs et des sorties | L'exécutabilité et les scores de leaderboard ne remplacent pas la discrimination sémantique |
| [Giallar, PLDI 2022](https://www.cs.columbia.edu/~rgu/publications/pldi22-tao.pdf), [Weaver, CGO 2025](https://dse.in.tum.de/wp-content/uploads/2025/01/Weaver-CGO-25.pdf), [QEDIA v1](https://arxiv.org/html/2610.17708v1) | Préservation sous sémantiques/abstractions de programmes et matériels explicites | Une preuve relative à une spécification ne certifie pas que cette spécification traduit le texte ou un appareil accessible |

La couverture de VeriSimpl est rapportée aux cas correctement répondus. Elle ne doit pas être comparée directement à notre couverture acceptés/tous les cas. La revue n'est ni exhaustive ni une preuve d'absence d'antériorité. La seconde recherche ciblée a été menée par l'intégrateur après épuisement du quota des relecteurs; la nouvelle revue finale distincte reste absente.

## Définitions et contrats

Une requête $u=(t,d)$ comprend un texte et des données numériques structurées. L'interpréteur propose un contrat $p=I(t,d)$; la formulation $F(p)$ et le solveur local sont déterministes dans les bras évalués. Nous distinguons une erreur de sens $L(u,p)$, la validité numérique des sorties pour $p$, l'acceptation d'un objet par un SDK versionné et le respect d'une spécification de dispositif. La dernière propriété reste partielle même quand un constructeur Device est exécuté.

Pour $N$ cas observés et des décisions $A_i$, la couverture et le risque sélectif sont :

$$C=rac{sum_i A_i}{N},qquad R=rac{sum_i A_i L_i}{sum_i A_i}.$$

Le risque est non défini si aucune requête n'est acceptée. Le rappel supporté est le nombre de bonnes acceptations divisé par le nombre de tâches supportées. Une tâche erronée acceptée sur une requête supportée compte aussi comme erreur. Les refus de schéma ne sont pas crédités comme abstentions sémantiques du LLM. Une mauvaise acceptation désigne une tâche exécutée hors du contrat annoncé; elle n'implique pas que sa solution numérique soit toujours fausse pour l'intention initiale. Une clause supplémentaire peut être inactive sur les optima de l'instance.

### Optimisation combinatoire

Le MIS pondéré porte sur un graphe simple non orienté, des poids entiers positifs et des variables binaires, avec au plus 12 sommets pour la référence exhaustive. La formulation minimise :

$$Q(x)=-sum_iw_ix_i+Psum_{(i,j)in E}x_ix_j,qquad P=1+max_iw_i.$$

Chaque arête est comptée une fois. Retirer un sommet choisi avec $d_igeq1$ voisins choisis change l'énergie de $w_i-Pd_i<0$. Tout minimiseur est donc indépendant; sur les ensembles indépendants, minimiser $Q$ maximise le poids. Cet argument uniforme n'est pas une revendication de nouveauté; le cadre Ising est documenté par [Lucas, 2014](https://doi.org/10.3389/fphy.2014.00005). Le certificat fini compare tous les optima pour les instances bornées. Il ne vérifie pas une contrainte textuelle omise, et une QUBO abstraite n'est pas automatiquement un Hamiltonien Pasqal réalisable. Max-Cut classique et Quantum Max-Cut ne sont pas assimilés à ce contrat.

### Photonique et dynamique

Le contrat agentique photonique C11 reste idéal, à un photon initial en mode 0, deux modes, radians, sans pertes, avec $U=R(b)\operatorname{diag}(1,e^{i\phi})R(a)$ et la rotation réelle $R$. Les probabilités sont comparées à un oracle trigonométrique à tolérance absolue $10^{-12}$. Cela ne certifie ni les amplitudes ni un circuit dans tout autre contexte d'entrée. La convention de rotation est :

$$R(t)=\begin{pmatrix}\cos t&-\sin t\\\sin t&\cos t\end{pmatrix}.$$

Dans l'expérience SDK, elle est construite avec `BS.Ry(theta=2t)`, avec phases et ordre explicités.

L'extension SDK porte sur deux photons indistinguables dans trois modes. L'oracle applique les opérateurs de création transformés et leurs facteurs de normalisation de Fock. La revue orthogonale emploie la somme des deux permutations :

$$P(s|t)=rac{|U_{i_1j_1}U_{i_2j_2}+U_{i_1j_2}U_{i_2j_1}|^2}{prod_k s_k!prod_k t_k!}.$$

Les indices sont répétés selon les occupations, y compris en collision. Ces conventions et la formule de Fock sont reliées au [papier Perceval](https://arxiv.org/html/2204.00602). L'extension démontre une validation numérique de circuits, pas une généralisation de l'agent à deux photons.

Pour deux atomes, le modèle nominal conserve l'interaction finie :

$$H=rac{Omega}{2}sum_{j=0}^1(e^{iphi}|r_j
anglelangle g_j|+e^{-iphi}|g_j
anglelangle r_j|)-deltasum_{j=0}^1n_j+rac{C_6}{r^6}n_0n_1.$$

Nous prenons $\hbar=1$. Les amplitudes/detunings sont en rad/µs, les distances en µm et les durées converties de ns en µs. La référence diagonalise une matrice $4\times4$ dans l'ordre gg, gr, rg, rr. Elle est distincte de l'ODE SDK et de sa représentation temporelle; aucun bruit Pasqal ou blockade parfait n'est supposé.

## Architecture et règles d'acceptation

Les huit responsabilités sont réparties entre modules explicites : compréhension LLM; normalisation des données; formulation; veto lexical; vérification numérique; frontière documentaire matérielle; choix de référence locale; évaluation hors ligne. Les principaux chemins sont `c11_inference.py`, `c11_score.py`, `compact_v4.py`, `contracts.py`, `core.py` et les modules SDK séparés. Le gold est lu uniquement par le scorer. Les traces conservent les messages, réponses, paramètres, tokens, temps et empreintes.

Un second modèle reçoit les mêmes requêtes dans un contexte isolé. Le bras complet exige deux propositions conformes et concordantes, puis applique les mêmes contrôles. Le refus est explicite en cas de désaccord. Ce sont deux modèles d'intention avec contrôles déterministes; nous n'attribuons pas un LLM autonome à chaque fonction. Aucun mécanisme de réparation après lecture du test n'est appliqué.

Les contrôles numériques certifient un problème normalisé, le veto reste heuristique et les vérifications matérielles restent relatives aux versions documentées. La route autorise seulement la référence locale et conserve les candidats Pasqal/Quandela comme non vérifiés pour une machine précise. Aucune génération complète de coefficients par LLM, politique apprise ou mesure de regret de portfolio n'est évaluée.

## Protocole de transfert et hypothèses

Le corpus nouveau contient 128 requêtes, 64 groupes appariés, 64 cas MIS et 64 photoniques, ainsi que 64 textes français et 64 anglais. Une paire conserve les données et change une clause de l'intention. Un auteur distinct produit les textes sans consulter le code v4; un relecteur annote chaque texte sans voir le gold auteur ou son générateur. Les 128 décisions action/tâche concordent avant génération. Les labels originaux et leur normalisation bijective restent conservés. Le relecteur connaît les travaux historiques et v4; aucune indépendance humaine ou de modèle n'est démontrée.

Le preflight vérifie 64 paires et les domaines, contrôle 184 fichiers historiques inchangés et ne trouve aucun doublon exact de requête ou de texte normalisé avec les 1 385 requêtes historiques distinctes examinées. Il ne prouve ni l'absence d'équivalence sémantique cachée ni l'absence de contamination du pré-entraînement. Tous les groupes C01–C10 sont du développement pour v4.

Les sources et instructions sont figées avant génération. Qwen2.5-0.5B-Instruct et SmolLM2-135M-Instruct sont exécutés hors ligne, float32 CPU, quatre threads, greedy, seed 20261113, maximum 128 nouveaux tokens, sans retry ni réparation. Les révisions et hashes des poids sont enregistrés. SmolLM2 est principalement anglophone selon sa carte; taille, entraînement et langue confondent toute comparaison causale entre modèles.

- H1 primaire : le veto retire au moins 50 % des erreurs du bras numérique tout en conservant au moins 90 % de ses bonnes acceptations.
- H2 : un certificat numérique ne suffit pas à établir la fidélité; un nouveau contre-exemple réel réfute cette suffisance, tandis qu'un zéro fini ne la prouverait pas.
- H3 exploratoire : le consensus réduit les erreurs et conserve au moins 80 % des bonnes acceptations de Qwen avec v4.

La baseline stricte, les mots-clés, le LLM direct, l'agent sans vérificateur, l'agent numérique, l'agent numérique avec veto et le consensus sont comparés. Le bras direct mesure une décision, les autres une autorisation d'exécution locale; cette différence est explicite. La formulation compacte étant déterministe, une ablation numérique nulle est attendue structurellement et n'évalue pas la détection de coefficients LLM erronés. Les niveaux de contrôles forment des points de couverture/risque, sans seuil probabiliste calibré.

Corpus de convenance apparié : nous rapportons les comptes finis, pas une p-value ou un intervalle binomial pour une population naturelle non définie. Les limites d'une génération partielle seraient conservées sans imputation. Ici les deux matrices de 128 appels sont complètes.

## Résultats comparatifs et ablations

| Méthode | Bons acceptés | Faux acceptés | Couverture | Risque |
|---|---:|---:|---:|---:|
| Strict | 0 | 0 | 0.000 | non défini |
| Mots-clés | 23 | 26 | 0.383 | 0.531 |
| Qwen : décision directe | 55 | 65 | 0.938 | 0.542 |
| Qwen : agent sans vérificateur | 55 | 44 | 0.773 | 0.444 |
| Qwen : numérique | 55 | 44 | 0.773 | 0.444 |
| Qwen : numérique + v4 | 23 | 12 | 0.273 | 0.343 |
| SmolLM2 : décision directe | 0 | 0 | 0.000 | non défini |
| SmolLM2 : sans vérificateur | 0 | 0 | 0.000 | non défini |
| SmolLM2 : numérique | 0 | 0 | 0.000 | non défini |
| SmolLM2 : numérique + v4 | 0 | 0 | 0.000 | non défini |
| Deux modèles + contrôles | 0 | 0 | 0.000 | non défini |

![Acceptations et risque sur C11 : mêmes réponses, contrôles discrets. Le risque reste non défini à couverture nulle.](figures/c11-selective-v2.png)

Chaque méthode observe 128 cas, dont 64 supportés. Les faux acceptés incluent les tâches erronées sur cas supportés : le direct Qwen en compte six, en plus de 59 acceptations hors contrat. Le contrôleur de données en bloque une partie. Les 44 erreurs restantes du bras numérique ont un certificat numérique valide pour la mauvaise interprétation.

H1 n'est pas soutenue : la réduction des erreurs atteint 72.7 %, mais la rétention des bonnes acceptations n'est que 41.8 %. Le veto retire 32 erreurs et 32 bonnes acceptations, sans ajout. H2 est illustrée par 44 nouveaux contre-exemples réels, en accord avec la distinction déjà connue entre sortie et sens. L'ablation numérique ne change aucune décision, conformément à la formulation déterministe.

Qwen produit 120 contrats conformes et aucune abstention explicite conforme; son exactitude action/tâche est 55/128. SmolLM2 produit zéro contrat conforme sous ce budget; 106 réponses atteignent la limite de tokens et 22 finissent par EOS. Ce résultat dépend du modèle, de la langue, de l'instruction et du budget de sortie; il ne prouve pas une incapacité intrinsèque. H3 n'est pas soutenue : l'accord strict refuse les 128 cas et perd toutes les bonnes acceptations. Son zéro erreur est accompagné d'une couverture nulle.

Par famille, numérique vers veto : MIS, 32 bonnes/29 mauvaises acceptations vers 18/10; photonique, 23/15 vers 5/2. Par langue : anglais 27/20 vers 13/6; français 28/24 vers 10/6. Ce contraste ne permet pas d'isoler une cause linguistique sans contrôler les clauses et données appariées.

Les erreurs résiduelles comprennent cardinalités minimale/maximale ou paire, exclusion de sommet, budget de poids, domaine de variables, nombre de photons et demande d'échantillons plutôt que de probabilités. Une contrainte de cardinalité maximale est omise; une demande de 100 échantillons refusant une distribution est interprétée comme calcul de probabilités. Les deux cas de parité acceptés ont ici une solution de cardinalité paire : une clause omise peut être inactive sur les optima observés, sans rendre les domaines formels identiques. La validité de la QUBO ou du circuit choisi ne corrige pas la clause omise. À l'inverse, des formes valides telles qu'une entrée donnée en notation de Fock ne satisfont pas nécessairement les marqueurs lexicaux attendus. Aucun correctif n'est introduit dans le score réservé.

### Bras différé plus grand : résultat de ressources

C14 sélectionne 32 cas dans 16 groupes C11 par famille, langue et ordre des IDs, après consultation de C11. Cette analyse différée ne fournit aucun nouveau corpus indépendant. Qwen2.5-1.5B est essayé sur CPU avec une précision de 16 bits, en raison des 8 GiB de RAM observées. Le float16 produit une réponse de 128 exclamations; un contrôle sur le même prompt constate 151 936 logits NaN. Après amendement, bfloat16 donne 151 936 logits finis, puis un contrat conforme de 49 tokens en 493.62 s. Ces deux configurations ne diffèrent pas seulement de la capacité du modèle C11; aucune causalité de taille isolée n'est revendiquée.

Les deux configurations sont arrêtées et leurs manifestes d'échec sont conservés. Le bras bfloat16 est arrêté précocement pour coût, sans épuiser artificiellement le budget : au débit du premier cas, la matrice de 32 serait impraticable dans les 1 650 s retenues. Il ne s'agit pas d'un temps total mesuré. Une seule réponse est achevée par configuration, sur le même cas; les 31 cas manquants ne sont pas des abstentions. H14 reste non résolue et aucun score de fidélité n'est attribué au modèle plus grand. La finitude du premier prefill ne certifie pas tous les tokens futurs. Ces diagnostics bornés figurent dans C14-PRECISION-RUNTIME; ils n'invalident ni ne remplacent le résultat réservé C11.

## Compatibilité logicielle et contraintes documentées

Perceval 1.3.1 exécute 486 évaluations : 81 configurations à trois modes, chacune avec six occupations d'entrée à deux photons, soit 2 916 probabilités. L'erreur maximale face à l'oracle de création est 2.22e-16, sous le seuil préenregistré $10^{-10}$. La revue distincte par somme de chemins confirme l'accord sous ce seuil; sa différence maximale flottante est $3.33\times10^{-16}$. Hong–Ou–Mandel et les collisions d'entrée servent de contrôles analytiques. Cinq sondes SDK sont rejetées; une entrée à trois photons est acceptée légitimement par le SDK et reste hors du contrat expérimental. Notre frontière de contrat refuse huit variantes et conserve son contrôle. Ce sont deux frontières différentes.

Pulser 1.7.2 et QuTiP 5.2.3 construisent et simulent 162 programmes AnalogDevice à deux atomes, dont 54 contrôles à entraînement nul. La comparaison au modèle nominal donne un écart de probabilités maximal 0.000473, sous $5\times10^{-3}$, et une erreur de normalisation de $1.61\times10^{-9}$, sous $10^{-8}$. La matrice Hamiltonienne à l'instant initial concorde à $6.12\times10^{-17}$; cette vérification ponctuelle n'atteste pas l'identité des trajectoires complètes. Le recalcul indépendant par exponentielle en série confirme l'oracle nominal à $3.06\times10^{-14}$. Les tolérances ODE ne sont pas des garanties globales. Les frontières temporelles échantillonnées constituent une explication plausible de l'écart nominal/SDK, non une cause isolée par cette expérience.

Sur neuf sondes Pulser, sept sont rejetées. Une durée demandée de 101 ns est acceptée après arrondi à 104 ns, avec avertissement; un registre sans layout est accepté par le constructeur malgré une exigence backend/layout distincte. Acceptation SDK, préservation des paramètres et compatibilité QPU ne sont donc pas interchangeables. Les spécifications et versions effectivement consultées sont conservées dans `research/c11-hardware-sources.json` et les cycles SDK. Aucune géométrie abstraite ou présence d'un SDK ne démontre un accès physique.

Ces expériences établissent l'exécution locale de programmes et des vérifications partielles de spécification. Aucune conformité à une machine Quandela précise, calibration Pasqal, bruit réel, disponibilité de compte ou exécution QPU n'est établie. La dynamique Rydberg ajoute un banc numérique; les agents de C11 n'ont pas été évalués sur cette famille.

## Coûts et reproductibilité

C11 : Qwen, 57560 tokens d’entrée, 7246 de sortie et 1114.45 s avec chargement; SmolLM2, 63783, 15693 et 465.61 s. Pics RSS enregistrés : 2.11 Go et 1.05 Go. Ces durées décrivent les configurations locales, sans isoler un effet de taille. Perceval et Pulser prennent respectivement 39.61 s et 21.82 s dans leurs processus enregistrés; le CPU principal Perceval exclut ses sondes en sous-processus.

Les générations sont hors ligne, avec Safetensors, sans code distant ou lecture de secrets. Chaque expérience conserve protocole, commandes, versions, commit de départ, empreintes avant/après, sorties et statut réel dans un manifest v2. Base Git `fee83eb`, arbre modifié; aucun push ou publication. Les coûts des générations communes sont comptés une fois, même si plusieurs ablations les réutilisent. Coût machine/énergie et coût complet de session inconnus, achat externe nul.

L'audit historique reproduit les premières expériences et vérifie leurs oracles indépendamment. C11 a des annotations et une revue pré-exécution distinctes; ses résultats finaux ont seulement l'auto-audit de l'intégrateur, le quota ayant ensuite échoué. C12/C13 disposent de recalculs orthogonaux par auteur distinct; les relecteurs n'ont pas rejoué tous les SDK. Les sources historiques du manuscrit sont conservées dans `paper/archive/`. Aucun PDF n'est prétendu validé en l'absence de compilation.

## Limites et maturité scientifique

La méthode ne comprend pas des documents scientifiques arbitraires : les données numériques sont fournies en JSON, les tâches supportées sont étroites et les formulations déterministes. Les annotations sont produites par des rôles LLM, avec connaissance partagée du projet, sans humains aveugles. Les modèles restent petits; les refus dus au format et les troncatures dominent certains bras. Le consensus ne mesure ni indépendance d'erreurs ni confiance calibrée. Les cas synthétiques, appariés et équilibrés ne représentent pas une distribution d'usage naturel.

Les SDK étendent les preuves logicielles, sans étendre automatiquement la généralisation agentique. Des conditions backend, géométriques, temporelles, de compilation et de calibration restent hors du certificat. La nationalité française d'un fournisseur ne prouve pas le lieu d'exécution. Aucun avantage quantique ne peut être inféré de ces références classiques ou simulations.

L'article n'est pas déclaré prêt pour soumission. Restent notamment : contribution originale différenciée par une recherche d'antériorité supplémentaire; annotations et revue finales plus indépendantes; baselines plus fortes à budget documenté; génération réelle de formulations si l'on veut étudier les vérificateurs de coefficients; nouvelle famille agentique et nouveaux groupes; connexion évaluée entre décision d'agent et contraintes SDK/backend; analyse contrôlée de la représentation temporelle Pulser. La prochaine expérience doit choisir une de ces faiblesses et préserver les résultats négatifs, plutôt qu'ajuster encore v4 sur ces données.

## Traçabilité des résultats et annexes

L'historique détaillé et les résultats C01–C10 sont déplacés vers `paper/archive/c01-c10-article.md`, `paper/archive/c01-c10-main.tex` et leurs répertoires `runs/`; aucune preuve historique n'est réécrite. Le registre append-only reste dans `research/claims.json`.

| Groupe de claims | Preuves et portée |
|---|---|
| C01-FINITE, C01-DISTINCT | Optima MIS et probabilités finis; répétitions identifiées |
| C02-CERTIFICATES, C02-WEAK-SUFFICES | Mutations synthétiques et réfutation des contrôles faibles |
| C03-ROUTING | Admissibilité documentaire de 20 propositions, pas accès QPU |
| C04-SEMANTICS, C04-NUMERIC-SUFFICES | Défi de développement et limites de la canonicalisation |
| C05-EXTERNAL-CONTRACT, C05-LEGACY-EXTERNAL-SAFE | Audit externe de schémas et 109 cas relus |
| C06-BASELINES-ONLY | Corpus antérieur et bras natifs historiquement bloqués |
| C07-OPEN-RESOURCES | Acquisition publique, intégrité et smoke local |
| C08-LOCAL-EVALUATED, C09-RESERVED-GUARD | Premiers pilotes LLM; erreur réservée C09 préservée |
| C10-DEVELOPMENT-V4 | Régression post-hoc, aucun nouveau test réservé |
| C11-FROZEN-TRANSFER, C11-RETENTION-HYPOTHESIS | 256 générations nouvelles; critère conjoint H1 non satisfait |
| C12-SDK-PHOTON, C13-SDK-RYDBERG | Validation logicielle finie sous les tolérances déclarées |

Les commandes de reproduction sont dans les manifestes et les vérifications cumulatives; elles doivent utiliser des destinations neuves. Un statut complete signifie cycle terminé, pas hypothèse confirmée ou article publiable.
