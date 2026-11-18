# Summary

Revue du manuscrit C19 court, versions `article.md`/`main.tex` et PDF **build-c19-v4/main.pdf**, huit pages. Lecture intégrale des deux sources, de l'extraction PDFKit et inspection visuelle des huit PNG existants; cinq passes séquentielles selon mathbox:referee : correction, cas limites, exposition, notation, portée des claims. Deux corrections locales et une suggestion; aucune objection critique ou majeure retenue.

Le résultat central est correctement négatif : **guidée13/20, auto12/20, gain1<4**, une réparation mathématique et une régression; **direct15/20**. Les trois références infaisables sont séparées des17faisables. Le texte ne transforme ni la réparation isolée ni l'accord des solveurs en preuve de succès de H19. C20 n'apparaît pas parmi ses résultats.

**Revue non aveugle et non indépendante de l'auteur des données :** ce rôle a construit le corpus C19, effectué son recalcul final et écrit l'implémentation patch C20. Les contrôles numériques antérieurs sont réutilisés, pas revalidés ici comme nouvelle preuve indépendante. Les autres agents avaient épuisé leur quota; aucune relance n'a été tentée. Le JSON conserve hashes, couverture, réglages non exposés laissésnull et réconciliation. Seuls les deux rapports demandés sont écrits.

# Main mathematical concerns

Aucune objection critique ou majeure démontrée dans la portée relue. La formule du certificat compare bien faisabilité et valeurs d'objectif sur **tout** le cube; le témoin de cardinalité et la régression46→48 sont cohérents avec cette définition. Le calcul64=2^(7-1) des affectations affectées par un seul poids sur sept variables est correct. Aucun théorème général ni garantie CEGIS n'est transféré au LLM.

# Other mathematical concerns

**Mustfix — notation-all-F001, moderate, confiance0,99.** Définir explicitement la colonne « Équiv. optimisation ». `article.md:37` dit : « Nous rapportons séparément l'égalité des domaines et de tous les ensembles d'optimiseurs. » Le tableau `article.md:75–80`/PDFp.4 donne13/15/13/14 : il s'agit de **mêmes domaines ET mêmes ensembles d'argmax**. La seule égalité des optimiseurs donne15/16/15/15 dans le rapport antérieur. Une phrase/formule avant le tableau doit définir cette conjonction et la convention argmax vide pour un domaine vide. Aucun nombre n'est à changer. La distinction est matériellement visible : l'initiale66f7838312e1 garde son optimum mais a le mauvais domaine; la révisioncaf531e5abc9 garde domaine et optimiseurs mais change des valeurs d'objectif. Voir aussi `main.tex:51,114–128`, PDFp.2 et4.

# Exposition and organization

**Mustfix — claims-all-F001, moderate, confiance1.** Le chemin actif de reproduction doit être identifiable sans parcourir les historiques. `article.md:178`/`main.tex:286`/PDFp.8 cite : « scripts/run_c19_phase.py lance une phase avec runner borné dans une destination neuve, sans écrasement. » Ce wrapper estv1 et pointe vers initiale/feedback/tracesv1. Les résultats sontv2, et le score final utilise l'auto **test-self-union-v2**, pas les treize seules lignes de test-self-v2. Même le wrapper scorev2 standard ne substitue pas cette union. Nommer `scripts/run_c19_phase_v2.py`, `scripts/continue_c19_comparison.py` et surtout `runs/20261115-c19-instruct-repair/test-score-v2/manifest.json`, qui conserve l'argv exact du score de l'union. Distinguer réévaluation des traces et nouvelle génération en destination neuve. Les bonnes commandes existent déjà : c'est une correction de guide, pas une invalidation des résultats.

**Suggestion — adversarial-all-F001, minor, confiance1.** Compléter le tableau du sélecteur (`article.md:62–63`, `main.tex:92–93`, PDFp.4) par la branche « sinon seconde invalide » lorsque les deux propositions sont invalides. Le protocole complet la fixe déjà. Aucun effet sur C19, où tous les candidats sont valides; cela évite une politique partiellement décrite.

Le PDFv4 est lisible : sommes, chapeaux de D/f, relations et bornes sont présents; les tableaux conservent leurs cellules et l'exemple ses contraintes. L'extraction texte perd certains glyphes mathématiques, mais **ce n'est pas un défaut du PDF** : inspection visuellep.2 effectuée. Les coupures de code de l'exemplep.6 ne changent pas les symboles. Aucun débordement ou ligne manquante démontré sur les huit pages inspectées. Aucune nouvelle compilation ou conversion PDF n'a été exécutée.

# Claim and scope assessment

La calibration générale correspond aux revues existantes : CEGIS est un précédent avec hypothèses de progression non transférées; auto n'est pas présenté comme reproduction de Self-Refine; OptiMUS/Opt-Verifier/VeriSimpl/SOVER sont des voisins, sans revendication de première méthode ni supériorité. Les versions Pulserv1.8 et Percevalv1.3 sont distinguées des exécutions historiques et ne justifient aucun run QPU. Ce contrôle utilise les lectures primaires déjà consignées dans `c15-method-positioning` et `c19-positioning-hardware`; aucune nouvelle recherche exhaustive ou preuve d'absence d'antériorité.

Les coûts sont correctement séparés : 80appels physiques contre120attribuables aux trois bras partageant l'initiale, 748,06s de lignes contre907,255s de processus, chargements inclus dans ces derniers, CPU parent de nettoyage exclu et explicitement non compté. Le choix DFS/HiGHS est décrit comme profilage ex post, avec coût des deux, sans accélération nette apprise. Les limites de référence fiable, petit corpus synthétique, graine unique, domaines vides et non-indépendance sont explicites. Les chiffres ont été comparés au rapport antérieur, sans nouvel audit des bruts.

# Questions for the authors

Aucune obligation mathématique nouvelle non résolue au-delà des deux clarifications locales ci-dessus. Cette absence de question ne certifie ni universalité, ni nouveauté, ni maturité pour soumission.

# Suggested revisions

1. Définir Eopt comme la conjonction domaine égal et argmax égal, avec convention du domaine vide.
2. Pointer le manifeste finalv2 et la route d'union13+7 réellement utilisée.
3. Facultatif : préciser la sortie lorsque les deux candidats sont invalides.

Root a annoncé appliquer ces trois points et produire PDFv5. La présente revue reste attachée au **v4** listé dans le JSON; elle ne prétend pas avoir examiné une révision future.

# Overall assessment

Le manuscritv4 présente une étude empirique finie négative et une réparation réelle isolée, avec un direct plus performant que le guidé et des limites substantielles correctement annoncées. Les deux corrections demandées sont locales et ne modifient pas le verdict H19 ou les scores. Aucune recommandation de publication n'est émise. L'indépendance, les données historiques contextuelles et la validation externe des citations ne sont pas réétablies par cette revue.
