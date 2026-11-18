# Carte des opportunités — première campagne, 2026-11-13

Jugements de priorité de l'intégrateur, pas mesures de nouveauté. Les axes
non sélectionnés restent proposés; leur littérature spécialisée reste à revoir.
Question centrale unique : fidélité du contrat puis admissibilité du solveur.

| Axe | Question agentique testable | Nouveauté potentielle | Vérifiabilité locale | Coût initial | Faisabilité française | Généralisation attendue à tester |
|---|---|---|---|---|---|---|
| Optimisation | Préserver contraintes et tous les optima après pénalisation | À établir, formulation classique connue | Très forte sur petits graphes | Faible, exhaustif | Pasqal candidat, géométrie/contrôles manquants | Poids, tailles, contraintes |
| Photonique | Préserver observable, cohérence et convention de composant | À établir | Très forte à un photon | Faible, analytique | Quandela candidat, accès non vérifié | Photons multiples, pertes, mesures |
| Plusieurs corps | Traduire observables et Hamiltonien Rydberg | À établir | Diagonalisation petite taille possible | Modéré | Pasqal plausible, séquences à valider | Dynamique et unités |
| Chimie | Maintenir secteur de particules, mapping et énergie | À établir | Petite matrice possible, oracle à construire | Modéré | Encodage et ressources non établis | Symétries et mesures |
| Apprentissage quantique | Choisir noyau, budget et baseline classique | À établir | Protocole de données nécessaire | Modéré | Aucun circuit validé | Distribution des données |
| Algèbre linéaire / EDO | Expliciter chargement, conditionnement et sortie | À établir | Forte sur petits systèmes | Modéré | Aucun algorithme matériel validé | Erreur et coût de lecture |
| Contrôle des erreurs | Distinguer mitigation, estimation et correction | À établir | Bruit/contrôles à définir | Modéré à élevé | Aucune calibration accessible | Changement de bruit |
| Apprentissage des agents | Mesurer détection, abstention et portée des certificats | À établir; voisin de NL4Opt/OptiMUS | Forte avec oracles finis | Faible sans LLM, accès requis ensuite | Transversal | Familles, langage, taille |

Choix : MIS pondéré + interférométrie idéale. Leurs oracles ont des mécanismes
d'échec différents (contraintes combinatoires contre interférence), et le même
format peut porter proposition, certificat et abstention. Cela justifie le
coût local, pas une généralisation démontrée. Sources ciblées et périmètre
de lecture : runs/20261113-c01-foundation/literature.md et hardware.md.
