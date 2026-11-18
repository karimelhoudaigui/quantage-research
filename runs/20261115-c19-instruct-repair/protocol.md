# C19 — baseline instruct4B et boucle de réparation

15 novembre2026, avant acquisition/inférenceC19. Les petites configurations
non-thinkingC15–C17 échouent aux contraintes; C18premierappel thinking atteint
1024tokens sans JSONfinal (HTTP récupérable, aucun retry). Nouvelle baseline
Qwen3-4B-Instruct-2507, uniquement non-thinking selon la carte originale.
Conversion communautairebartowskiQ4_K_M àcommit/LFSshaépinglés. Runtime
b12359 déjà vérifié, MetalMTL0,CPUthreads4. Fit8GiB à tester, jamais promis.

Étape capacité :les2anciens casdéveloppementC16 080d034c34b2,4e0256180e89,
un appel initial chacun,512tokens/call,contexte4096,180s/complétion,aucun
réessai de modèle. Même consigne de primitives, avec distinction explicite
optionsdisponibles/sélections et arêteslistées/toutespaires. GrammaireJSONde
forme; aucun coeff/clauses ajouté par le compilateur ou référence en prompt.
SamplerT0.7,p0.8,k20,penalties0;seedSHAIDround0. Pas de pensée cachée.
Modèle natifnon-thinking, templateGGUF via/apply-template. Réserve3GiBavant
startup/1GiBavantcall. Un seul moteur GPUen même temps.

Si au moins1proposition fidèle et ressourcesviables, geler avanttest un
nouveau corpus avec combinaisons absentes du développement historique.
Comparer direct/auto/guidée, initialepartagée,2appels/bras/cas,512tokenschacun,
mêmes budgets de contexte/sampler et sélection sansgold. Corpus/testcomplet
à préenregistrer après capacité et avant toute observation de testC19.
Aucun C15/C16test relabellisé nouveau. Pas d'entraînement, achat, secret,
publication,pushouQPU. Annotations/revues finales séquentielles si quota natif
toujours épuisé; ne pas les déclarer indépendantes.
