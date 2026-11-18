# Contrat de vérification multiniveau

Un résultat ne peut annoncer qu'un niveau réellement exécuté. Aucun niveau n'implique le suivant.

| Niveau | Contrôle | Échec / frontière |
|---|---|---|
| L1 — syntaxe | clés/type/schema, champs requis, unités explicites, nombres finis, dimensions et indices | IR invalide; pas de valeur par défaut silencieuse |
| L2 — fidélité sémantique | comparer paramètres, clauses, unités, omissions et intention à une référence annotée indépendante; séparer supporté/ambigu/hors-domaine | Équivaut à la référence finie, pas à comprendre tout texte libre |
| L3 — mathématiques | construire matrice dense sur petite taille; hermiticité, dimensions, convention, interactions `C6/r^6`, état normalisé; évolution unitaire exacte et probabilités normalisées | Certificat sur le modèle/instance et l'hypothèse donnés seulement |
| L4 — SDK | compiler avec la version locale Pulser; vérifier erreurs, avertissements, durée effective, pulses, état/canaux/registre; comparer la séquence construite à l'IR | SDK accepté ne prouve pas l'égalité à la demande |
| L5 — Device/backend | appliquer `AnalogDevice` documentation/construction; backend-specific/layout restrictions et disponibilité déclarés séparément | Construction locale ne valide pas QPU; `mimic_qpu`/backend sans connexion peut tester une partie des contraintes seulement |
| L6 — simulation | simulation locale Pulser, comparer à l'oracle indépendant selon tolérance préenregistrée; conserver résultats bruts | Simulation idéale ne mesure pas bruit ou réalisation physique |
| L7 — QPU | désactivé | Aucun run QPU, compte, connexion, job ou prétention de validation physique |

## Comparaison mathématique

Pour `N` petits, construire indépendamment `H` dans une base de chaînes d'excitation et calculer `exp(-iHt)|psi0>` par diagonalisation hermitienne. Vérifier `H=H†`, `||psi||²=1`, somme des probabilités 1 et observable demandé. Comparer les termes avec le Hamiltonien Pulser extrait et résultats de simulateur. La formule, correspondance d'indices et convention de phase doivent être revues avant gel.

C13 fixe un précédent de seuil `max |p_ref-p_sdk| < 5e-3`, mais cette valeur concerne un modèle constant nominal contre la représentation temporelle Pulser et n'est pas une garantie universelle. Toute réutilisation pour le pilote nécessite de confirmer qu'elle est adaptée au niveau d'erreur attendu; sinon le pilote est bloqué jusqu'à une analyse de tolérance.

## Exactitude de la demande vs normalisation

Si une durée de 101 ns devient 104 ns, la séquence peut être valide au sens SDK mais ne respecte pas strictement la demande. Le vérificateur doit distinguer:

- demande mathématiquement spécifiée;
- Sequence valide, durée réellement appliquée;
- différence explicitement autorisée par le contrat ou nécessitant clarification;
- compatibilité backend/QPU non testée.

L'acceptation d'un registre sans layout en simulation ne peut pas devenir « QPU compatible ».
