# C21 — audit du pilote avec évaluations candidates

15 novembre 2026. Le recalcul confirme **deux patches valides et une formulation fidèle sur deux**. `29507bb778cc` ajoute littéralement l'implication manquante `x5 - x4 <= 0`; `417127d82203` conserve son orientation inversée. Les deux réponses terminent sur EOS. Le contrôle passe655assertions en0,026 s, sans nouvelle génération, serveur ou solveur.

**Limite d'indépendance :** cet agent a écrit le corpus C19 et l'appliqueur/driver C20. Cette passe utilise un replay distinct et les annotations/oracle reviewer C19, sans importer les fonctions patch ou scorer de production; elle n'est pas une revue indépendante de l'auteur. Les deux anciennes erreurs C19 sont du développement observé à plusieurs reprises, jamais un nouveau test réservé.

## Résultats et diagnostic

| Cas | Domaine référence | Domaine candidat avant→après | Désaccords faisabilité avant→après | Objectif erroné | Fidèle après |
|---|---:|---:|---:|---:|---|
| 29507bb778cc, FR, n6 | 6 | 8→6 | 2→0 | 0 | Oui |
| 417127d82203, EN, n4 | 2 | 1→1 | 1→1 | 0 | Non |

Le premier patch contient un seul `add_constraint`. La nouvelle ligne est écrite par le modèle, pas complétée par l'appliqueur. Le domaine et les valeurs d'objectif coïncident ensuite exactement avec la référence sur les64affectations. Le diagnostic identifie l'implication5→4 omise dans le texte; cela explique l'édition mais ne constitue pas un certificat autonome de raisonnement.

Le second patch remplace la ligne5 `x1-x2<=0` par la même chaîne : aucune modification littérale. Son diagnostic cite correctement les deux lignes candidates violées par `[1,1,0,0]` — ligne0(lhs2≤1 faux), ligne5(lhs1≤0 faux) — puis affirme à tort que « selecting entry 2 requires also selecting entry 1 » est capturé par `x1-x2<=0`. L'orientation reste inversée et les exclusions inventées restent présentes. Le témoin est admissible pour la référence mais rejeté par le candidat; le même contre-exemple subsiste. L'évaluation arithmétique correcte des lignes n'assure donc pas leur correspondance avec les clauses du texte.

Les diagnostics font583 et767caractères ASCII sous la nouvelle borne768; les réponses font221 et250tokens sous1024. Elles n'atteignent pas le plafond de complétion. L'absence de troncature sur tokens ne démontre pas que ces plafonds sont sans effet sur la génération.

## Trace candidate-only et replay

Les trois évaluations de témoins contiennent19évaluations de lignes au total : deux témoins sur cinq lignes pour le casn6, un témoin sur neuf lignes pour le casn4. Chacun des index, lhs, relations, rhs, booléens de satisfaction, objectifs et faisabilités candidates est recalculé depuis la **seule initiale LLM**. Toutes les valeurs concordent. Les rhs sont ceux des lignes candidates; aucune ligne, coefficient ou correction issu de la référence n'est fourni par l'outil.

Le verdict minimal est exactement celui de C19. Le gloss anglais se reconstruit exclusivement à partir de ses booléens expected/proposed. Les payloads envoyés correspondent au verdict, aux évaluations et au gloss conservés; leurs seuls autres contenus sont consigne, requête publique et réponse initiale historique. Le code de contrôle utilise séparément les annotations reviewer pour vérifier le verdict, sans s'en servir pour fabriquer les valeurs de l'outil ou appliquer une édition.

Le replay décode les opérations depuis raw_response et les applique à une copie de l'initiale. L'ajout et le remplacement observés sont vérifiés, puis les chaînes sont compilées avec l'interpréteur AST distinct de l'audit C16. Modèles matérialisés, objectifs, domaines, témoins, scores avant/après et optima de référence concordent avec l'oracle antérieur et les sorties enregistrées. Cette passe ne prouve pas la correction de toutes les opérations possibles sur tout patch.

Les deux paires HTTP, seeds, T0.7/top-k20/top-p0.8, demandes1024tokens, contexte4096 avec réserve3071en entrée, prompts/templates, identifiants et probabilités choisies sont contrôlés. Les initiales et leurs hashes sont conservés sans rééchantillonnage. Les sources/entrées du gel C21 restent conformes. Aucun checkpoint ni binaire n'est rechargé ou réacquis.

Les quatre résultats enregistrés DFS/HiGHS concordent avec une nouvelle énumération exacte des modèles candidats : maximum129 pour le premier,33 pour le second. Le premier est utilisable pour l'original après certification; le second reste sous l'optimum original78. Le choix ex post du solveur le plus rapide est cohérent et le coût des deux est inclus. Aucun solveur n'est relancé par l'audit.

## Coûts et interprétation

Deux nouveaux appels C21 :3383tokens d'entrée,471de sortie,33,809192 s de durées des réponses,0,034061 s de CPU client par réponse. Avec les deux initiales historiques attribuées :4742tokens d'entrée,725de sortie,48,745947 s et0,062270 s de CPU client. Les initiales ne sont ni régénérées ni réputées gratuites.

La phase prend56,283345 s, dont21,168952 s de chargement; CPU client2,987373 s et serveur13,552415 s, total16,539788 s. Matérialisation0,001168458 s, vérification0,001202375 s, portfolios0,404831792 s. Le nettoyage avant inférence est enregistré séparément :7,819828 s, CPU propre0,920110 s et CPU enfants2,959890 s. Énergie, développement/annotation et coût complet de session restent inconnus; ces durées ne sont pas un benchmark matériel isolé.

**Aucun effet causal isolé :** C21 change conjointement l'évaluation arithmétique candidate, le gloss, le plafond de complétion512→1024 et celui du diagnostic256→768 par rapport à C20. Observer1/2 après0/2 ne permet pas d'attribuer la différence au seul outil, à la seule taille de budget ou à un raisonnement plus long. Ce sont deux probes posthoc; aucune généralisation ni nouveauté n'est établie.

Le [JSON](c21-observed-review.json) conserve diagnostics exacts, opérations,19évaluations recalculées, résultats cubes/solveurs,655contrôles, coûts, versions et hashes avant/après. Commande de contrôle inline `python3 -B`, bibliothèque standard, SIGALRM60s, Python3.9.6; helpers `research/c16-observed-audit.py`, sans import de production patch/scorer. Seules les deux sorties de revue autorisées sont écrites. Aucun article, source, state ou claim n'est modifié.
