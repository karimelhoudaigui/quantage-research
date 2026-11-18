# Protocole Phase 2 — brouillon de pilote de développement

**Statut : non gelé; aucun pilote exécuté à cette version.** Il doit être relu par le rôle Scientific Reviewer avant implémentation/exécution. Les résultats ne peuvent pas être utilisés comme test réservé.

## Questions de garde

1. Question quantique : fidélité d'une description de dynamique Rydberg analogique à travers interprétation, IR, Hamiltonien, Sequence Pulser et choix local/abstention.
2. Hypothèses : H_A/H_B dans `02_SCIENTIFIC_QUESTION.md`.
3. Propriété mesurée au pilote : capacité du socle vérificateur à distinguer exactitude du modèle, acceptation SDK, normalisation du SDK et limites de Device; pas de performance générale d'agent.
4. Lien mission : compréhension, formulation, vérification et stratégie sur Pulser/Pasqal.
5. Baselines : A–F de `07_BASELINES.md`; pilote 1-call (si disponible) ne compare aucun baseline statistiquement.
6. Échec : IR mal typée acceptée, Hamiltonien non hermitien, état/probabilités incohérents, séquence différente annoncée fidèle, ou requête QPU/ambigüe acceptée comme validée.
7. Priorité : C13 offre un oracle local réel, et C13 a déjà révélé arrondi 101→104 ns et acceptation sans layout; la préservation de l'intention à cette frontière est une faille concrète à étudier.
8. Budget : une génération locale au plus, 120 s max, un cas principal n=3, quatre contrôles SDK/max, 300 s pilote total, un thread numérique; 0€ externes, 0 QPU, aucun réseau. Arrêt sans retry.

## Tâche principale non réservée

Cas de développement illustratif, à figer avec ses hash avant modèle : trois positions non colinéaires `(0,0)`, `(6,0)`, `(2,5)` µm; initial `|ggg>`; pulse global constant ground–Rydberg, `Omega=2 rad/µs`, `Delta=1 rad/µs`, `phi=0.4 rad`, `T=200 ns`; observable distribution du nombre d'excitations et `P(N_r>=2)`. Fournir explicitement l'id du Device/version; le `C6` est lu du Device local, non ajusté.

Contrôles de développement non réservés :

- `T=101 ns` et registre sans layout sont des sondes déjà exécutées dans C13. Elles peuvent servir uniquement de tests de régression et ne compteront dans aucun score nouveau.
- Distance inférieure au minimum du Device et grandeur manquante doivent être refusées/clarifiées avant résultat physique.
- Aucune interaction/drive/noise hors modèle ne doit être assumée.

Les cas qui alimenteraient un score devront être définis séparément et annotés par des rôles distincts avant génération.

## Référence et comparaison

Construire la référence à partir d'une matrice dense indépendante de dimension `2^N`, `C6/r^6`, de l'état initial et de l'évolution unitaire; contrôler hermiticité, trace d'état et probabilité. Puis compiler/simuler sur l'interpréteur Pulser 1.7.2 et comparer le système d'indices/pulses/durée. Reprendre le seuil C13 de 0.005 seulement s'il est confirmé adapté par le relecteur; sinon l'exécution est bloquée jusqu'à une tolérance préenregistrée justifiée.

Un appel de Qwen2.5-0.5B local, si validation de ressources et protocole reçue, est seulement un essai technique. Conserver réponse, prompt, version, hash, tokens, durée et erreurs; ne pas relancer. Aucune conclusion H_A/H_B avec un cas.

## Arrêt, isolation et non-retry

Exécuter uniquement sur données de développement nouvelles, dans un répertoire de run neuf. Ne pas lire/ouvrir le corpus/gold C23 ni aucun test réservé. Arrêter si les dépendances manquent, si une contrainte scientifique est indéfinie, si la mémoire/temps est dépassé ou si un invariant échoue. Conserver toutes sorties partielles. Aucun nettoyage de fichiers historiques.

## Protocole final réservé

**Non défini / bloqué.** Il faut une décision de seuil et puissance, annotateurs indépendants, revue ciblée de nouveauté, diversité réelle de solveurs/méthodes, validation ressources et approbation humaine. Le contenu test n'est ni inventé ni consulté ici.
