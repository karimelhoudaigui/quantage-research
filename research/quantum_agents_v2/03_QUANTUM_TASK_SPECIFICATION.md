# Tâche quantique candidate : dynamique analogique Rydberg

## Modèle de développement

Pour `N` atomes aux coordonnées 2D `(x_i,y_i)` en µm, deux niveaux `|g>` et `|r>`, un champ global constant et interactions finies de van der Waals :

`H(t)/hbar = sum_i [Omega/2 (exp(-i phi)|g><r|_i + exp(i phi)|r><g|_i) - Delta n_i] + sum_(i<j) (C6/r_ij^6) n_i n_j`.

Convention : `n_i=|r><r|`, `Omega` et `Delta` en rad/µs, `phi` en rad, durée en ns convertie en µs, distance en µm. `C6` provient de la spécification `Device` Pulser explicitement versionnée, jamais ajusté aux résultats. Le modèle est idéal, sans pertes, bruit, shots ou modulation de pulse. Ces hypothèses délimitent la validité et ne décrivent pas tout appareil Pasqal.

## Famille de tâche de développement

Demande textuelle : trois atomes non colinéaires, état initial `|ggg>`, pulse Rydberg global constant, durée demandée en ns, phase et amplitudes explicitement données, observable de distribution du nombre d'excitations. Le raisonnement nécessite de dériver les distances et les interactions pair-à-pair, vérifier le régime et les unités, construire un Hamiltonien à `2^N` états, puis proposer un calcul et une séquence SDK. Ce n'est pas une substitution de quelques valeurs dans un programme pré-écrit.

Une instance illustrative non réservée pourra utiliser les coordonnées `(0,0)`, `(6,0)`, `(2,5)` µm, `Omega=2`, `Delta=1`, `phi=0.4`, `T=200 ns`, initial `|ggg>`. Les références et résultats doivent être générés puis vérifiés avant tout appel de développement. Cet exemple n'est pas un résultat déjà exécuté.

## Variantes à prévoir en développement

- valide, avec géométrie non symétrique et observable explicitement définie;
- durée incompatible avec la clock Pulser (p.ex. 101 ns) pour détecter arrondi;
- géométrie trop serrée ou hors rayon;
- champ/canal absent ou amplitudes hors limites;
- layout/backend manquant alors que la demande exige spécifiquement une exécution QPU;
- information initiale, phase, unité, interaction ou observable absente;
- `noise`, modulation ou transitions autres que `ground-rydberg` demandés hors de la portée de l'oracle;
- demandes contradictoires ou ambiguës où clarification/abstention est préférable.

La liste sert à créer des **cas de développement seulement**. Aucun corpus réservé n'est consulté ni défini par révélation de labels dans ce document.

## Domaine de non-application

Pas de dissipation, bruit, pertes, calibration, contrôle local, forme temporelle variable, état initial cohérent, transition de niveau autre que `ground-rydberg`, shots, compilation de pulses, waveform optimization, QPU ou preuve de fidélité à une machine particulière. Ces demandes exigent abstention ou une extension et un oracle distincts.
