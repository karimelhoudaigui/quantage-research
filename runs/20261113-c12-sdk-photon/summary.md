# C12 terminé — passage à la photonique multiphotonique simulée

Exécuté réellement : Perceval1.3.1 local, 486 évaluations de circuits3modes/2photons idéaux et 2916 probabilités confrontées à un oracle bosonique séparé. Erreur maximale 2.22e-16, seuil1e-10; HOM et collisions d'entrée concordent. H12 soutenue uniquement sur cette grille finie.

SDK : cinq sondes refusées, trois photons acceptés légitimement hors contrat; notre frontière refuse huit variantes et conserve son contrôle. Les erreurs SDK et les acceptations sont enregistrées. Pas de validation de machine Quandela, performance LLM, nouveauté ou QPU. Auto-revue mathématique distincte d'implémentation, revue d'auteur indépendante encore requise.

Preuves : protocol.md, contract-mathbox.json, environment.json, results/raw.jsonl, metrics.json et manifest.json. Trois tests analytiques passent. Temps mur39.61s, achat0; CPU principal ne compte pas les sous-processus.

Article : l'intégrateur peut remplacer la limite historique «aucun SDK» par ce résultat logiciel précis et ajouter la difficulté multiphotonique, sans annoncer une compatibilité QPU. Prochaine expérience : programme Pulser2atomes avec Hamiltonien indépendant et sondes de contraintes; ensuite étude d'agents sur familles hors développement, si annotations et budget le permettent.
