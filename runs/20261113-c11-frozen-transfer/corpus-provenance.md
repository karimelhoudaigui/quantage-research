# C11 — provenance du corpus auteur

Corpus écrit par le sous-agent `/root/literature`, distinct de l’intégrateur,
avant toute génération C11. Le rôle a rédigé les intentions et leurs étiquettes;
ce n’est ni une annotation humaine ni une étude aveugle d’accord entre modèles.
Un second rôle doit relire ces annotations avant l’évaluation. L’indépendance
de modèle entre ces rôles n’est pas garantie.

## Connaissance antérieure et séparation

L’auteur a lu core.py et verification.py historiques, C05, le corpus public et
les étiquettes C06 lors d’une ancienne mission de revue, research/state.md et
les résumés C09–C10. Il connaît donc les deux contrats mathématiques et les
échecs historiques généraux. Pour cette création C11, il n’a lu ni code du
veto v4, ni nouveau script C11, ni candidats ni sorties expérimentales C11.
Les chemins déjà présents frozen-inputs.json, historical-snapshot.json,
model-smol.json et protocol.md ont seulement été listés, pas lus. Aucune
optimisation des textes selon une performance du vérificateur n’a eu lieu.
Les quatre fichiers de cette mission ne modifient aucune preuve C01–C10.

Les groupes C01–C10 restent développement. La différence de mots et de nombres
n’établit pas l’absence de contamination du pré-entraînement. Il s’agit d’un
jeu de défi synthétique borné, pas d’un échantillon d’intentions scientifiques
naturelles. Ne pas annoncer un test aveugle à la conception des familles.

## Construction

Commande : `python3 runs/20261113-c11-frozen-transfer/build_corpus.py`.
Python standard, générateur `random.Random`, seed **2026111511**. Aucun LLM
d’inférence externe ni appel SDK/agent n’a été exécuté par le constructeur.
Les textes et modifications de clauses sont rédigés dans le source; seuls
les graphes, poids, angles et l’ordre final des lignes sont pseudoaléatoires.
Le constructeur ne lit ni vérificateur ni scores ni corpus antérieur.

128 cas, 64 groupes appariés : 32 groupes MIS et 32 photon, un cas supporté
et une clause modifiée nécessitant abstention par groupe. 64 intentions EN et
64 FR. Quatre genres : demande directe, note de laboratoire, message à un
collaborateur, fiche structurée; huit groupes par genre et par famille.
Les 32 bases de chaque famille sont des textes distincts, pas quatre gabarits
répétés avec des nombres changés. Les répétitions de la définition de R(t) et
des hypothèses physiques expriment une convention commune indispensable.

MIS : tailles 4 à 12, graphes simples non orientés, poids entiers strictement
positifs 1 à 11. Photon : un photon, deux modes, loss=0, angles réels finis
variés en radians dans le cas supporté. Toutes les données restent identiques
entre les deux membres d’un groupe. 64 jeux de données distincts. Les cas
négatifs changent l’intention, pas les données; certains introduisent donc
explicitement une instruction contradictoire avec le champ de base, à refuser
ou clarifier, sans réparation tacite.

Les négatifs MIS portent sur sens ou quantité d’objectif, maximalité, quotas,
sommets imposés/interdits, implications, budgets, parité et ambiguïtés. Les
négatifs photoniques portent sur entrée, unités, observable, pertes, nombre
de photons et ordre temporel. Pour l’ordre, la phase est déplacée au début
ou à la fin; nous ne reposons pas seulement sur l’échange symétrique a/b.
Les mentions de Pasqal et Quandela restent locales et conditionnelles : elles
ne constituent jamais une preuve d’accès ou une demande de soumission QPU.

## Portée des labels

`expected_action=propose` signifie que l’intention est fidèle au contrat core
complet et que les données sont dans ses bornes; le texte libre doit encore
être interprété par l’agent. `abstain` signifie contrat différent, hors portée
ou ambigu : il ne signifie pas que le problème scientifique soit insoluble.
`expected_task` vaut mis/photon pour propose, null pour abstain. Le type de
clause changée et la justification se trouvent seulement dans le gold auteur.
Le public contient strictement id, group_id et request (intent/data); IDs
opaques hashés et lignes mélangées, sans étiquette attendue explicite.

Un changement d’objectif ou une contrainte peut conserver accidentellement
un optimum numérique sur une instance. Les labels évaluent le contrat complet,
pas seulement la réponse observée. Une équivalence d’optimum ponctuelle ne
prouve pas la fidélité de clauses; inversement aucune différence numérique
n’est affirmée sans calcul. Le constructeur n’a exécuté aucun solveur.

## Contrôles avant relecture

Validation statique des schémas exacts, IDs uniques, 128 textes distincts,
deux cas et données égales par groupe, bornes des données et équilibre des
familles/langues/actions. Comparaison aux seules intentions publiques
historiques des fichiers top-level énumérés ci-dessous : égalité de texte
après casefold et normalisation des espaces, aucune collision. Cette recherche
ne prouve ni absence de similarité sémantique ni séparation d’un corpus naturel.
Aucune sortie brute expérimentale n’a été lue pour ce contrôle.

Fichiers historiques consultés pour le contrôle exact :

- `runs/20261113-c03-routing/cases.json`, SHA-256 `2d3c6b77c102421f683d7dd049c5d7a348640899f11b6420ffc8c462c8f45ce3`.
- `runs/20261113-c04-transfer/cases.json`, SHA-256 `64bf3bfe4f365600bff83824e5d04df6c5c64e1d1b64f2256662a1d2963077b3`.
- `runs/20261113-c06-native-agents/public_cases.json`, SHA-256 `11c3c5b17fe8f3c0c9023c4fd8adb829dc8da739b0a4be4001213f6bdce1d0ae`.
- `runs/20261113-c08-local-agent/cases.json`, SHA-256 `a0c9830b4c73a26ad3c95766c492518cd013f3c2b721b5ee40d4a0b2153287f7`.
- `runs/20261113-c09-heldout-guard/cases.json`, SHA-256 `f7c754c80433ace90db0538a0ae3494856dd964edfd46ec08c62bf38ab100b38`.

Nombre d’intentions publiques comparées : 88.

## Gel auteur

Empreintes SHA-256 après génération et contrôles :

- `build_corpus.py` : `199fbd9efb927b329a0401c6c7ea02d1f43855c64c4e8941c9c8b16ac5d3b83e`.
- `public_cases.json` : `d181acd855b9db47f53763ee8154a03a838e04683ec5bee8de137f04c9480a45`.
- `private_gold.author.json` : `310346755ab71381b44a0458a072451ae5a33e271c3180941071e9e2144886ca`.

La relecture doit citer ces versions. Tout désaccord est résolu par
l’intégrateur avant la génération; garder les annotations auteur originales.
Si le public doit être corrigé, conserver une révision et refiger les hashes.
Ne pas modifier les textes après consultation d’une sortie C11. Le gold, le
constructeur et ce rapport ne doivent pas être donnés à l’agent évalué.

Prochaine action : relecture distincte des 128 cas et adjudication avant toute
inférence. Ces fichiers ne sont pas encore un résultat expérimental C11.
