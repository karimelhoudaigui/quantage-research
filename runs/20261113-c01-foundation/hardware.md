# Capacités et accès — 2026-11-13

Sources primaires réellement consultées; versions documentaires figées,
pas de relevé de compte ni de spécifications obtenues d'un backend.

| Fournisseur | Documenté | Annoncé / exemple | Accessible dans cette session |
|---|---|---|---|
| Pasqal | Atomes neutres Rydberg, interactions dépendant de la distance, validation Device/Channel et backend distinct | L'exemple AnalogDevice de Pulser 1.8.0 donne 80 atomes, l'exemple FRESNEL_CAN1 du tutoriel en donne 100; ces nombres ne sont pas interchangeables | Aucun Device de compte interrogé, SDK absent, aucun QPU autorisé |
| Quandela | Photonique linéaire; composants, simulation et calcul distant distincts; contraintes/commandes propres aux plateformes | Exemples de plateformes, sans garantie de droits utilisateur | Aucun compte interrogé, SDK absent, aucun QPU autorisé |

Pasqal : https://docs.pasqal.com/pulser/v1.8.0/hardware/ (§Device,
Channels, AnalogDevice); https://docs.pasqal.com/pulser/v1.8.0/register/
(Rydberg-Atom Interactions);
https://docs.pasqal.com/pulser/v1.8.0/tutorials/qpu/ (§1).
La géométrie, les couplages résiduels, les contraintes laser, les layouts et
les contrôles disponibles doivent être validés. Une QUBO pondérée abstraite
ne constitue pas un programme Rydberg réalisable.

Quandela : https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html
(Computer, SimulatedComputer, RemoteComputer);
https://perceval.quandela.net/docs/v1.0/reference/runtime/remote_processor.html
(document historique 1.0 pour commandes/contraintes, sans supposer son API
actuelle). Le calcul exact de probabilités par un simulateur ne devient pas
une acquisition de probabilités exactes par QPU; un QPU fournit des mesures.

Identité : page officielle Pasqal «About us», siège France
(https://www.pasqal.com/about-us/); mentions légales Quandela, SAS à Massy
(https://www.quandela.com/legal-terms/), consultées. Fournisseur français ne
prouve pas qu'un job serait exécuté en France : localisation des machines
utilisées ici = sans objet; aucun job distant. Le siège n'est pas un datacenter.

Localement : calcul classique exact pour MIS et calcul flottant idéal pour
photonique. Aucun émulateur calibré de bruit. SpinPulse non utilisé; aucune
assimilation au bruit de Pasqal. Aucun autre fournisseur ajouté.
