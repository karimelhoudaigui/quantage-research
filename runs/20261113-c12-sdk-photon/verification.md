# Vérification C12 — simulation idéale Perceval réelle

Résultat : implémentation exécutée et assertion finie reproduite, sous tolérance flottante; auto-revue, auditeur distinct encore requis.

Le manifest v2 results/manifest.json est completed et son validateur avec --root . passe. La grille préenregistrée contient exactement 486 évaluations, 81 configurations de paramètres, six occupations d'entrée et six sorties par évaluation, soit 2916 probabilités comparées. Ce sont des cas déterministes, sans intervalle de population ni observations indépendantes revendiquées.

Erreur absolue maximale de probabilité : 2.2204460492503131e-16; matrice : 1.1102230246251565e-16; normalisation : 4.4408920985006262e-16, toutes sous le seuil préenregistré 1e-10. L'oracle construit les matrices trigonométriques et propage les opérateurs de création, sans appeler Perceval ou son permanent. Le simulateur observé est perceval.backends._slos.SLOSBackend, version Perceval 1.3.1, exqalibur 1.4.2, Python 3.11.15. Le backend a été exécuté réellement; il ne s'agit pas d'une simulation inventée ou d'un mock logiciel.

Hong–Ou–Mandel donne SDK P(2,0,0)=P(0,2,0)=0.5, P(1,1,0)=0. Les trois tests analytiques sans SDK vérifient bunching, normalisation de l'entrée en collision et influence d'une phase recombinée. Une phase placée sans recombinaison aurait été peu discriminante; le troisième beam splitter assure cette sensibilité.

Les six sondes SDK sont conservées sans présumer leurs issues : indice de composant hors modes rejeté; longueur d'entrée incorrecte rejetée; occupation négative rejetée; matrice nonunitaire rejetée; trois photons acceptés avec probabilité totale 1; canal de perte rejeté dans Circuit, avec conseil d'utiliser Experiment. L'acceptation de trois photons est une capacité légitime du SDK, hors du contrat de cette expérience. Le rejet d'une perte dans Circuit ne signifie pas que tout Perceval ou tout QPU serait sans pertes.

Notre frontière explicite accepte le contrôle valide et refuse huit variantes hors portée (dimension, signe d'occupation, nombre de photons, perte, bruit, booléen, NaN et observable à seuil). Ces neuf sondes ne prouvent pas une validation exhaustive du schéma. L'inspection des sources SDK installées montre des assert pour plusieurs gardes; Python optimisation=0 dans ce run. Aucune garantie sur un lancement python -O n'est déduite.

Temps mur mesuré dans le programme : 39.607213 s, y compris imports et six sous-processus. Temps CPU du processus principal : 1.661093 s, excluant le CPU des sondes enfants; ne pas le présenter comme CPU total. Installation et octets réseau totaux non instrumentés. Versions complètes requirements-quantum-sdk.txt, hashes des sources installées environment.json. Coût d'achat externe 0; énergie et coût machine non mesurés.

Ce résultat soutient H12 sur la grille déclarée et établit une exécution logicielle idéale locale. La compatibilité avec une machine Quandela précise reste unverified : aucune spécification réelle des sources, pertes, détecteurs ou contraintes de compilation de plateforme n'a été validée. Zéro QPU, aucun SDK distant, aucun secret, achat, compte, push ou publication. Pas de preuve de nouveauté, avantage quantique ou généralisation de l'agent.

Commandes principales : voir argv dans results/manifest.json; validation : python3 <Mathbox>/computation-audit/scripts/validate_manifest.py runs/20261113-c12-sdk-photon/results/manifest.json --root .; tests : python3 -m unittest discover -s tests -p test_sdk_photon.py -v. Aucun ajustement de l'expérience après les résultats; sources et données du run restent figées.
