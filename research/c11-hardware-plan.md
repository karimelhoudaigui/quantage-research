# Faisabilité matérielle et plan SDK — vérification documentaire C11

Sources primaires consultées le13novembre2026; détails dans c11-hardware-sources.json. Ce rapport prépare C12 et ne constitue pas un résultat de simulation.

Le Python par défaut3.9.6 ne convient pas aux SDK actuels. [PyPI Pulser](https://pypi.org/project/pulser/) donne1.10.0(29octobre2026), Python>=3.11; [Perceval-Quandela](https://pypi.org/project/perceval-quandela/) donne1.3.1(1octobre2026), Python>=3.10,<3.15. Un Python3.11.15 existe déjà dans /opt/homebrew/bin/python3.11; sa métadonnée locale montre Pulser1.7.2 et QuTiP5.2.3 déjà installés. Aucun SDK n'a été exécuté pour cet inventaire. Le venv LLM3.9 doit rester séparé. Les docs Pulser versionnées1.10 n'ont pas été accessibles; ne pas confondre métadonnée de release actuelle et API1.9.1 consultée.

## Quatre niveaux à conserver séparés

1. Formulation mathématique : équivalence/probabilités sous hypothèses déclarées.
2. Programme accepté par un SDK donné : validation des objets et exécution locale observée.
3. Respect d'une spécification : contraintes d'un Device et d'un backend identifiés, y compris celles non contrôlées automatiquement.
4. Exécution physique : aucun run QPU autorisé ou effectué.

Un simulateur local n'établit ni accès de compte ni emplacement d'exécution physique. Le fournisseur français et la nationalité de l'hébergement sont deux propriétés différentes.

## Pasqal : contrôles pertinents

Les [spécifications1.8.0](https://docs.pasqal.com/pulser/v1.8.0/hardware/) documentent pour AnalogDevice un registre2D, au plus80atomes, distance minimale5µm, rayon38µm, canal Rydberg global, amplitude maximale4πrad/µs, horloge4ns, durée minimale16ns et séquence6000ns. Ce sont des exemples versionnés, pas des droits d'accès. Lire le Device installé avant toute expérience. L'interaction C6/r^6 contraint les coefficients; aucune réalisation d'une QUBO arbitraire n'en découle.

La [validation de Sequence1.9.1](https://docs.pasqal.com/pulser/v1.9.1/sequence/) rejette une géométrie trop serrée et contrôle les ajouts; certaines contraintes backend ne sont activées qu'avec mimic_qpu. with_new_device peut modifier la séquence sauf strict=True. Une séquence valide ne constitue donc pas à elle seule un certificat d'exécution QPU.

Les [conventions](https://docs.pasqal.com/pulser/v1.9.1/conventions/) imposent en ground-rydberg |r>=(1,0), |g>=(0,1), et r->bit1. L'ordre des atomes et les conversions ns/µs sont centraux pour un oracle indépendant. Les versions>=1.9 déprécient QutipEmulator.run; préférer QutipBackendV2 pour une nouvelle version, mais utiliser la documentation exacte1.7.2 si l'installation existante est retenue. Pas de modèle de bruit réel validé; SpinPulse n'est pas assimilé au bruit Pasqal.

## Quandela : extension C12 prioritaire

Question : la distribution complète de circuits3modes/2photons d'un Perceval réellement exécuté concorde-t-elle avec une expansion bosonique indépendante, et quels défauts sont ou non refusés par le SDK?

Les [composants1.3](https://perceval.quandela.net/docs/v1.3/reference/components/unitary_components.html) fixent Ry(theta=2a)=R(a), PS(phi)=exp(iφ); le défautRx a d'autres phases. [SLOSBackend](https://perceval.quandela.net/docs/v1.3/reference/backends/slos.html) accepte un état de Fock sans annotations et calcule les distributions. Le nomSLOS désigne désormais une implémentationC++; instancier explicitement SLOSBackend et enregistrer la classe/version réelles. Les couches [Computer](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html) séparent simulation et remote; C12 emploiera seulement le backend local direct.

Contrat recommandé : photons indistinguables idéaux, aucune perte, aucun bruit, détecteurs résolvant le nombre, angles radians, toutes les six occupations à2photons sur3modes. Circuit composé de rotations voisines et d'une phase intermédiaire. Inclure HOM équilibré, identités, collisions en entrée et grilles d'angles; réutiliser uniquement les idées physiques, aucune donnée C01–C10 comme test indépendant.

Oracle : appliquer successivement les opérateurs de création transformés, avec facteurs sqrt(n+1) et normalisation sqrt(prod(t_j!)), à une matrice construite séparément par trigonométrie. Ne pas appeler un permanent du SDK. Contrôles : distribution entière, somme1, erreurs absolues, unité de U, conservation du nombre. La [formule de Fock](https://arxiv.org/html/2204.00602) du papier Perceval§4.2.1eq7 fournit une vérification documentaire de la normalisation, sans rendre le calcul nouveau.

Négatifs à préenregistrer selon API : indice de composant hors modes, entrée de taille incompatible, occupation négative, photon supplémentaire, nonunitaire. Un photon supplémentaire peut être une entrée SDK parfaitement valide; il doit être refusé par le contrat expérimental plutôt que faussement présenté comme échec SDK. Un composant de perte est aussi une fonctionnalité légitime hors du contrat idéal, pas nécessairement une erreur SDK. Conserver messages d'exception et corrections automatiques éventuelles; ne pas masquer les acceptations.

C12 peut démontrer une compatibilité logicielle idéale observée et le passage à une difficulté multiphotonique. Il ne mesure pas à lui seul une généralisation agentique ni une conformité à un QPU Quandela spécifique. Les limites du nombre de modes/photons, sources, pertes, détecteurs et compilation de plateforme restent inconnues sans spécification machine vérifiée.

## Option ultérieure Pasqal

Après priorité photonique, une séquence de deux atomes avec pulse constant et interaction finie offre un Hamiltonien4×4 diagonalizable indépendamment et un test de géométrie min-distance, canaux et amplitude. Préenregistrer avant exécution, enregistrer la version installée et comparer probabilities plutôt que samples. Ce serait une autre famille de dynamique, sans optimisation QPU, sans approximation de blockade parfait proclamée exacte.

Aucune installation, soumission ou dépense n'a été faite pour ce rapport. L'exécution C12 autorisée par l'intégrateur sera enregistrée dans son propre protocole/manifeste; les résultats seront distincts du présent plan.
