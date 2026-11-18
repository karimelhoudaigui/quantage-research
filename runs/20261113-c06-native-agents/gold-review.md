# C06 — revue des annotations avant génération

Relecteur : sous-agent `/root/literature`, rôles compréhension et vérification.
Date : 13 novembre 2026, 13:20:11 UTC. Aucun candidat ni résultat expérimental
consulté; seuls corpus public, gold, core, verification et politique ont été lus.
La lecture des étiquettes gold est déclarée : ce contrôle est une seconde
dérivation, pas une annotation aveugle. Le relecteur est distinct de l’auteur
du corpus, sans garantie de modèle distinct; aucun annotateur humain.

## Verdict

**31 accords et 1 désaccord d’action sur 32 cas. Adjudication nécessaire avant
génération.** Le JSON contient un avis et sa justification pour chaque id.
Les avis du relecteur comportent 19 propose et 13 abstain; le gold lu comporte
20 propose et 12 abstain. Ce désaccord n’est pas une mesure de performance.

Contrat appliqué : canonicalisation vers le moteur figé sans changer les
données et avec fidélité à l’objectif, aux contraintes et aux hypothèses
explicites. Les sorties numériquement égales sur une instance ne remplacent
pas cette fidélité. Les labels portent sur ce contrat logiciel borné.

## Désaccord à résoudre

`q_33cf35350c7a` : le gold indique propose; je propose **abstain avec
clarification de direction d’objectif**. Texte exact :

> Optimiser la somme des poids d’un sous-ensemble indépendant de ce graphe non orienté : une arête interdit de sélectionner ses deux extrémités, chaque choix est binaire. Je demande une référence de calcul locale; Pasqal est seulement une piste conditionnelle future.

«Optimiser la somme des poids» ne détermine pas maximiser ou minimiser.
Le texte ne dit pas «poids maximal» et ne nomme pas explicitement MIS. Avec
des poids positifs et sans cardinalité imposée, minimiser peut retenir le
vide alors que maximiser retient un ensemble non vide; core fixe le second
problème. Le contexte Pasqal/local ne lève pas l’ambiguïté mathématique.

Résolution proposée : conserver le texte figé et corriger l’étiquette en
abstain. Si l’auteur voulait maximiser, remplacer ce mot explicitement puis
refaire le gel et les hashes avant tout candidat. Ne pas corriger après
génération en fonction des performances observées.

## Réserves sans désaccord d’action

- `q_fa5c340df7d4` : abstain est défendable car cible de phase contradictoire
  ou corrigée par une dernière exigence hors contrat. Toutefois, pour ces
  rotations réelles, changer la cible mode 1 en mode 0 peut conserver les
  probabilités; c’est un test de fidélité du contrat/clarification, pas un
  contre-exemple garanti de faux résultat numérique.
- `q_59406adaa7b5` : cardinalité et poids sont deux objectifs distincts, même
  si le même ensemble peut optimiser les deux sur cette instance. Le refus
  suppose explicitement un score de contrat complet et données inchangées.
- `q_2c074443d82b` : poids nul rejeté par le moteur positif; cela ne signifie
  pas qu’un MIS à poids nul soit mathématiquement mal défini.
- Les mentions de Pasqal/Quandela avec demande locale et interdiction QPU
  sont du contexte conditionnel, pas une exigence matérielle qui forcerait
  un refus. Les quatre cas de cette sorte restent propose, sauf ambiguïté
  de direction propre à q_33cf35350c7a.
- Les angles négatifs sont des réels autorisés; les degrés explicitement
  non convertibles, pertes non nulles, amplitudes et deux photons sortent
  du contrat. Mode d’entrée non fixé et objectif non résolu appellent
  clarification, plutôt qu’une valeur par défaut.

## Avis par id

