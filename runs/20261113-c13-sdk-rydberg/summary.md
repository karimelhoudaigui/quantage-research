# C13 terminé — dynamique réelle Pulser et limites observées

162 programmes AnalogDevice à deux atomes réellement construits et simulés (Pulser1.7.2/QuTiP5.2.3), comparés à un Hamiltonien4x4 indépendant avec interaction finie. H13 soutenue dans le domaine et les tolérances déclarés : Hmax 6.12e-17, probabilitésmax 0.000472653 (<0.005), normalisationmax 1.61e-09 (<1e-8). Aucune précision1e-10 revendiquée pour la dynamique.

Neuf sondesSDK : sept rejets; durée101ns arrondieà104ns avec avertissement; registre sanslayout accepté pour construction/simulation malgré requires_layout. La compatibilité QPU reste nonétablie. Tempsmur21.82s, CPU3.73s; aucun achat ouQPU.

Preuves : protocol.md, sources.json, environment.json, results/raw.jsonl, metrics.json, manifest.json, verification.md; trois testsanalytiques propres passent. Revue indépendante encore requise. L'intégrateur peut ajouter ce résultat logiciel et la troisième famille de dynamique au manuscrit sans l'appeler généralisation agentique.

Prochaine expérience justifiée : vérifier, dans une nouvelle évaluation prospective d'agents, la préservation des unités/durées et le refus des hypothèses matérielles insuffisantes. Les effets de frontières échantillonnées et les arrondis doivent rester distincts de la justesse de la formalisation et des droits d'accès QPU.
