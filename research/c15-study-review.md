# C15 — revue indépendante du scorer et du feedback, prototype v1

Statut : revue du prototype v1 terminée ; **ne vaut pas revue des futurs
drivers/frontend v2**. L'intégrateur annonce une révision de représentation
après développement et avant toute génération réservée. À son instruction,
toute nouvelle exécution d'audit est suspendue jusqu'au gel `FROZEN`.
Les preuves v3 du cœur, du helper et des solveurs restent inchangées.

## Portée et provenance

Lu : `quantage/repair_study.py` dans sa version soumise, avec les modules
déjà audités. Aucun gold auteur, générateur de corpus ou provenance privée
de corpus ouvert ; aucune réponse LLM de test lue ou générée. Le présent
rapport n'évalue pas la qualité scientifique de générations de développement.

La source exacte du scorer au moment du calcul est identifiée par son
SHA-256 dans `research/c15-study-audit/manifest.json`. Le script indépendant
est `research/c15-study-audit.py`, contrat
`research/c15-study-audit.contract.json`. Le manifest v2 a le statut
`completed` et a été validé avec la racine à l'exécution. Un changement
ultérieur du prototype doit être conservé comme changement de source, sans
modifier ce manifest ni lui attribuer la nouvelle version.

## Sélection et métriques relues

La sélection directe reçoit uniquement les deux propositions et choisit par
validité de schéma, moyenne de log-probabilité après processeurs, puis première
proposition en cas d'égalité. Elle ne consulte aucun label, certificat,
optimum ou solveur. Auto et guidée partagent exactement la règle de révision :
seconde proposition valide, sinon première valide, sinon seconde invalide.
Une correction valide peut donc régresser ; le scorer la conserve et mesure
cette régression au lieu de choisir par le gold.

Le certificat strict et les diagnostics d'optima restent séparés. Le nombre
de réparations est décomposé selon que la première proposition échouait au
schéma ou à la sémantique finie. Les régressions ont pour dénominateur les
cas initialement fidèles ; le compteur d'erreurs initiales est conservé.
H15 applique exactement le critère conjoint préenregistré : guidée moins
auto au moins trois formulations fidèles, et au plus une régression guidée.
Le mode développement initial seul donne `development_only`.

Les strates sont langue et faisabilité de la référence. Lorsque la première
proposition échoue au schéma, le scorer énumère quand même la référence pour
connaître sa strate : une sortie invalide ne transforme pas un problème
infaisable en problème faisable. Les sommes des strates doivent redonner
chaque total. Les erreurs de schéma ont zéro affectation comparée ; leurs
désaccords numériques ne sont pas des zéros de justesse et ne doivent pas
être interprétés ainsi.

Tout modèle final au schéma valide est passé au portfolio, même si son
certificat sémantique échoue. Les solveurs n'ont accès qu'au modèle candidat.
Le marqueur `usable_for_original_problem` exige ensuite fidélité et
concordance. Il inclut une déclaration d'infaisabilité correcte ; il ne
promet pas une solution quand le domaine est vide. Le portfolio mesure les
deux solveurs et choisit après leurs exécutions, ce qui ne constitue pas un
routeur accélérant une requête future. Un même candidat initial choisi par
plusieurs bras peut être profilé plusieurs fois ; ces exécutions restent
des coûts physiques réels, pas des observations indépendantes de performance.

## Feedback exposé et rapports privés

Le producteur calcule le rapport complet, puis n'écrit dans `minimal.json`
que `feedback_for_model(report,n)`, validé par le helper. Les erreurs de
schéma y sont des messages constants ; les autres retours sont des témoins
bornés ou un message de succès constant. Les comptes détaillés, le temps de
vérification et les rapports complets vont dans `reports.jsonl`, distinct.
Le driver guidé doit recevoir uniquement le chemin `minimal.json` ; les
arguments réels et les messages enregistrés seront contrôlés après run.

## Contrôles exécutés — fixtures synthétiques, aucune performance LLM

Quatre cas artificiels de deux variables et seize enregistrements artificiels
ont été créés par le script d'audit, sous le nom
`synthetic-fixtures`. Ils ne proviennent d'aucun modèle. Les valeurs de temps
et de tokens y sont choisies pour tester la comptabilité et ne décrivent
aucun coût d'inférence réel.

Les attentes ont été fixées à la main avant l'appel du scorer : priorité de
validité, priorité de score, égalité directe, fallback commun, réparation de
format, réparation mathématique, régression guidée, domaine infaisable,
objectif proportionnel distingué de la fidélité, et mode initial seul.
Les métriques obtenues, les sommes des strates et les messages minimaux
correspondent à ces attentes. Les solveurs ont réellement été appelés sur
les petits modèles artificiels ; leurs temps ne sont pas utilisés comme
performance scientifique.

Le résultat est dans `research/c15-study-audit/raw.json`, explicitement marqué
`SYNTHETIC SOFTWARE FIXTURES; NO LLM PERFORMANCE`. Les sorties du scorer et du
feedback sont hashées séparément par le manifest. Python 3.9.6, SciPy 1.13.1,
NumPy 1.26.4, limite 30 s, thread conventionnel 1. Commande enfant conservée :

```bash
python3 research/c15-study-audit.py --output research/c15-study-audit
```

Le contrat, tous les modules importés et la commande du runner sont dans le
manifest. Les répertoires existants ne doivent pas être réutilisés pour un
replay.

## Coûts et limites de validation à traiter au gel v2

Le nombre physique de générations vaut une initiale partagée plus trois
secondes, soit quatre appels par cas. Chaque bras déployé se voit attribuer
deux appels, initiale plus sa seconde ; additionner les trois coûts attribués
compterait volontairement l'initiale plusieurs fois. Le scorer respecte
cette distinction.

`physical_generation_cost` additionne les compteurs de lignes. Pour les
temps, cela exclut le chargement du modèle, les intervalles entre requêtes,
la création du feedback et le score/portfolio. Ces coûts sont accessibles
dans d'autres bruts/manifestes, et ne doivent pas disparaître d'une
comptabilité complète. Les champs de ce prototype décrivent donc le temps
des requêtes, pas le coût total de session ou de workflow.

Le prototype vérifie une matrice unique complète et la correspondance entre
réponse brute et parse sauvegardée. Il ne contrôle pas encore dans `indexed`
la phase attendue, les plafonds de tokens, les IDs/log-probabilités et leur
moyenne ; les entrées réelles doivent être auditées avant d'affirmer le
respect des budgets. Le chargement du gold ne rejette pas explicitement les
doublons d'ID et le score utilise `families` sans le déclarer dans sa
validation de schéma ; ce champ n'influence ici ni sélection ni strates.

Le parseur v1 admet une unique clôture Markdown facultative, retirée avant
JSON. Cette normalisation syntaxique doit être annoncée comme telle dans le
protocole, et les sorties enveloppées ne doivent pas être appelées « JSON
brut conforme ». Elle ne complète aucune clause ou coefficient. La nouvelle
représentation algébrique v2 devra décrire séparément sa normalisation.

Verdict limité : sélecteurs, feedback et comptabilité du prototype v1
conformes dans les contrôles finis effectués. Aucun résultat H15 ni avantage
de réparation établi. Revue statique du frontend/scorer v2 puis exécution
d'audit uniquement après annonce de son gel ; audit des bruts réels à suivre.
