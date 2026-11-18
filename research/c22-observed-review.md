# C22 — une réponse connue, une tentative inconnue

16 novembre2026. L'audit confirme **0 formulation fidèle sur1réponse connue, plus1issue inconnue**. Le8B corrige réellement le sens d'une implication dans417127d82203, mais le modèle reste globalement infidèle. L'appel associé à29507bb778cc n'a ni réponse, ni métadonnées finales, ni manifeste final conservé : il reste inconnu et n'est jamais rejoué ou imputé. Sur les deux cas prévus, le nombre fidèle est donc borné entre0 et1; ce n'est pas un score complet ni un intervalle de confiance.

Le [calcul borné](c22-observed-review.py) passe223contrôles, en0,009 s environ, sans importer l'appliqueur/scorer de production, sans nouveau modèle, serveur, solveur ou fichier manquant créé. Son [manifeste](c22-observed-review.audit/manifest.json) est valide; cela qualifie cet audit terminé, pas une expérience C22 complète.

## Trois statuts à conserver séparément

| Étape | Complétions | Évidence et statut |
|---|---:|---|
| probe-guided-v1 | 0 | Garde disque avant démarrage serveur; generation.partial_error et runner.failed, exit1. Ce zéro concerne uniquement cette tentative de démarrage. |
| probe-guided-v2,29507bb778cc | 1tentative déclarée,0réponse conservée | Requête000 présente, raw vide; réponse000, generation.json et manifeste final absents. Cause inconnue. La réconciliation de processus conservée ne trouvait plus de processus llama appartenant au lot. |
| probe-remaining-v3,417127d82203 | 1réponse | generation.completed, planned=completed=1, serveur exit0, réponse EOS. Runner.result-missing avec exit0 parce que deux sorties001 avaient été déclarées pour un lot d'un seul cas. |

Pourv3, seules `http/001.request.json` et `http/001.response.json` sont déclarées manquantes; elles ne correspondent à aucun second cas attendu dans remaining_cases.json. Les fichiers000, le raw et les métadonnées existent et leurs hashes correspondent au manifeste. L'audit conserve l'erreur de déclaration sans créer les001 ni modifier le manifeste. Ce défaut du runner ne rend pas la réponse000 inconnue, et n'efface pas l'interruption réellement inconnue dev2.

L'unique cas restant est exactement417127d82203, déclaré jamais appelé dans la réconciliation dev2. La seed et les messages de la requête inconnue identifient29507bb778cc. Aucune nouvelle initiale4B ni seconde tentative du cas inconnu n'est incluse. Une requête sérialisée ne prouve pas combien de tokens le serveur a effectivement consommés ou générés.

## Patch8B et certificat fini

La sortie connue est un patch à une opération : remplacer la ligne5 `x1-x2<=0` par **`x2 - x1 <= 0`**. Le replay indépendant depuis le texte brut produit exactement le modèle enregistré. Le diagnostic identifie correctement que « selecting entry2 requires entry1 » ne signifie pas1→2. Cette amélioration locale est observée; elle ne suffit pas à une formulation fidèle.

Les contraintes candidates conservent trois incompatibilités non demandées : `[0,1]`, `[0,2]`, `[0,3]`, en plus des deux exclusions publiques. Le domaine candidat demeure `{ {0} }`, tandis que la référence reviewer admet `{ {0}, {0,1} }`. Le témoin lexicographique résiduel est **[1,1,0,0]**, accepté par la référence et rejeté par le candidat. Après l'édition, la ligne d'implication est satisfaite, lhs−1≤0; la seule ligne candidate qui viole encore ce témoin est la ligne0, `x0+x1<=1`, lhs2>rhs1.

Sur les16affectations, l'objectif reste identique mais il subsiste1désaccord de faisabilité. La référence a un optimum78 pour `{0,1}`; le candidat a un optimum33 pour `{0}`. Les domaines et optima de référence coïncident avec l'oracle C19 antérieur. Le diagnostic n'est pas certifié comme raisonnement global, et la correction d'une relation ne permet pas d'ignorer les exclusions inventées. Aucun solveur n'est exécuté par cet audit : les optima cités proviennent de son énumération exacte.

Les messages réutilisent l'initiale C19 et le feedback C21 attendu. Les évaluations arithmétiques du témoin sont recalculées à partir des seules lignes de l'initiale; aucune correction de référence n'entre dans cet outil. L'application littérale n'utilise que le patch et le modèle initial. L'oracle séparé intervient ensuite, uniquement pour l'évaluation de fidélité.

## Mode non-thinking et placement observé

Les templates conservés des requêtes inconnue et connue se terminent par le préfixe exact :

~~~text
<|im_start|>assistant
<think>

</think>

~~~

