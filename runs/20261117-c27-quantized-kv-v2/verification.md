# Vérification C27

## Méthode

La génération a été vérifiée par un chemin distinct du driver : reprise des enregistrements initiaux C19, du patch C22, de l'état gelé C24 et du patch C27; comparaison de la matérialisation littérale et des empreintes de lignée; puis énumération exacte du cube binaire contre l'annotation de référence. Aucun modèle, réseau ou corpus C23 n'est lu par la commande d'audit.

Commande :

```text
python scripts/audit_c27.py
```

Environnement : Python 3.11.15, macOS 26.2 arm64, SciPy 1.17.1. Les hashes des données, manifestes, journaux d'exécution et sources sont dans `verification.json`.

## Résultat mathématique fini

Le C19 initial et l'état C24/C22 avant le second patch ne sont pas fidèles : 1 désaccord de faisabilité parmi 16 affectations, témoin `[1,1,0,0]`; zéro désaccord d'objectif. Le patch C27 est rejoué littéralement et le modèle final est fidèle sur les 16 affectations : zéro désaccord de faisabilité et d'objectif. Les nombres de solutions faisables sont deux pour la référence et pour le candidat final.

La portée est strictement le cube de cette instance annotée. Cela ne certifie pas la compréhension générale du texte ou la correction d'une famille entière de problèmes.

## Intégrité de la lignée

Les empreintes de l'initial C19 et du patch C22 correspondent aux hashes conservés dans le gel C24; l'état sérialisé C24 est égal à la matérialisation rejouée du premier patch. Le patch C27 est ensuite parsé contre cet état exact et son modèle matérialisé égale celui enregistré par le driver. Il n'y a pas de nouvel initial ni de retry.

## Limites de revue

L'audit mathématique a été exécuté indépendamment du chemin de génération, mais par le même intégrateur; ce n'est pas une revue humaine ou agent distincte. La revue statique C26/C27 précédente couvrait fixtures et code, pas ce résultat réel ni la mémoire réelle. Les tests synthétiques ne sont pas une preuve matérielle.