| Id | Gold | Avis | Accord | Motif |
|---|---|---|---|---|
| q_47eb07193267 | propose | propose | oui | Somme de poids explicitement maximale, choix binaires, arêtes de conflit non orientées; deux poids positifs et extrémités valides. |
| q_2c074443d82b | abstain | abstain | oui | Le poids du sommet 2 vaut 0. La définition mathématique du MIS peut admettre ce poids, mais core exige strictement des entiers positifs; le texte interdit de modifier les poids. |
| q_2f2e839717d9 | propose | propose | oui | Probabilités, entrée \|1,0>, deux modes cohérents sans pertes; R(t) réel explicitement défini, phase mode 1, ordre temporel R(a), P, R(b), radians. |
| q_26a31ac7003d | propose | propose | oui | Objectif de somme de poids maximale et exclusion des voisins explicités; le graphe sans arêtes est valide, aucun sommet ou poids ne manque. |
| q_947ea6516776 | propose | propose | oui | Même contrat optique explicite en français; angle b négatif autorisé car fini réel, et non une perte ou probabilité. |
| q_b8ccfcda3441 | propose | propose | oui | La probabilité de chacune des deux issues est la distribution ordonnée des modes; source, cohérence, pertes nulles, convention, ordre et radians sont explicites. |
| q_e1e7124a8604 | abstain | abstain | oui | Le texte réclame deux amplitudes complexes, expressément sans module au carré. core ne retourne que leurs probabilités. |
| q_aab7987d440e | abstain | abstain | oui | loss=0.04 doit être inclus et le texte interdit de remplacer le modèle par un circuit sans pertes; le contrat local ne le permet pas. |
| q_be0c1190deaa | propose | propose | oui | Le calcul demandé est local, sans exécution matérielle; Quandela est un intérêt de contexte. Tous les éléments optiques du contrat local sont explicites. |
| q_ca9678cc7da3 | propose | propose | oui | Quandela est seulement une future plateforme possible et toute soumission actuelle est exclue; le contrat de référence optique local est complet. |
| q_7cf4e858e97b | propose | propose | oui | Entrée \|1,0>, sorties probabilistes, deux modes, cohérence et pertes nulles; convention réelle, chronologie, cible de phase et radians déterminés. |
| q_59406adaa7b5 | abstain | abstain | oui | Le texte ignore explicitement les poids et maximise le nombre de sommets. Données inchangées, cela ne représente pas le même objectif que core, même si cette petite instance peut partager un optimum. |
| q_d201e47573a0 | propose | propose | oui | Maximum de somme des poids, incompatibilités non orientées, variables binaires et données valides; Pasqal est un intérêt futur avec demande locale et interdiction de soumettre. |
| q_ba86bb306293 | propose | propose | oui | Deux probabilités idéales avec entrée \|1,0>, circuit cohérent sans pertes, R réel, phase mode 1 et radians; second mode explicité comme index 1. |
| q_93b97a91759c | abstain | abstain | oui | n=3 exige trois poids; la liste ne contient que 9 et 6. Incohérence non réparable sans inventer ou supprimer un sommet. |
| q_6bf2519d6be0 | abstain | abstain | oui | Le texte impose des degrés et interdit conversion ou réinterprétation. core attend radians; remplacer uniquement le texte sans convertir violerait la requête. |
| q_8d4693aec7e5 | propose | propose | oui | Poids total explicitement le plus grand, graphes non orientés, choix binaires, absence de condition supplémentaire; données valides. |
| q_1d0d82d4a9b8 | propose | propose | oui | Le texte réclame les probabilités idéales, pas les amplitudes; entrée, ordre, phase mode 1, radians et pertes nulles conformes. a négatif reste dans le domaine réel. |
| q_c8460a41cbce | propose | propose | oui | Distribution du mode contenant un photon équivaut aux deux probabilités de sortie; tous les composants, leur ordre, entrée et hypothèses sont fixés. |
| q_508994ad3b05 | abstain | abstain | oui | Exactement deux sommets est une contrainte obligatoire; core impose seulement indépendance. Sur cette étoile les optimums contraints et non contraints ne coïncident pas. |
| q_19d11c70f915 | propose | propose | oui | Somme de poids explicitement maximale, chaque choix au plus une fois et aucun couple incompatible; six poids positifs associés aux six sommets valides. |
| q_fa5c340df7d4 | abstain | abstain | oui | Le texte affirme successivement la phase sur mode 1 puis exige de ne pas la mettre sur mode 1 et de la mettre sur mode 0. Le contrat complet doit être clarifié; si la dernière phrase prime, la cible structurale est hors core. Réserve: les probabilités seules peuvent néanmoins coïncider pour les rotations réelles de ce banc. |
| q_044a69872b75 | propose | propose | oui | Probabilité de chaque mode, entrée \|1,0>, circuit cohérent sans pertes, convention réelle et radians; une phase négative est valide. |
| q_7dc8bd369f02 | abstain | abstain | oui | n=4 autorise les indices 0..3; une arête mentionne 4. Le texte interdit de renuméroter ou corriger. |
| q_d615a33b3e3a | propose | propose | oui | Maximiser le poids cumulé avec seules exclusions par arêtes et variables binaires; les arêtes vides ne rendent pas le contrat incomplet. |
| q_ad48958b4f32 | abstain | abstain | oui | Le texte dit expressément que poids ou cardinalité restent indécidés et interdit de choisir à sa place. Une clarification de direction/objectif est nécessaire. |
| q_102ff810a069 | propose | propose | oui | Poids total maximal explicite, indépendance, binarité et aucune autre contrainte; quatre sommets et poids positifs valides. |
| q_33cf35350c7a | propose | abstain | **non** | Le verbe «Optimiser» ne fixe pas le sens maximiser/minimiser. Aucun «maximal», «maximiser» ou «MIS» ne le lève dans cette intention. Le contrat core impose maximiser et ne peut fournir cette décision tacite. |
| q_b3da77afac4f | abstain | abstain | oui | Entrée \|1,1> et photons=2 réclament deux photons; ni les occupations ni le modèle peuvent être ramenés silencieusement à un photon. |
| q_9a214e12ea8b | propose | propose | oui | La plus grande somme de poids, explicitement distincte du nombre de sommets, est demandée sous indépendance binaire non orientée; données positives valides. |
| q_e9c9eeaaec7d | propose | propose | oui | La somme des poids est explicitement maximisée avec contraintes de conflits non orientés et choix binaires; données valides. |
| q_ea7fda3d1cde | abstain | abstain | oui | Mode initial non spécifié et choix de 0 ou 1 expressément interdit; fixer \|1,0> introduirait une hypothèse non autorisée. |

## Empreintes des entrées

SHA-256 observés avant écriture du rapport :

- `runs/20261113-c06-native-agents/public_cases.json` : `11c3c5b17fe8f3c0c9023c4fd8adb829dc8da739b0a4be4001213f6bdce1d0ae`.
- `runs/20261113-c06-native-agents/private_gold.json` : `ca4315838310f93441101f160273385545758d5438bb373f84c1b84825eafd71`.
- `quantage/core.py` : `35001246743a201d2326a53a586fd50bedca48d8e322f52124f2a3e0c7403be2`.
- `quantage/verification.py` : `c7d070281763bb46ad6244ef1c0bc4734c159bc32d5adca1dfac6e9786f6426f`.
- `config/policy.json` : `bf40f7dc349b1e22468e14e4d31ce34f5e17c21f8e45459d71bb062e3fd0fc7b`.

Ces empreintes authentifient les fichiers lus, pas la vérité des annotations.
Aucune donnée de corpus, code, gold ou fichier commun n’a été modifié.
La revue demeure pending pour adjudication de q_33cf35350c7a.
