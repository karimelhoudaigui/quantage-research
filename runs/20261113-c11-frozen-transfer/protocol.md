# C11 — transfert du contrôleur figé et risque sélectif

Préenregistrement avant génération et avant consultation de la nouvelle annotation.
Priorité : C10-v4 a été ajusté sur C09; sa performance sur de nouveaux groupes
est inconnue. L'audit C11 a trouvé un probe de cardinalité paire; ce probe reste
hors du corpus de test et ne déclenche aucune correction v4.

## Positionnement et hypothèses
La revue primaire research/c11-literature.md et c11-comparison.json distingue
NL4Opt, OptiMUS, Opti-Agent-Bench, Opt-Verifier, VeriSimpl, SOVER et QAOS.
Ajouter un vérificateur, un risque sélectif ou un workflow structuré ne suffit
pas à établir une originalité. Contribution candidate étroite : banc apparié
multidomaine qui sépare erreurs de sens, certificat de sortie et admissibilité
logicielle/matérielle, avec transfert d'un veto figé et échecs conservés.
Originalité globale non démontrée; la recherche de recouvrement doit continuer.

H1 (primaire, checkpoint Qwen) : sur les nouvelles propositions, le veto v4
retire au moins la moitié des fausses acceptations du bras numérique et conserve
au moins 90 % de ses acceptations correctes. Deux critères conjoints; si le bras
numérique n'a aucune erreur ou aucune acceptation correcte, résultat non résolu.
Décision sur comptes finis exacts, sans test populationnel ni ajustement après.
H2 : un certificat numérique d'une instance n'implique pas sa fidélité au texte.
Un contre-exemple réel nouvellement généré suffit à réfuter la suffisance;
l'absence de contre-exemple sur C11 ne démontre pas cette suffisance.
H3 exploratoire : accord de deux modèles + mêmes contrôles diminue le nombre
d'erreurs tout en conservant au moins 80 % des bonnes acceptations de Qwen+v4.
Le désaccord entraîne abstention; aucun rôle ne lit les labels de référence.
Les coûts des deux générations sont comptés, pas attribués deux fois aux
ablations qui réutilisent une même réponse.

## Corpus et annotations
Auteur distinct /root/literature, cible 128 requêtes = 64 groupes appariés,
32 groupes par famille, textes français et anglais. Chaque groupe partage les
données et oppose une intention supportée à une clause changée/ambiguë.
Qualité d'annotation prioritaire sur le nombre. Aucun entraînement.
L'auteur déclare ce qu'il a lu; il n'inspecte pas v4 ni ses scores avant création.
Relecteur /root/c11_audit annote public_cases.json sans ouvrir les labels auteur
ou le générateur. L'intégrateur compare ensuite les deux fichiers figés et
arbitre les désaccords AVANT toute génération. Désaccords et versions conservés.
Ce sont des rôles LLM distincts, pas des humains ni une indépendance de modèle
prouvée; le relecteur connaît l'implémentation v4 et cela reste une menace.
Contrôler IDs, groupes, doublons exacts de requêtes et de textes normalisés,
intersection avec C01–C10, données partagées au sein des paires et domaine.
Les nouveaux groupes ne sont pas une preuve d'absence de contamination du
pré-entraînement. Corpus de convenance; pas d'intervalle sur une population
naturelle non définie. Sensibilité aux désaccords annotée séparément si présents.

## Versions figées et inférence
Ne modifier aucun fichier C01–C10 ni compact_v2/v3/v4, core, verification,
contracts, compact_agent, C09/instructions.md. frozen-inputs.json les fixe par
SHA-256. Copier le runner v2 dans c11_inference.py en ne changeant que le budget
à 1 650 s et l'inventaire ressources. Le contenu de l'instruction reste C09.
Qwen2.5-0.5B-Instruct, révision 7ae557604adf67be50417f59c2c2f167def9a775,
checkpoint existant C07. Second modèle plus petit SmolLM2-135M-Instruct,
révision 12fd25f77366fa6b3b4b768ec3050bf629380bac, Apache-2.0, Safetensors
publics seulement; ressources card principalement anglaises, limite connue.
Même runtime isolé torch2.8/Transformers4.45.2, CPU float32, quatre threads,
greedy, seed20261113, maximum128 nouveaux tokens, entrée4096tokens sans
troncature silencieuse. Modèles chargés séparément, sans outils réseau au runtime.
Ordre lexicographique ID; un appel par modèle et requête, aucun retry ou réparation.
Si l'acquisition ou un modèle échoue, conserver son échec et évaluer les seuls
bras observés; pas de consensus simulé ni de réponse absente comptée abstention.

## Comparaisons et architecture
1. Strict historique; 2. mots-clés historiques.
3. LLM direct : décision/tâche décodées sans exécution; erreurs de format séparées.
4. Agent sans vérificateur : schéma/types nécessaires au logiciel puis formulation
   déterministe et solution, sans certificat numérique ou veto.
5. Même agent + vérificateur numérique fini.
6. Même agent + numérique + veto sémantique v4 figé.
7. Architecture complète : deux propositions réellement indépendantes de contexte,
   accord des tâches/actions, v4, vérification numérique et sélection documentaire
   locale. Refus si désaccord ou information matérielle insuffisante pour QPU.
Chaque rôle est explicite : intention LLM, formalisation/ formulation
et solver déterministes, veto lexical, oracle numérique, frontière matérielle
et évaluation hors ligne. Aucun besoin d'un LLM par rôle, aucune boucle corrective.
Le bras compact formule déterministement : l'ablation numérique peut être nulle
par construction; elle n'est pas une mesure de détection d'erreurs de coefficients
LLM. Le LLM direct mesure une décision, les bras agents une autorisation locale;
ne pas les comparer comme s'ils étaient tous des exécutions QPU.

## Métriques et décisions
Rapporter dénominateurs : N observé, supportés/hors contrat, bons/mauvais acceptés,
fausses/correctes abstentions du contrôleur, formats invalides et abstentions LLM.
Couverture sélective C = tous acceptés/N; rappel supporté = bons acceptés/supportés;
risque R = mauvais acceptés/tous acceptés (non défini si aucun accepté).
Exactitude sémantique action+tâche LLM séparée de validation numérique et de
conservation des données/formulations. Tableau par famille, langue et clause.
Courbe aux niveaux de contrôles discrets, pas score probabiliste calibré.
Comparer avant/après sur les mêmes réponses; compter erreurs retirées et bonnes
acceptations perdues. H1/H3 selon seuils ci-dessus, H2 par contre-exemples.
Groupes appariés non indépendants; pas de p-value ou intervalle binomial naïf.
Tokens, temps chargement/génération, CPU, pic RSS si disponible, fins/troncatures,
versions et empreintes brutes; coût énergie et session inconnus. Zéro achat externe.

## Budget et arrêt
Deux acquisitions/générations maximum, 256 appels prévus si corpus complet;
1 650 s internes et 1 800 s runner par modèle, 4 MiB logs, 12 MiB résultats.
Petites évaluations/oracles 60 s. Pas de QPU, API payante, entraînement ni Codex
imbriqué. Arrêter le bras sur échec/limite; préserver toute trace partielle.
Ne jamais retoucher v4 ou le corpus après sorties pour améliorer le score C11.
C12 prépare séparément des circuits SDK avec oracle bosonique; ce résultat
n'est ni une validation sémantique C11 ni un run matériel.

## Artefacts attendus
public_cases.json, deux annotations, adjudication et gold figé, contrôles de
séparation, manifests de provenance par modèle/scoring, bruts, métriques,
revue indépendante, summary.md et completion.json; article intégré ensuite.
