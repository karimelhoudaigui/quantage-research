# C20 — audit des deux probes de développement

15 novembre 2026. **Deux réponses réelles, deux patches valides, zéro formulation fidèle après application.** Le replay littéral distinct, les cubes binaires et les quatre résultats de solveurs concordent avec les sorties conservées. Le calcul borné passe 615 contrôles en 0,084 s; aucune nouvelle inférence, aucun solveur ni serveur n'est lancé.

**Indépendance limitée :** cet agent a écrit le corpus C19 et les modules patch C20. Cette revue est un contrôle de calcul séparé de l'appliqueur/scorer de production, pas une revue indépendante de leur auteur. Elle réutilise les annotations et l'oracle reviewer C19; elle n'en établit pas une nouvelle indépendance. Les deux cas sont du développement choisi après observation C19, sans test réservé ni conclusion de généralisation. Aucun brut ou source C21 n'a été lu.

## Résultats par cas

| ID | Taille | Domaine référence | Domaine candidat avant/après | Désaccords faisabilité avant/après | Objectif erroné | Fidèle après |
|---|---:|---:|---:|---:|---:|---|
| 29507bb778cc | 6 | 6 affectations | 8 / 8 | 2 / 2 | 0 | Non |
| 417127d82203 | 4 | 2 affectations | 1 / 1 | 1 / 1 | 0 | Non |

**29507bb778cc.** Les cinq éditions remplacent les lignes0 à4 par leurs chaînes originales exactes. Le modèle matérialisé est littéralement identique à l'initiale; l'implication5→4 omise reste absente. Pour le témoin `[0,1,0,0,0,1]`, toutes les lignes du candidat sont satisfaites, alors que la référence l'interdit. L'exclusion `[2,5]` invoquée par le diagnostic est satisfaite : 0+1=1. Le diagnostic commence par affirmer une violation, puis reconnaît explicitement que la ligne est satisfaite. Il est auto-contradictoire; le modèle n'a pas littéralement écrit l'inégalité0+1>1. Les deux contre-exemples initiaux restent résiduels.

**417127d82203.** L'édition remplace la ligne3 `x1+x3<=1` par `x0+x3<=1`, déjà présente à la ligne2. Comme x3 est interdit, cette substitution change le texte mais pas le domaine. Les exclusions inventées et l'implication inversée restent. Pour le témoin `[1,1,0,0]`, les violations effectives du candidat sont la ligne0, lhs2≤rhs1 faux, et la ligne5, lhs1≤rhs0 faux. La ligne `x0+x3<=1` invoquée par le diagnostic est satisfaite, lhs1≤rhs1. Le témoin est **admissible pour la référence et rejeté par le candidat**; le diagnostic parle d'un témoin marqué infaisable sans maintenir cette distinction. Le même contre-exemple subsiste après patch.

Les deux diagnostics comptent exactement **256 caractères ASCII** et finissent au milieu d'une phrase (« compulsory re » et « The pair ( »). Les complétions terminent sur EOS à302 et113tokens, sous le plafond512. La fin prématurée du diagnostic correspond donc à sa borne de caractères, pas à un arrêt sur le plafond global de tokens. Cette observation descriptive n'établit pas que cette borne cause les erreurs ni qu'un diagnostic plus long les corrigerait.

## Replay, HTTP et solveurs

Le contrôle décode les patches depuis raw_response et applique indépendamment chaque `replace_constraint` observé à une copie du JSON initial. Il vérifie l'indice dans la liste courante, les champs, la borne32opérations, le diagnostic ASCII, puis normalise avec l'interpréteur AST distinct de l'audit C16. Il n'importe pas parse_patch, le compilateur de production ou le scorer. Le modèle final, ses lignes d'origine et le hash de l'initiale correspondent exactement aux traces. Cette passe porte sur les opérations effectivement observées; elle ne prouve pas la correction de toutes les opérations possibles de l'appliqueur.

