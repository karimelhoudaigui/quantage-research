# C14 — ressource/runtime, pas comparaison sémantique complète

Cycle bloqué pour l'hypothèse H14. Les32cas/16groupes sont choisis sans score,
mais après consultation de C11; même une matrice complète serait exploratoire.
Le checkpoint public Qwen2.5-1.5B est acquis àrévision fixe et hashLFS vérifié.
RAMphysique observée8GiB; aucune dépense/QPU.

Float16 CPU : une réponse complète composée de128exclamations en59.41s,
puis processus interrompu par l'intégrateur. Le contrôleforward sur le même
premier prompt donne151936NaN sur151936logits, argmax0='!'. Ce n'est pas une
mesure de compétence sémantique. Manifestgeneration/failed, sortiepartielle
conservée. Le diagnosticfloat16 est standalone, hors runner; commande/source
et résultat conservés, pas d'empreinteobservée avant exécution de ce diagnostic.
Ne pas lui inventer une provenancev2 complète.

Amendement avant nouvelle réponse : contrôler bfloat16 puis autoriser ce bras
seulement si tous les logits sont finis. Le probev2 precision-bfloat16/ a un
manifestcompleted;151936logits finis,0NaN/inf. La même première requête fournit
ensuite un contrat conforme,49tokens/EOS,493.6225s. La latence observée rend la
matrice32impraticable dans les1650s retenues; arrêt anticipé de ressources,
pas timeout effectivement épuisé. L'extrapolation au débit du premier cas est
une estimation, pas un temps total mesuré. Le manifestgeneration-bfloat16/failed
et l'événementd'interruption restent intacts.

Lesdeuxconfigurations ont chacuneuneseuleréponse achevée sur le même premier
cas.31cas sansréponsefinale ne sont pas31abstentions. Aucun score H14, gain de
taille ou résultat de consensus n'est calculé. Les appels interrompus peuvent
avoirconsommé du calcul sans trace de réponse complète; les durées desmanifestes
incluent le processusjusqu'àl'arrêt etdoivent être préférées àla seule somme
des latences achevées. Les generation.json n'ont pas été écrits aprèsSIGTERM;
picsRSS complets ettotaux d'appels démarrés manquent, ils ne sont pas fabriqués.

Observation bornée : sur ce prompt/checkpoint/runtime, la précisionfloat16
produitdesNaN, bfloat16deslogitsfinis. Pas de théorème sur touteslesCPUs,
versions, séquences de tokens ou modèles; ce n'est pas une causalité globale.
Les contrôles sont réalisés par l'intégrateur; nouveau quota de relecture
indépendante absent. Sources et paramètres des bras C11 demeurent inchangés.

Prochaine action : reprendre une baseline plus forte avec un runtime/format
et un budget effectivement adaptés à8GiB, puis préenregistrer une nouvelle
comparaison complète. Pas de retry supplémentaire dans C14. La prochaine
méthode sémantique demandera de nouveaux groupes indépendamment annotés;
les cas C11 et C14 sont désormais développement pour cette méthode.
