# C13 — programme Pulser à deux atomes et oracle Hamiltonien séparé

Préenregistré le13novembre2026, après clôture C12 et avant tout import ou exécution Pulser/QuTiP pour cette étude. CodeSDK installé1.7.2 inspecté comme texte seulement. Aucune modification des cycles historiques.

Question : un programme Pulser réel associé à AnalogDevice, dans sa portée de simulation idéale, reproduit-il une dynamique de deux atomes décrite indépendamment, et quelles contraintes sont réellement validées? H13 est une assertion finie de concordance, pas une revendication de nouvel algorithme ou de généralisation LLM.

## Modèle et conventions

Deux atomes aux coordonnées(-r/2,0),(r/2,0) en µm, canal Rydberg global, état initial|gg>. Pulse.ConstantPulse(t_ns,Omega,delta,phi), mesure ground-rydberg, sans modulation du pulse, bruit ou shots. Le Hamiltonien indépendant H/hbar=Omega/2 sum_i(exp(-i phi)|g><r|_i+exp(i phi)|r><g|_i)-delta(n0+n1)+V n0 n1, V=C6/r^6. C6 est une donnée de spécification du Device installé et sera enregistrée; ce n'est pas un ajustement à ses résultats.

L'oracle est construit dans l'ordre|gg>,|gr>,|rg>,|rr>, puis diagonalise sa matrice hermitienne4x4 par numpy.linalg.eigh pour calculer exp(-iHt)|gg>. Pulser emploie l'ordre|rr>,|rg>,|gr>,|gg>; la traduction est explicitement inversée. Aucun Hamiltonien, état final ou solveur QuTiP n'est utilisé pour construire l'oracle. Le Hamiltonien SDK extrait au temps0ns est comparé séparément, avec traduction de base. Les API exactes sont celles du module installé1.7.2; QutipEmulator.from_sequence(...,sampling_rate=1.0,with_modulation=False,evaluation_times='Minimal').run(atol=1e-10,rtol=1e-10,max_step=0.001) fournit la dynamique par ODE.

Grille : r∈{6,10,14}µm, Omega∈{0,1,2}rad/µs, delta∈{-1,0,1}rad/µs, phi∈{0,pi/2}, durée∈{100,500,1000}ns, soit162évaluations. Aucun échantillonnage aléatoire. Géométrie, amplitudes, désaccords et durées doivent respecter les specs enregistrées; les limites des layouts/backend QPU ne sont pas supposées satisfaites.

Tolérances préenregistrées : Hamiltonien au temps0,1e-10 en rad/µs; probabilités finales contre pulse constant nominal,5e-3; normalisation de chaqueétat,1e-8. Le seuil de probabilité tient compte de l'échantillonnage en ns, du retour à zéro de la forme SDK à sa frontière finale et de la comparaison au pulse continu nominal. Les tolérances du solveur ODE ne sont pas des garanties d'erreur globale. Conserver l'erreur mesurée plutôt que prétendre à une précision1e-10 pour les probabilités. Pas d'approximation de blockade parfait : interaction finie intégraleV conservée.

Contrôles analytiques sans SDK : Omega=0 conserve|gg>; V=delta=0 donne produit de deux rotations indépendantes avec pexc=sin²(Omega*t/2); conservation de norme et hermiticité. Les tests analytiques vérifient une construction distincte des assertions de boucle.

## Sondes de validation

Observer sans présumer les issuesSDK : distance2µm sousminimum; atome horsrayon; canal rydberg_local indisponible surAnalogDevice; amplitude supérieureau maximum; detuning supérieureau maximum; durée inférieureà16ns; durée101ns non multiplede4ns; séquence de durée>6000ns; registre libre sanslayout versuslayoutrequispourQPU. SDK peut arrondir une durée ou différer une contrainte à un backend; enregistrer avertissements, durée demandée et obtenue plutôt que compter comme rejet. Un registre libre accepté ne prouve pas les contraintesQPU; aucuneconnexionouBackendQPUne sera créé.

## Ressources et arrêt

Utiliser uniquement Python/opt/homebrew/bin/python3.11, Pulser1.7.2 et QuTiP5.2.3 déjàinstallés; versions et hashes sources enregistrés avantrun. Aucun venv LLM modifié, aucuneinstallationpourC13. Un threadnumérique, budget300secondes, plafond162simulations+9sondes. Arrêter l'expérienceprincipale au premierécart de tolérance, préserver le manifest d'échec; ne pas réécrire les sorties. Si API inaccessible, documenter l'échec avant correction dans une version de reprise séparée. AucuncalculQPU, compte, secret, achat, push, publicationou messageexterne.

ProvenanceMathboxv2 : commande, hashes avant/après, baseGit, versions, temps, bruts. H13 est soutenue seulement sur la grille et les conventions déclarées si touslescontrôlespassent. Unevalidation SDK/Device est distincte de compatibilité matérielle d'un QPU réel. Généralisationagentiqueetnouveauténe sont pasévaluées. Revue indépendante d'auteur encore requise aprèsrun.
