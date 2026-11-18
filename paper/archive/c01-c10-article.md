# Certificats de sortie, fidélité sémantique et admissibilité du solveur

QuantAge — document de travail, 13 novembre 2026.

## Résumé

Nous construisons un banc déterministe pour étudier les contrôles d'une chaîne intention → problème → formulation → solveur. Deux familles aux oracles différents, le MIS pondéré et l'interférométrie idéale à un photon, permettent de séparer trois questions : le contrat a-t-il été compris, ses sorties sont-elles préservées et la recommandation de solveur est-elle justifiée ? Des expériences locales montrent les limites de contrôles faibles et du parsing par mots-clés. Après les baselines déterministes, C08 et C09 produisent 48 réponses réelles d’un petit LLM local sur deux étapes séparées par groupes. Aucun SDK quantique ni QPU n’est exécuté; la compréhension LLM est suivie d’une formulation déterministe. Ces résultats constituent un socle d'évaluation, sans validation de performance agentique, de nouveauté ou d'avantage quantique.

## Question et travaux proches

La question centrale est la portée d'un certificat : que permet-il d'affirmer sur la chaîne complète ? NL4Opt évalue déjà la reconnaissance d'entités et la représentation intermédiaire des problèmes d'optimisation [Ramamonjison et al., 2023](https://proceedings.mlr.press/v220/ramamonjison23a/ramamonjison23a.pdf). OptiMUS distingue les erreurs d'extraction, de formulation et de code [AhmadiTeshnizi et al., v4, 2026](https://arxiv.org/html/2407.19633v4). Notre distinction est adjacente à ces travaux, et ne constitue pas une revendication de nouveauté. La revue est ciblée, pas exhaustive; les sections réellement consultées et les versions sont consignées dans research/sources/index.json.

Les huit axes du programme sont comparés dans research/opportunity-map.md. Nous retenons deux bancs avec des oracles locaux peu coûteux. La littérature spécialisée des six autres axes reste à approfondir.

## Contrats et méthodes

La baseline stricte reçoit une intention en langage contrôlé et des données JSON; elle accepte exactement deux phrases documentées dans examples/. Elle valide les domaines, les contraintes et les champs, formule le problème, vérifie ses sorties puis choisit un solveur local. Les intentions inconnues et les variantes non prises en charge provoquent une abstention. Ce parseur strict ne comprend pas le langage naturel général. Les bras LLM C08–C10 reçoivent un texte libre et les mêmes données structurées, puis proposent un contrat compact.

Nous séparons la fidélité de l'interprétation initiale, le certificat numérique d'une instance normalisée et l'admissibilité documentaire d'une recommandation. Le module de revue des propositions matérielles est évalué séparément; il ne compile aucun programme physique. Une validation des sorties après normalisation n'atteste pas que la normalisation correspond au texte.

Pour un graphe simple non orienté, avec poids entiers strictement positifs, le MIS pondéré maximise $\sum_i w_i x_i$ sous $x_i+x_j\leq1$ pour chaque arête, avec $x_i\in\{0,1\}$. La QUBO minimise

$$Q(x)=-\sum_i w_i x_i+P\sum_{(i,j)\in E}x_i x_j,\qquad P=1+\max_i w_i.$$

Chaque arête est comptée une fois. Retirer un sommet sélectionné ayant $d_i\geq1$ voisins sélectionnés change l'énergie de $w_i-Pd_i<0$. Tout minimiseur est donc indépendant et, sur les indépendants, minimiser $Q$ maximise le poids. Le cas non pondéré est classique [Lucas, 2014, §4.2](https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2014.00005/full); l'argument pondéré ci-dessus est direct. Pour $K_2$, $w_0=w_1=P=1$, les états $01$, $10$ et $11$ minimisent tous $Q=-1$ : la borne non stricte peut conserver un optimum infaisable.

Le second contrat est un photon entrant en mode 0 d'un circuit idéal à deux modes,

$$U=R(b)\operatorname{diag}(1,e^{i\phi})R(a),\qquad R(t)=\begin{pmatrix}\cos t&-\sin t\\\sin t&\cos t\end{pmatrix}.$$

Les angles sont en radians, sans pertes, bruit, post-sélection ou shots. L'algorithme propage les amplitudes; l'oracle utilise l'expression développée

$$p_0=\cos^2a\cos^2b+\sin^2a\sin^2b-2\cos a\sin a\cos b\sin b\cos\phi,\qquad p_1=1-p_0.$$

La tolérance absolue est $10^{-12}$. Notre $R(t)$ correspond à BS.Ry(theta=2t) dans les conventions documentaires de Perceval 1.3, et pas à son composant par défaut [documentation des composants](https://perceval.quandela.net/docs/v1.3/reference/components/unitary_components.html). Cette traduction n'a pas été exécutée dans le SDK. Les hypothèses de source et de détection deviennent essentielles au-delà du modèle idéal [Heurtel et al., 2023](https://arxiv.org/html/2204.00602).

Les références fortes sont l'énumération complète des sous-ensembles faisables et l'oracle optique analytique. Le glouton est une heuristique complémentaire. Les comparaisons initiales sont des ablations déterministes : contrôle d'une seule solution ou de normalisation, identité syntaxique, revue des modalités et portée des promesses, parsing strict ou par mots-clés. Les mutations sont des propositions synthétiques, jamais des sorties LLM.

## Protocole et résultats

Les expériences numériques possèdent un protocole écrit avant exécution, un contrat de calcul, les lignes brutes, les agrégats et un manifest v2 avec commandes, versions, commit de départ, empreintes observées avant/après et durées. C07 conserve des manifestes d'acquisition et de smoke distincts. Base Git fee83eb, arbre modifié durant la campagne. C01–C04 utilisent Python 3.9.6 et sa bibliothèque standard, avec une limite de 60 secondes par expérience; les générations locales ultérieures ont des dépendances et budgets propres. Aucun entraînement. C01–C03 servent au développement; C04 gèle le moteur et change tailles, angles et textes. Le corpus C04 reste conçu par l'auteur connaissant le parseur; ses paires de langage partagent les données numériques. Il ne s'agit pas d'un test aveugle.

| Cycle | Domaine effectivement testé | Résultat observé | Claim |
|---|---|---|---|
| C01 | 1 199 évaluations MIS, dont 1 194 entrées distinctes; 125 triplets optiques | Tous les ensembles d'optima concordent; erreur optique maximale $2.22\times10^{-16}$ | C01-FINITE, C01-DISTINCT |
| C02 | 2 225 propositions mutées, dont 795 changent la sortie contractuelle | 267 erreurs acceptées par le contrôle faible; 0 par l'oracle complet | C02-CERTIFICATES |
| C03 | 20 recommandations annotées, dont 14 non justifiées | 13, puis 4, puis 0 fausses acceptations après contrôles nom, modalité, portée; 6 recommandations admissibles conservées | C03-ROUTING |
| C04 | 24 requêtes de défi, dont 12 équivalentes au contrat | Strict : 6/12 couvertes, 0/12 cas hors contrat acceptés; mots-clés : 12/12 couvertes, 6/12 cas hors contrat acceptés | C04-SEMANTICS |
| C05 | 67 propositions externes + 6 frontières; revue séparée de 109 cas | 23 acceptations malformées de l’interface historique directe rejetées, 11 contrôles conservés; revue concordante | C05-EXTERNAL-CONTRACT |
| C06 partiel | 32 requêtes, 19 supportées après relecture | Strict : couverture 0/19, erreurs 0/13; mots-clés : 9/19 et 5/13; zéro candidat natif évalué | C06-BASELINES-ONLY |

C01 énumère tous les 1 099 graphes simples étiquetés de tailles 1 à 5 à poids unitaires, puis évalue 100 graphes pondérés de tailles 2 à 6, seed 20261113; 5 requêtes MIS se répètent. Les optima sont comparés sur 36 346 états binaires. Le glouton est sous-optimal sur 4 évaluations, avec un écart absolu maximal de 2. La grille optique comporte 125 triplets prescrits. Ces comptages ne prouvent pas une propriété d'une population d'instances réelles.

C02 utilise les graphes de taille au plus 4 et les graphes pondérés de C01, avec sept mutations MIS et huit mutations optiques. Parmi les 795 changements effectifs, le contrôle faible manque 90 erreurs MIS et 177 optiques. Les 1 430 autres propositions préservent la sortie de leur instance et sont acceptées par l'oracle complet. Son absence de fausse acceptation découle de sa comparaison au même oracle qui définit l'erreur; elle ne mesure pas une performance indépendante de détection sur du LLM. Un changement de constante, un rescaling positif ou une phase globale peut être fidèle sans être syntaxiquement identique. Inverser les rotations, changer le signe de $\phi$ ou déplacer la phase sur l'autre mode conserve aussi les probabilités de ce contrat. Le certificat ne distingue donc pas les circuits ou amplitudes correspondants. La suffisance des contrôles faibles est réfutée par contre-exemples (C02-WEAK-SUFFICES).

C03 compare des règles sur des labels manuels. «Admissible» signifie recommandation locale ou candidat conditionnel dans le périmètre documentaire du projet, jamais faisabilité physique établie. Une QUBO abstraite n'est pas automatiquement un programme Pasqal : le registre et les interactions dépendent de la géométrie [Pulser 1.8.0](https://docs.pasqal.com/pulser/v1.8.0/register/). Un objet Device et une connexion QPU sont distincts [spécifications matérielles](https://docs.pasqal.com/pulser/v1.8.0/hardware/). De même, simulation et acquisition distante restent distinctes chez Quandela [Perceval 1.3](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html). La nationalité du fournisseur ne détermine pas le lieu d'exécution. Aucun accès de compte n'a été vérifié; aucune permission physique n'est émise. SpinPulse n'est ni utilisé ni assimilé au bruit Pasqal.

C04 utilise seed 20261114, trois MIS de tailles 7, 8 et 8 et trois nouveaux triplets optiques. Les six paraphrases équivalentes sont toutes refusées par le mode strict. Le mode mots-clés accepte aussi six intentions changées; leurs six sorties reçoivent néanmoins un certificat numérique valide après la mauvaise interprétation. Un certificat de sortie ne suffit donc pas à vérifier l'intention (C04-NUMERIC-SUFFICES réfuté).

## Propositions externes et collecte réelle : C05–C06

C05 distingue le générateur interne figé de la future interface recevant des propositions externes. Un auditeur distinct a trouvé 23 acceptations mal formées dans 67 appels directs à l’ancien vérificateur, par exemple un sens inconnu silencieusement traité comme une maximisation, des indices Python négatifs ou des métadonnées non finies ignorées (C05-LEGACY-EXTERNAL-SAFE réfuté). L’ancien CLI, qui construit lui-même ses modèles, refuse déjà les six entrées invalides testées. Aucun résultat C01–C04 n’est réfuté par ces contre-exemples.

La nouvelle frontière quantage/contracts.py contrôle explicitement problème normalisé, schéma, types, indices, enums, tolérance et métadonnées avant l’oracle de sorties. Elle rejette les 23 acceptations invalides et conserve 11 contrôles. Une revue par un auteur distinct vérifie 109 cas, dont 42 supplémentaires : 81 rejets au schéma, 4 rejets numériques et 24 acceptations attendues, sans divergence (C05-EXTERNAL-CONTRACT). Le domaine QUBO externe est entier. La revue n’est pas aveugle, et l’indépendance de modèle n’est pas établie. Les anciens fichiers hashés ne sont pas modifiés.

C06 comporte 32 nouvelles requêtes écrites par un autre rôle, puis relues séparément avant collecte. Les annotateurs s’accordent sur 31 actions; le désaccord «optimiser» sans direction est arbitré en abstention, avec versions originales conservées. Les labels finaux ont 19 contrats supportés et 13 abstentions. Sur ce corpus, le strict refuse tout; les mots-clés couvrent 9/19 contrats et acceptent 5/13 cas hors contrat. Le risque parmi leurs 14 acceptations est 5/14; les 14 sorties obtiennent pourtant un certificat numérique valide (C06-BASELINES-ONLY). Ces labels sont des annotations d’agents, pas une étude humaine aveugle.

Deux vraies tâches natives de génération ont été lancées en contextes neufs et interrompues par quota avant toute réponse; le bras documenté n’a pas été lancé ensuite. Aucun candidat natif n’est évalué, et aucune performance n’est imputée aux bras absents. Le cycle reste historiquement blocked pour sa question centrale, malgré le run local des baselines terminé. Prompts et échecs sont conservés dans generation_record.json. L’utilisateur a ensuite autorisé une recherche publique : C07 acquiert des archives et C08–C09 génèrent localement sous des protocoles distincts. Les archives ne remplacent pas les candidats natifs manquants. La chaîne quantage/agent_pipeline.py et l’évaluateur quantage/evaluation.py traitent les propositions enregistrées sans lire les labels pendant exécution.

## Ressources ouvertes : C07

La demande de recherche publique débloque une alternative au quota natif. Douze fichiers publics sont acquis depuis QCV et PQID-Bench, à commits fixes, avec licences et empreintes. L’archive PQID contient 70 enregistrements de réponses Qwen2.5-Coder-7B, dont 51 codes non vides liés aux payloads bruts et 19 sans code. Les 70 requêtes et réponses partagent leurs trois hashes de liaison. Ces métadonnées sont des déclarations des auteurs, sans authentification fournisseur; aucun code généré n’est exécuté et aucun score QuantAge n’est attribué à ces archives. Voir [QCV](https://github.com/QuantBlockchain/quantum-circuit-vision) et [PQID-Bench](https://github.com/Elias-Abebe-Gasparini/PQID-Bench).

Un checkpoint distinct [Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct), Apache-2.0, révision 7ae557604adf67be50417f59c2c2f167def9a775, est acquis : neuf fichiers, 999 602 607 octets. Le SHA-256 des poids Safetensors correspond à la métadonnée LFS. Un vrai smoke test CPU hors ligne produit le JSON ready=true, sans cas scientifique. Cela établit la faisabilité locale, pas la fidélité ou la performance de l’agent (C07-OPEN-RESOURCES). Le benchmark C08 préenregistre séparément un agent hybride à contrat compact, formulation déterministe et référence locale. Il ne remplace pas silencieusement les bras natifs manquants C06.

## Premier pilote local : C08

Le protocole C08 sélectionne sans labels quatre groupes lexicographiques par famille parmi C06 : 16 requêtes appariées, huit par famille, dont dix supportées et six hors contrat. Les groupes sont sélectionnés avant génération et ne sont pas utilisés pour entraîner le modèle. L’agent hybride demande au LLM un contrat compact (action, famille, tâche, raison), copie les données d’origine, puis formule et choisit la référence locale déterministement. Il ne s’agit pas d’un bras où le LLM invente tous les coefficients ou d’un choix matériel validé.

Le checkpoint Qwen2.5-0.5B-Instruct de C07 génère réellement 32 réponses, instruction seule puis instruction avec dossier pour chaque cas. CPU float32, quatre threads, torch 2.8.0, Transformers 4.45.2, greedy, seed 20261113, maximum 192 nouveaux tokens. Les messages, sorties brutes, fin de génération, tokens et temps sont conservés; labels absents du programme de génération.

| Méthode sur les mêmes 16 cas | Supportés couverts /10 | Hors contrat acceptés /6 | Risque parmi acceptations |
|---|---:|---:|---:|
| Strict |0|0|non défini|
| Mots-clés |3|1|1/4|
| Hybride sans dossier |5|2|2/7|
| Hybride avec dossier |4|2|2/6|

Les deux erreurs MIS acceptées dans chaque bras obtiennent un certificat numérique valide. En photonique, les huit réponses de chaque bras indiquent family=mis et une tâche photonique; le contrôle de schéma les refuse toutes, y compris cinq tâches supportées. Deux réponses MIS documentées utilisent aussi une tâche inconnue. Ces contradictions ne sont pas de simples erreurs de syntaxe JSON et restent visibles; aucune réparation après score. Parmi les réponses conformes, le modèle ne choisit jamais l’abstention. Les refus du contrôleur ne sont donc pas crédités comme une bonne compréhension du LLM (C08-LOCAL-EVALUATED).

Le dossier n’améliore pas ce pilote : une acceptation correcte sans dossier devient un refus, aucune mauvaise acceptation n’est corrigée sur les 16 paires. Il ajoute des tokens d’entrée (18 642 contre 8 146) et le temps de génération observé est 216.75 s contre 152.76 s. Le run complet dure 378.40 s de temps écoulé avec chargement, pour 26 788 tokens d’entrée et 2 015 de sortie; les bibliothèques, poids et commandes sont figés. Coût d’achat externe 0, coût machine/énergie et développement non mesuré; pas de conclusion statistique ou de budget d’entrée égal.

Ce résultat négatif motive C09, préenregistré ensuite sur les autres groupes C06 : retirer la famille redondante et comparer, sur les mêmes nouvelles réponses, un contrôleur numérique et un veto textuel borné. C08 est dès lors du développement; il ne sera pas fusionné avec C09 comme un unique test aveugle.

## Groupes réservés et correction du prototype : C09–C10

C09 supprime le champ famille redondant, garde le même checkpoint, et génère une seule réponse par requête sur les huit groupes C06 non présentés en C08 : 16 cas, dont neuf supportés et sept hors contrat. Le schéma exige action, tâche et raison. Une comparaison appariée applique aux mêmes propositions le contrôle des types/données et l’oracle numérique, puis un veto textuel borné, fixé avant ces réponses. Il vérifie des marqueurs de direction, poids, contraintes, observable, unités et phase, sans lire les labels. Ce n’est pas un analyseur universel d’entailment.

| Méthode sur les mêmes 16 cas réservés | Supportés couverts /9 | Hors contrat acceptés /7 | Risque parmi acceptations |
|---|---:|---:|---:|
| Strict |0|0|non défini|
| Mots-clés |6|4|4/10|
| Hybride sans veto textuel |7|3|3/10|
| Même réponse avec veto |5|1|1/6|

Le veto retire deux acceptations erronées et deux acceptations correctes (C09-RESERVED-GUARD). La demande résiduelle précise que le mode d’entrée est inconnu et interdit de le choisir; la seule présence du token mode 0 ne prouve pas qu’il est fixé. Le LLM propose pourtant l’exécution, même si sa raison dit que l’information manque. Le contrôleur choisit alors l’entrée par défaut et son certificat numérique passe. Les refus valides manqués concernent les synonymes greatest value et distribution. Par famille, avant veto : MIS 4/4 supportés et 2/4 hors contrat acceptés; photonique 3/5 et 1/3. Après veto : MIS 3/4 et 0/4; photonique 2/5 et 1/3. Les deux familles ont donc des exécutions réelles, sans garantie générale de fidélité.

Les 16 appels se terminent sans réponse manquante, avec 6702 tokens d’entrée et 842 de sortie, en 130.58 s avec chargement. Un JSON porte une abstention avec tâche non nulle et est refusé au schéma; aucune abstention conforme du modèle. Les coûts avant/après veto sont ceux des mêmes générations, pas deux collectes. C08 et C09 n’ont pas les mêmes cas : leurs différences ne permettent pas d’isoler causalement l’effet de changement du schéma. Les huit groupes de chaque étape sont disjoints dans le protocole de génération; pas de revendication d’absence de toute contamination pré-entraînement.

C10 livre une correction après consultation de C09. Reconnaître les synonymes et refuser l’entrée inconnue restaure deux acceptations correctes, mais ouvre d’abord une autre erreur : l’objectif est explicitement non décidé entre poids et nombre de sommets. Cette version v3 à une erreur reste archivée. La version v4 donne priorité aux clauses d’objectif non résolu. Sur les mêmes 16 propositions déjà connues, elle accepte 7/9 tâches supportées et 0/7 hors contrat, avec deux refus de tâches supportées (C10-DEVELOPMENT-V4). Par famille : MIS 4/4 et 0/4; photonique 3/5 et 0/3. **Ce zéro est une régression de développement après consultation, pas un nouveau résultat réservé.** Le résultat primaire C09 conserve son erreur résiduelle.

Le CLI final reçoit une intention JSON, génère réellement un contrat compact hors ligne, applique v4, copie les données, formule, vérifie les sorties et sélectionne la référence locale. Trois smokes sur des cas connus reproduisent exactement les textes bruts avec cette configuration et obtiennent les statuts attendus : acceptation d’une distribution photonique explicite, refus d’une entrée inconnue, refus d’un objectif inconnu. Ils ne sont ni de nouveaux cas indépendants ni une preuve de reproductibilité universelle. Les raisons libres et la compatibilité QPU ne sont pas certifiées.

## Limites, coût et prochaine expérience

C01–C04 étaient auto-revus par leur auteur. C05 dispose ensuite d’un auditeur distinct; le corpus C06 d’un auteur et d’un relecteur distincts de l’intégrateur. Ces rôles peuvent partager la même famille de modèle et voient l’état du projet : aucune indépendance de modèle ou annotation humaine aveugle n’est établie. Le quota a de nouveau interrompu la génération des candidats. Les zéros d'erreur s'appliquent aux jeux finis déclarés. Les corpus sont déterministes ou synthétiques de convenance, avec répétitions et paires : nous ne calculons pas d'intervalles de confiance pour une population naturelle non définie. Aucun score de confiance ou calibration probabiliste n'est évalué.

Les temps des manifests mesurent les processus locaux, pas le coût complet de conception, de raisonnement, de recherche documentaire ou de cette session. C08–C09 disposent de 48 réponses locales réellement évaluées sur 32 requêtes uniques dans 16 groupes; aucun job QPU ou achat externe; la session elle-même a un coût non mesuré. Les bras complets où le LLM propose tous les coefficients et la politique apprise restent non exécutés; seuls les contrats compacts hybrides sont évalués, avec conditions de reprise dans research/blockers.json. La source LaTeX est synchronisée mais aucun compilateur n'est disponible; aucun PDF validé.

Les ressources publiques et le prototype local sont disponibles. Le prochain test scientifique doit employer de nouveaux groupes annotés séparément, avec v4 figé et sans correction après consultation. Tous les groupes C06 ont maintenant été utilisés; ils sont développement pour les versions futures. Les archives publiques restent un complément rétrospectif distinct. Comparer les mêmes sorties avant/après vérification, en séparant fidélité de l'intention, fidélité de la sortie et portée matérielle; enregistrer modèle/version, tokens, latence et coût. Geler les textes par groupes sémantiques et réserver séparément familles et tailles; ne pas entraîner sur C04 après consultation puis le présenter comme test. Une revue indépendante du nouveau veto et des scores reste nécessaire dès que le quota le permet. Les modèles multiphotoniques et les autres axes restent proposés.