Toutes les64 et16affectations sont évaluées avec les annotations reviewer C19. Domaines de référence et ensembles complets d'optima coïncident avec l'oracle antérieur. Faisabilité, objectifs, témoins avant/après et verdicts du scorer concordent. Les nouvelles consignes sont séparées des consignes historiques; les initiales sont réellement réutilisées, sans nouvel appel initial. Les messages, feedbacks minimaux, templates, hashes de prompts, seeds, plafonds et paramètres T0.7/top-k20/top-p0.8 sont contrôlés sur les deux paires HTTP. Les tokens et probabilités des jetons choisis correspondent aux comptes et scores conservés. Ces probabilités restent des heuristiques API traitées.

DFS et HiGHS ont deux portfolios concordants, soit **quatre résultats réellement enregistrés**. Une nouvelle énumération des modèles candidats confirme leurs objectifs129 et33 et leurs solutions. Sur le premier cas, la solution rendue est aussi optimale pour l'original, mais le domaine proposé est faux : usable reste false. Sur le second, la solution `{0}` a valeur33 contre78 pour `{0,1}` dans l'original; elle est admissible mais sous-optimale pour l'original. L'accord des solveurs ne répare donc pas la formulation. Aucun solveur n'a été réexécuté pendant cet audit.

## Comptabilité

| Périmètre | Appels | Entrée | Sortie | Durées des réponses | CPU client des réponses |
|---|---:|---:|---:|---:|---:|
| Nouveaux appels physiques C20 | 2 | 2352 | 415 | 28,690225 s | 0,032131 s |
| Initiales historiques + révisions | 4 attribuables | 3711 | 669 | 43,626980 s | 0,060340 s |

Le coût des initiales n'est pas une dépense physique C20 supplémentaire, mais il n'est pas présenté comme gratuit pour une chaîne complète. Les deux représentations ne partagent pas un effort égal simplement parce que leur plafond512 est identique.

La phase d'inférence C20 prend48,925130 s, dont19,017571 s de chargement; CPU client3,111328 s et serveur9,541885 s, total12,653213 s. Les durées de réponse excluent le chargement. La matérialisation conservée prend0,001766499 s et la vérification0,001199208 s. Les deux portfolios totalisent0,395571875 s, coût des deux solveurs compris; import/processus de scoring et session complète sont distincts.

Le nettoyage de ressources **avant** inférence est enregistré séparément :5,386900 s de durée,0,515121 s de CPU propre et2,970689 s de CPU enfants. Il ne faut ni l'omettre silencieusement ni le fusionner avec les durées par réponse. Énergie, annotation, développement et coût complet de session restent inconnus. Le chargement observé annonce Metal37/37couches et un buffer positif, sans preuve d'exécution exclusivement GPU ni nouvel audit des poids.

## Provenance et portée

Entrées : `runs/20261115-c20-grounded-edits/probe-guided-v1/driver/{raw.jsonl,generation.json,http/*}`, `probe-score-v1/{raw.jsonl,metrics.json}`, gel et resource-management, plus publics/initiales/feedback et annotations/oracle reviewer C19. Les SHA du gel C20 sont conformes et tous les fichiers lus par le contrôle restent identiques après lecture. Les manifests originaux sont completed/exit0. Le checkpoint et le runtime ne sont pas rechargés ou réacquis par cette revue.

Le [JSON compagnon](c20-observed-review.json) conserve les615contrôles, diagnostics exacts, replay de chaque édition, évaluations arithmétiques par ligne de chaque témoin, domaines/optima, coûts et hashes. L'aide AST/cubes est `research/c16-observed-audit.py`, SHA `3d8939f15bd201aba7b4228d30541600fcfeab0f081e71147b692c41d9a0c167`. Exécution inline `python3 -B`, Python3.9.6, bibliothèque standard, SIGALRM60s, n≤6 et deux réponses; seules les deux sorties de revue autorisées sont créées, sans nouveau répertoire de calcul ou script persistant.

Conclusion limitée : dans ces deux probes sélectionnées après C19, le format diagnostic+patch a produit des opérations syntaxiquement valides et aucune réparation sémantique. Il n'établit ni un échec général des éditions guidées, ni une causalité du diagnostic, ni un succès prospectif de C21. Aucun article, source, état ou claim n'est modifié.
