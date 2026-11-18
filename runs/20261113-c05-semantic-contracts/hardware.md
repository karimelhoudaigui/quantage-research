# C05 — Contrat minimal d'une recommandation matérielle

Date de vérification : 2026-11-13. Rôle matériel, distinct de l'auteur du moteur.
Portée : préciser les informations exigibles d'un agent; aucune validation SDK,
aucun compte ni secret consulté, aucun job distant, aucune dépense. Les identités
françaises déjà documentées en C01 sont réutilisées sans nouvelle conclusion sur
la localisation d'une machine. Ce rapport ne remplace pas une validation physique.

## États à ne pas confondre

| État | Critère | Conclusion autorisée |
|---|---|---|
| Piste documentaire | Famille et modalité plausibles, documentation citée | Fournisseur à examiner; pas de compatibilité de l'instance |
| Encodage absent | Géométrie, circuit, contrôles ou correspondance non fournis | Abstention sur la compatibilité; pas de preuve d'impossibilité |
| Candidat d'instance conditionnel | Encodage explicite et hypothèses/tolérances identifiées | Étudier cet encodage; les contrôles non exécutés restent ouverts |
| Incompatibilité démontrée | Violation précise d'un modèle ou d'une spécification identifiée | Rejet de cet encodage sur ce modèle/dispositif; pas de toute solution possible |
| Accès inconnu | Aucun droit de compte ou backend vérifié | Aucun accès affirmé, même si l'encodage est plausible |

Ces états sont des propositions de contrat QuantAge, pas une taxonomie publiée
par les fournisseurs. `candidate` ne doit jamais signifier «réalisable» sans
préciser lequel des deux premiers niveaux de recommandation est visé.

## MIS pondéré → candidat Pasqal

Pour dépasser la piste documentaire, demander :

1. L'instance canonique : sommets, arêtes non orientées, poids, domaine binaire,
   objectif, contraintes et convention de comptage des termes quadratiques.
2. L'encodage choisi : un atome par variable ou gadgets/ancillas avec décodage;
   coordonnées et unités; échelle d'énergie, termes linéaires et couplages visés;
   couplages réels pour **toutes** les paires, y compris les non-arêtes;
   erreur admissible et justification de préservation des solutions.
3. Le dispositif modèle identifié/versionné, ses états et canaux supposés;
   traitement des poids non uniformes, durée et unités des commandes; contrôles
   disponibles ou hypothétiques explicitement séparés.
4. Une procédure de préparation, mesure en bitstrings, décodage et contrôle
   classique de faisabilité/qualité, sans garantie infondée d'optimum.
5. Un tableau des obligations restantes : contraintes de registre/layout,
   amplitude, désaccord, durée, calibration et accès. Aucune de ces cases ne
   devient validée parce qu'un petit problème classique a été résolu.

