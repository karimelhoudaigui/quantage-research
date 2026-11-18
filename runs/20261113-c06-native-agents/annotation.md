# C06 — Provenance et annotation du corpus natif

Corpus fixé le 13 novembre 2026 à 13:18 UTC, avant consultation de propositions
candidates ou du nouveau garde de compréhension. Base Git observée :
`fee83eb4575198e3e142d41c621300b4d11361d8`; travail local non committé.

## Auteur et indépendance

Auteur : assistant natif de cette session, sous-agent `/root/hardware`, chargé
pour cette tâche des rôles `solver/dataset_author`. Le nom exact du modèle et
sa consommation de tokens ne sont pas exposés par l'interface; ils ne sont pas
inventés. Aucun appel API externe, sortie de benchmark ou proposition de
solveur n'a été généré dans cette tâche.

L'auteur a lu les fiches `agents/problem.md` et `agents/experiment.md`, le
contrat existant dans `quantage/core.py`, le protocole C04 et l'état antérieur
du projet. Il connaît donc les familles et leurs limites. Il n'a pas consulté
les formulations textuelles du corpus C04, les sorties des agents candidats
C06, ni le nouveau garde sémantique. Les textes sont rédigés pour cette tâche,
sans reprise textuelle du testbed C04. La séparation entre auteur et évaluateurs
est fonctionnelle, pas une indépendance institutionnelle ou de distribution :
une même famille de modèle peut intervenir des deux côtés. Aucun annotateur
humain aveugle n'a validé ces étiquettes. Le corpus est synthétique et conçu à
partir de limites connues; il ne représente pas une population naturelle.

## Construction et règles d'annotation

32 requêtes : 16 MIS et 16 photoniques. Dans chacune des deux familles,
10 requêtes portent exactement sur le contrat mathématique supporté et
6 imposent une abstention. Les 20 cas supportés sont des paraphrases EN/FR,
avec données conservées, sans ajout de contrainte ni hypothèse à résoudre.

- MIS supporté : choix binaires, graphe non orienté, somme des poids à
  maximiser et aucune paire adjacente sélectionnée; aucune autre contrainte.
  Tailles 2 à 6, poids entiers strictement positifs et arêtes valides.
- Photonique supportée : entrée `|1,0>`, deux modes, un photon, modèle cohérent
  idéal sans pertes; `R(t)=[[cos(t),-sin(t)],[sin(t),cos(t)]]`; ordre temporel
  `R(a)`, phase `exp(i*phi)` sur le mode 1, `R(b)`; angles en radians;
  probabilités des deux sorties. Chaque requête fixe ces conventions.
- Abstentions MIS : objectif cardinalité au lieu du poids; contrainte de
  cardinalité obligatoire; objectif explicitement indécis; discordance n/poids;
  extrémité d'arête hors domaine; poids nul hors contrat strict.
- Abstentions photoniques : deux photons; pertes non nulles requises; degrés
  explicitement fournis avec interdiction de conversion; amplitudes complexes
  demandées; mode d'entrée explicitement indéterminé; instructions contradictoires
  sur le mode où appliquer la phase.

Les étiquettes résultent de cette comparaison de contrats, rédigée avant toute
évaluation. Elles n'utilisent pas une règle lexicale cachée. Un nom de fournisseur
ne détermine jamais l'action. Quatre cas supportés mentionnent Pasqal ou Quandela
comme souhait futur et demandent une référence locale, sans soumission QPU.
La sortie exacte attendue pour `canonical_intent` est la constante du moteur
pour les seuls cas supportés; elle est `null` pour toute abstention.

## Groupes et séparation

16 groupes opaques de deux requêtes, huit groupes par famille. Chaque groupe
réutilise une instance de base : soit une requête supportée et une variante à
abstenir (six groupes par famille), soit deux paraphrases supportées
(deux groupes par famille). Les trois défauts MIS de données modifient seulement
le champ explicitement invalide. La perte et le nombre de photons modifient les
champs correspondants. Les autres variations changent l'intention.

Les identifiants de cas et groupes sont des chaînes pseudorandomisées sans
préfixe de famille, étiquette ou split; l'ordre public est mélangé. Ils ont été
générés avec `random.Random(2026111306)` sous Python 3.9.6. La rédaction des
phrases et les valeurs des instances sont manuelles; la seed ne sert qu'aux
identifiants et à l'ordre. Aucun split entraînement/test n'est attribué ici.
Tout split futur doit conserver les groupes entiers afin d'éviter une fuite
par données partagées. Les 32 lignes ne sont pas 32 observations indépendantes.

Le public contient exclusivement `id`, `group_id` et `request` (avec `intent`
et `data`), sans annotation. `private_gold.json` est une convention de séparation
dans le dépôt, pas un contrôle d'accès : le coordinateur doit transmettre aux
évaluateurs seulement le fichier public et leur interdire la lecture du gold
et de cette annotation avant de figer leurs réponses.

## Vérifications réalisées

Vérification structurelle locale, sans importer ni exécuter de garde de
compréhension : JSON strict sans NaN, IDs uniques et concordants entre fichiers,
16 groupes de deux, comptages 10/6 par famille, champs publics autorisés, schémas
des données et validité des données des 20 cas supportés. Cette vérification
n'est pas une mesure de performance d'agent. Les ambiguïtés et variantes sont
annotées manuellement; aucune performance ni solution numérique n'est produite.

SHA-256 des fichiers figés :

| Fichier | SHA-256 |
|---|---|
| `public_cases.json` | `11c3c5b17fe8f3c0c9023c4fd8adb829dc8da739b0a4be4001213f6bdce1d0ae` |
| `private_gold.json` | `ca4315838310f93441101f160273385545758d5438bb373f84c1b84825eafd71` |

Prochaine étape : figer ces hashes dans le protocole d'évaluation, transmettre
uniquement les entrées publiques aux vrais agents, puis faire contrôler leurs
réponses par un vérificateur distinct de l'auteur des réponses. Une adaptation
ultérieure sur ces cas rendrait ce corpus impropre à une revendication de test
aveugle inédit.