Il s'agit d'un bloc vide **fermé dans le prompt**, pas d'un raisonnement généré. Le serveur connu reçoit `--jinja` et `--chat-template-kwargs {"enable_thinking":false}`; generation.json consigne le contrôle du suffixe. La réponse contient directement le JSON patch et termine sur EOS après106tokens. Les IDs, probabilités choisies, moyenne logarithmique, seed, T0.7/top-p0.8/top-k20, cap1024 et réserve de contexte4096 sont cohérents avec les requêtes conservées. Les scores API restent des heuristiques traitées, pas des vraisemblances globales conditionnelles.

Les logs connus confirment **37/37couches déportées**, avec deux buffers modèle MTL0 positifs486,87 et3968,47MiB. Cela prouve le placement observé pour cette exécution; cela ne mesure ni la RAM globale de macOS, ni un pic complet, ni une exécution exclusivement GPU. Le serveur restant utilise batch/microbatch128 et quatre threads CPU. La continuation est enveloppée par caffeinate après amendement de ressources. Ces changements, l'interruption et la variante de checkpoint empêchent une interprétation en effet causal isolé de taille ou benchmark de latence. Aucun fit général sur8GiB ni faisabilité à contexte6144 n'est déduit.

## Coûts connus et inconnus

| Périmètre observable | Réponses connues | Entrée | Sortie | Durées des réponses | CPU client des réponses |
|---|---:|---:|---:|---:|---:|
| Nouvelle réponse417 | 1 | 1537 | 106 | 20,371954 s | 0,030630 s |
| Cas417, initiale historique+révision | 2 | 2164 | 208 | 26,839187 s | 0,046424 s |
| Deux initiales historiques+seule révision connue | 3sur4attribuables prévues | 2896 | 360 | 35,308709 s | 0,058839 s |

La requête inconnue contient1854IDs d'entrée et demande au plus1024tokens de sortie. **Tokens réellement consommés/générés, durée, CPU et résultat de cet appel restent null/inconnus, jamais zéro.** Les sommes ci-dessus sont partielles; elles ne constituent pas le coût total des deux nouveaux appels.

La phase connuev3 prend50,097389 s, dont28,098785 s de chargement; CPU client6,263109 s et serveur5,566396 s, total11,829505 s. Le wrapper prend55,163264 s. Le démarrage abandonnév1 conserve7,656353 s et5,711480 s de CPU client malgré zéro complétion. L'acquisition déclare64,563125 s. Les trois fichiers resource-management enregistrent séparément les nettoyages :5,222098 s,2,111280 s et0,000004917 s, avec CPU propre/enfants dans le JSON. La première erreur de préparation documente aussi un nettoyage dont le compte supprimé n'a pas été persisté; il n'est pas reconstruit. Coût complet de session, énergie et coût de la tentative inconnue restent indisponibles.

## Cache, provenance et limites

Le registre `research/c19-c21-validation-before-cache-eviction.json` contient17validations de manifeste réussies **avant** éviction des caches publics4B/C16, avec échecs expérimentaux distincts de la validité de leur preuve. `storage-additional-v2.json` conserve SHA, fermeture lsof, URLs de restauration et alias. Les poids évincés sont absents; les bruts et sources consultés sont intacts. L'audit lit ce registre antérieur et les hashes des traces, sans prétendre réexécuter aujourd'hui les17validations complètes après suppression des poids. Restaurer les octets publics serait nécessaire pour certains rejeux. Le8B actif n'est ni lu ni rehashé par ce contrôle; son pin officiel est celui des métadonnées d'acquisition.

Le [contrat](c22-observed-review.contract.json) fixe58entrées textuelles/métadonnées, un thread, cap70s de runner et60s interne, logs65kio. Le [résultat brut](c22-observed-review.audit/raw.json) et sa [copie JSON](c22-observed-review.json) conservent la réponse, le replay, le cube, le témoin évalué par ligne, statuts, coûts, événements de cache et hashes avant/après. Commande enregistrée : `python3 -B research/c22-observed-review.py --output research/c22-observed-review.audit/raw.json`. Le validateur retourne `valid evidence record (run status: completed)` pour le nouvel audit. Les manifestes C22originaux restent failed, absent ou result-missing comme observés.

**Revue non aveugle/non indépendante de l'auteur :** ce rôle a construit le corpus C19 et l'infrastructure patch C20. Les prédicats finis et l'interpréteur sont séparés de l'appliqueur/scorer de production et utilisent les annotations reviewer; cela n'établit pas une nouvelle indépendance humaine ou de modèle. Les deux cas sont anciens, sélectionnés posthoc pour développement. Aucun nouveau test C23, sortie C24, résultat de généralisation, nouveauté ou avantage quantique n'est examiné. Aucun fichier manquant, source, modèle, article, state ou claim n'est modifié.
