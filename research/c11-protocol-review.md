# Revue indépendante du protocole et du code C11 avant exécution

Relecteur : /root/c11_audit. Revue de code, pas nouvelle expérience de performance.
Je connais les versions historiques et v4 pour les avoir auditées. Je n'ai ouvert ni private_gold.author.json, ni build_corpus.py, ni aucune intention de label auteur; le corpus public n'était pas encore disponible lors de cette revue.

## Conclusion

Le protocole répond à la faiblesse principale : v4 est conservé sans correction et évalué sur un nouveau corpus; annotations auteur/relecteur séparées puis arbitrage avant génération. Les sept catégories de comparateurs sont explicites. Le direct mesure action/tâche, les agents une décision d'exécution locale : cette différence doit rester visible dans les tables. Aucun coefficient n'est généré par le LLM et l'ablation numérique peut être nulle; le protocole le déclare correctement.

La chaîne d'inférence ne lit pas le gold : elle charge les cas publics, les instructions fixes et les poids locaux vérifiés, puis produit une réponse par ID. Les contrôleurs n'importent aucun fichier d'annotation. Les deux modèles ont des contextes séparés et aucun outil d'accès au dépôt pendant génération; cela ne démontre pas leur indépendance statistique ou une indépendance de famille de modèle des annotateurs. Le consensus compare bien les mêmes tâches/actions, puis applique v4, l'oracle numérique et la route locale.

Les métriques principales ont des dénominateurs explicites : couverture tous acceptés/N, rappel correct/supportés, risque erronés/tous acceptés. Les sorties de format invalide et les abstentions du modèle sont distinguées. H1 vérifie deux seuils conjoints; le cas où le bras de référence n'a aucune erreur ou aucune acceptation correcte est non résolu. H2 ne conclut pas à la suffisance en l'absence de contre-exemple. H3 requiert une réduction stricte des erreurs et au moins 80 % de rétention; un zéro d'erreur de référence ne peut donc produire d'amélioration stricte.

## Corrections et clarifications recommandées avant gel

1. **Définition des effets appariés.** Dans paired, removed_wrong/removed_correct classe actuellement les cas uniquement selon expected_action. Le compteur principal accumulate classe correctement une proposition de mauvaise tâche sur un cas supporté comme erreur. Réutiliser ce même prédicat de correction pour les paires. Les schémas numériques disjoints rendent ce cas peu probable pour les agents exécutables actuels, mais les définitions devraient coïncider.
2. **Validation des labels.** Le scorer valide les IDs, mais pas les enums expected_action, la nullité de expected_task pour abstain, ni sa cohérence avec family/group_id. Une valeur malformée serait traitée silencieusement comme hors contrat. Ajouter ces validations dans le scorer ou un preflight exécuté et conservé avant génération.
3. **Matrice partielle.** Le score ignore correctement les réponses absentes au lieu d'imputer une abstention. En revanche H1 est calculé sur toute portion observée sans marqueur de campagne partielle. Figer avant exécution que l'échec/timeout conduit à un résultat partiel et ne valide pas l'hypothèse pour le corpus planifié; décrire séparément les comptes observés. L'ordre ID étant fixe, une troncature n'est pas un sous-échantillon aléatoire.
4. **Identité des bras.** Les fichiers de réponses n'incluent pas l'identité modèle par ligne; elle figure dans generation.json. Vérifier en preflight d'évaluation les deux métadonnées et leurs manifests pour empêcher une inversion de fichiers primaire/secondaire. Les prompts exacts et fin de génération doivent être contrôlés et rapportés.
5. **Limites de chargement.** Le try/finally d'inférence commence après chargement du modèle. Un échec d'initialisation peut donc n'avoir aucun generation.json; le manifest du runner et stderr devront être la preuve de cet échec, sans métadonnée inventée. Le budget interne est contrôlé entre requêtes; le runner reste la borne finale.

Aucune modification de ces scripts ou du protocole par le relecteur. Aucun nouveau calcul LLM, aucun accès réseau, SDK ou QPU. Cette revue ne remplace pas l'audit final des données, labels, métriques et conclusions après exécution. Les recommandations ne justifient aucun ajustement de v4 sur les exemples de test.

## Empreintes au moment de cette revue

Date UTC : 2026-11-13T19:58:56.699628+00:00

- quantage/c11_score.py : 32ce0afaf7493e63a712caed99ceacbae3cfb3e919e9df22196201e1f65e389d
- quantage/c11_inference.py : a57fd120df771ca6125529737d5a77ae7735e705fbbfeaf53ba51c52b2752ad6
- runs/20261113-c11-frozen-transfer/protocol.md : 340afe2d1256596f1d33f77a189a44f181554169dda3301dade44d58bbd868a2


## Annotation indépendante figée avant comparaison

Date UTC : 2026-11-13T20:07:37.965761+00:00

Corpus public SHA-256 : d181acd855b9db47f53763ee8154a03a838e04683ec5bee8de137f04c9480a45.
Annotation relecteur SHA-256 : 3660c3f0787f030231f3cf404e7d75dd0abd59564c8eef6ad10ce2916391c235.
128 requêtes lues individuellement; chaque rationale conserve l’énoncé et la justification du contrat. Aucune consultation de private_gold.author.json, build_corpus.py ou corpus-provenance à labels; aucun appel au veto, à l’agent ou à un modèle pour produire ces labels. Connaissance antérieure de v4 et de l’audit déclarée ci-dessus. Validation élémentaire des données numériques réalisée séparément des décisions textuelles. Répartition : {"mis": {"propose": 32, "abstain": 32}, "photon": {"propose": 32, "abstain": 32}}.
Les identifiants courts mis/photon ne sont utilisés comme expected_task que pour propose; null pour abstain. Les catégories changed_clause sont propres au relecteur et ne constituent pas un vocabulaire partagé avec l’auteur. La comparaison pertinente porte d’abord sur action/tâche; préserver l’annotation originale avant toute normalisation ou arbitrage.

## Vérification des corrections avant génération

Les trois corrections prioritaires sont présentes dans le scorer relu après annotation : les paires utilisent action+tâche; les labels sont validés pour action/famille/tâche/groupe; H1 devient unresolved_partial_generation si la collecte primaire est incomplète. SHA-256 du scorer relu : 4042958024addcbb0ae5a5c7b4c358db4b9a5a602863b6baa41d907386a65065. Aucun label auteur ou résultat candidat consulté pour cette vérification.