Fondement : [Pulser, Programming a neutral-atom QPU, version affichée 1.10.0](https://pulser.readthedocs.io/en/stable/programming.html),
§2.1–2.2 et Pick a Device, texte consulté. L'interaction Rydberg directe dépend
des distances; les canaux déterminent les commandes possibles. **Inférence
QuantAge** : une matrice QUBO abstraite ne fournit pas cet encodage. À distance
finie et coefficient non nul, prétendre réaliser exactement des couplages nuls
de non-arêtes par ce seul terme direct est incompatible avec ce modèle; une
approximation, un gadget ou une autre méthode doit être déclaré et évalué.

Précision sur les poids : le [tutoriel officiel MWIS, Pulser 1.7.2](https://docs.pasqal.com/pulser/v1.7.2/tutorials/mwis/),
§Solving the MWIS, Pick a Device, Create the Register et Pick the channels,
effectivement consultés, utilise un canal Rydberg global et un DMM pour la
construction présentée. Son exemple choisit `MockDevice`, dispositif virtuel;
son optimisation de positions est décrite comme heuristique. Cette construction
ne prouve ni encodage universel ni disponibilité du DMM sur un QPU de compte.
Le rapport ne reprend pas les identités algébriques du tutoriel comme preuve
de notre pénalité. Sans encodage de poids annoncé, statut = encodage absent;
si une construction exige un canal absent d'un dispositif identifié, rejet de
cette construction sur ce dispositif seulement.

L'[exécution QPU, Pulser 1.7.2](https://docs.pasqal.com/pulser/v1.7.2/tutorials/qpu/),
§1 et §3.1, consultés, demande une connexion compatible, un Device obtenu du
backend et les layouts admissibles. Elle produit un bitstring par run. Ces
obligations restent non exécutées ici; aucun nombre d'atomes d'un exemple n'est
traité comme une capacité accessible à ce compte.

## Un photon → candidat Quandela

Pour dépasser la piste documentaire, demander :

1. Le nombre de modes et la distribution d'entrée Fock, ici `[1,0]`; les degrés
   de liberté retenus et les hypothèses source, pertes et détection.
2. La liste ordonnée des composants avec modes, angles, unités et convention
   de matrice; la correspondance avec les composants Perceval. Pour le moteur
   actuel, `R(a)` correspond à `BS.Ry(theta=2*a)` et la phase agit sur le mode 1;
   l'ordre est `R(b) P(phi) R(a)`.
3. L'observable demandée : probabilités idéales locales, ou fréquences de
   comptage avec shots, filtre/post-sélection et incertitude définis. Une
   estimation expérimentale ne doit pas être étiquetée probabilité idéale exacte.
4. Une plateforme cible identifiée ou un champ explicitement inconnu; sa modalité
   simulateur/QPU, ses contraintes modes/photons/détecteurs et les validations
   nécessaires; accès et localisation traités séparément.

La [documentation Unitary Components, Perceval 1.3](https://perceval.quandela.net/docs/v1.3/reference/components/unitary_components.html),
§Beam Splitter conventions, reflectivity et Phase Shifter, consultés, donne les
conventions `Rx`, `Ry`, `H` et leurs paramètres. La traduction ci-dessus est une
comparaison directe de matrices, pas un essai SDK. Une convention oubliée est
une obligation manquante; un composant revendiqué avec une matrice contraire à
la convention spécifiée est une incompatibilité démontrée de cette traduction.

[Computer, Perceval 1.3](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html),
§Computer, SimulatedComputer, RemoteComputer, available_commands, specs et
estimate_required_shots, consultés, distingue acquisition locale/distante et
QPU/simulateur; le distant dépend d'une couche de communication et les ressources
dépendent du circuit et des filtres. Aucun objet distant n'a été créé ici.
Deux photons ne constituent pas une incompatibilité générale Quandela : c'est
une sortie du périmètre du solveur local QuantAge à un photon.

## Limite constatée de `quantage/routing.py`

Inspection du fichier et deux appels locaux réalisés avec Python 3.9.6. Hash
SHA-256 inspecté :
`ffb64bc9e517f5ba4e01e9e60b07d57ed75c6f6192716e44d543aab86cb902c1`.

Le niveau `guarded` contrôle triplet solveur/famille/fournisseur et portée du
claim. Il n'exige pas les champs d'encodage ci-dessus. Appelé directement avec
`problem={'family':'mis'}` et la proposition
`{'solver':'pasqal_analog','provider':'Pasqal','execution_kind':'candidate','claim':'conditional_candidate'}`,
il renvoie `acceptable_recommendation=true`, `reasons=[]`. Le même résultat est
observé pour `problem={'family':'photon','photons':2}` avec `quandela_linear` et
`Quandela`. Dans les deux cas : `execution_permission='not_authorized'`,
`hardware_readiness='unverified'`, `qpu_submission_implemented=false`.

Commande de reproduction des deux appels :

```python
import json
from pathlib import Path
from quantage.routing import review_route
policy = json.loads(Path('config/policy.json').read_text())
for problem, solver, provider in [
    ({'family': 'mis'}, 'pasqal_analog', 'Pasqal'),
    ({'family': 'photon', 'photons': 2}, 'quandela_linear', 'Quandela')]:
    print(review_route(problem, {
        'solver': solver, 'provider': provider,
        'execution_kind': 'candidate', 'claim': 'conditional_candidate'
    }, policy))
```

Cela établit l'absence de validation d'instance dans cette fonction, pas une
violation de permission ni une impossibilité physique. `core.understand` est
plus strict, mais cette précondition n'est pas imposée par `review_route`.
Le garde-fou doit donc annoncer «piste documentaire» ou recevoir un contrat
d'instance vérifié en amont avant d'affirmer davantage. Aucun code modifié.

## Prochaine action

Introduire dans le protocole sémantique des cas distincts : encodage manquant,
violation d'une spécification identifiée, accès inconnu et candidat conditionnel
documenté. Les étiqueter séparément pour éviter qu'une prudence de permissions
masque une recommandation scientifique insuffisamment étayée. Les résultats C03
restent des décisions sur corpus fini; ce complément ne les transforme pas en
validation matérielle.
