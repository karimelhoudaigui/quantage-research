# C11 terminé — hypothèse de rétention non soutenue

256 générations réelles sur 128 nouvelles requêtes, deux modèles locaux.
Annotations action/tâche concordantes de deux rôles avant génération, gold et
versions figés. Qwen + numérique : 55 bonnes et 44 mauvaises acceptations;
+ veto v4 : 23 et 12. Le veto retire 32 erreurs et 32 bonnes réponses.
H1 non soutenue (41.8% de rétention contre90% requis), H2 illustrée par44
contre-exemples réels, H3 non soutenue : Smol0format conforme, consensus0couverture.
Le risque du consensus est non défini; ce zéro n'est pas une garantie utile.

Preuves : protocol.md, adjudication.json, preflight.json, generation-qwen/,
generation-smol/, results/ et leurs manifestescompleted. Corpus128unique,
64groupes, pas256observations indépendantes. Les données structurées et la
formulation déterministe limitent la portée; pas de nouveauté démontrée.

Manuscrit restructuré autour des questions/méthodes/résultats, historique en
paper/archive/. Audit final des scores par l'intégrateur; revue finale distincte
interrompue par quota. Les revues pré-exécution/annotations restent valides.

Prochaine faiblesse : baselines minuscules et coût des erreurs de format.
C14 compare un modèle plus grand sur32cas sélectionnés par groupes, comme
analyse différée exploratoire, sans réécrire C11. SDKs validés séparément C12/C13.
