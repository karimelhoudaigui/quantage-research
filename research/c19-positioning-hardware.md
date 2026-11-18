# C19 — positionnement et limites matérielles, contrôle du 15 novembre 2026

C19 est une étude de formulation et de réparation d'ILP binaires avec oracle
fini annoté et solveurs classiques. Son protocole ne construit aucun encodage
atomique ou optique. Les expériences SDK historiques restent distinctes : leur
validation locale ne vaut ni réalisation des ILP complètes de C19 ni accès QPU.
Aucun résultat de génération C19 n'a été consulté pour cette fiche.

Le contrôle reprend les fiches `c15-method-positioning`, `c11-hardware-plan`,
`c11-hardware-sources` et l'index des sources, puis relit les passages ci-dessous.
Cinq sources primaires seulement servent de preuves dans cette passe.

## Frontières françaises utiles à l'article

**Pasqal/Pulser.** Le manuel **Pulser 1.8.0**, *Hardware specifications*, distingue
explicitement `Device` et QPU/backend. Il détaille géométrie du registre, canaux
et bornes des pulses ; `requires_layout` et `accepts_new_layouts` comportent des
contrôles propres à l'exécution QPU. `AnalogDevice` est un exemple versionné,
pas une machine réservée au compte. [Passages relus : The Device, spécifications,
canaux, AnalogDevice](https://docs.pasqal.com/pulser/v1.8.0/hardware/).

Application à C19 : fidélité d'une ILP, transformation éventuelle en QUBO et
admissibilité physique sont trois obligations différentes. C19 n'apporte pas
le registre, l'encodage complet des clauses, les pulses et le backend précis
nécessaires à cette dernière étape. Il faut écrire « compatibilité physique
non établie », sans conclure à une impossibilité générale sur Pasqal.

**Quandela/Perceval.** La documentation **Perceval v1.3**, *Computer*, sépare
explicitement `SimulatedComputer`, exécuté localement avec un backend de
simulation, et `RemoteComputer`, qui utilise une `CommunicationLayer` vers un
QPU **ou** un simulateur distant. Le caractère distant ne prouve donc pas une
exécution physique. [Passages relus : introduction, SimulatedComputer,
RemoteComputer](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html).

Application à C19 : les contrôles photoniques locaux antérieurs ne fournissent
ni compilation des ILP vers un circuit, ni admissibilité pour une plateforme
Quandela identifiée. Les deux solveurs classiques de C19 ne deviennent pas
quantiques par rattachement au fournisseur.

Ces pages ont été revérifiées à la date du contrôle dans leurs versions citées.
Elles ne sont pas déclarées être les dernières versions disponibles, ni les
spécifications actuelles d'une machine accessible. Aucun catalogue, compte,
file d'attente, droit d'accès ou bruit réel n'a été vérifié. Les contraintes
locales de politique interdisent toujours soumission QPU et dépense externe.

## Antériorité méthodologique limitée

**CEGIS.** Solar-Lezama et al., *Combinatorial Sketching for Finite Programs*,
ASPLOS **2006**, copie auteur : §5.2 équation (5.1), PDF p.7, et texte de §5.4,
PDF p.9, relus. Le synthétiseur accumule les contre-exemples du validateur.
Sa recherche finie suppose que les candidats respectent les observations
accumulées. [Source primaire](https://people.csail.mit.edu/asolar/papers/Solar-LezamaTBSS06.pdf).
C19 reprend cette idée avec un générateur LLM et un nombre borné de réparations ;
la complétude et la progression de la synthèse classique ne lui sont pas acquises.

**Self-Refine.** Madaan et al., version publiée **NeurIPS 2023**, §2, algorithme 1
et équations (2)–(4), PDF pp.3–4, relus : le même LLM produit un feedback explicite
puis raffine avec historique. [Source primaire](https://proceedings.neurips.cc/paper_files/paper/2023/file/91edff07232fb1b55a505a9e9f6c0ff3-Paper-Conference.pdf).
Le bras auto de C19 reçoit une consigne générique de révision ; il n'est pas
une reproduction de ce protocole à étape FEEDBACK distincte.

**Opt-Verifier.** Liu et al., **arXiv:2605.29556v1, 28 mai 2026**, §4.2–4.4 relus :
interprétation de structure et de solution, commentaires des agents de
vérification, puis révision du modèle. La réparation guidée de formulations
d'optimisation a donc un précédent directement pertinent.
[Source primaire versionnée](https://arxiv.org/html/2605.29556v1).
C19 utilise plutôt des contre-exemples exacts sur un petit domaine et une
référence annotée supposée correcte. Ce changement de contrat n'établit pas
une nouveauté ou une supériorité ; aucun taux de l'article n'est repris.

OptiMUS reste un voisin déjà consigné dans `research/sources/index.json` et les
fiches C11. Il n'a pas été relu dans cette passe et ne constitue pas une sixième
source de preuve ici. La version publiée finale d'Opt-Verifier n'a pas été
inspectée ; la présente extraction porte exclusivement sur l'arXiv indiqué.

## Formulation recommandée pour calibrer l'article

« Nous étudions une réparation bornée inspirée de CEGIS, guidée par un oracle
exhaustif relatif à des annotations séparées. Les formulations produites sont
résolues par des solveurs classiques. Les résultats ne certifient ni le sens
arbitraire d'un texte libre, ni une compilation ou une exécution sur les QPU
français ; la nouveauté générale de la méthode n'est pas établie. »

Cette proposition décrit le dispositif, pas un résultat positif. Le contrôle
est ciblé, sans recherche globale de nouveauté, reproduction de logiciel externe
ou évaluation comparative des méthodes citées. Les versions, passages et
obligations encore non vérifiées sont détaillés dans le JSON compagnon.
L'auteur de cette fiche est aussi l'auteur du corpus C19 ; ce travail documentaire
ne constitue pas une nouvelle revue aveugle des annotations ou des résultats.
