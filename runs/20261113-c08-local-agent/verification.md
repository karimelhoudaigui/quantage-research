# C08 — vraies générations locales, résultat négatif conservé

32 appels de génération réellement terminés,16 cas x2conditions, aucun manquant.
Qwen2.5-0.5B-Instruct à révision/hash fixes, CPU float32,32 réponses brutes avec
messages exacts et tokens. Total26788 tokens d'entrée et 2 015 de sortie;
378.403101833s mur,362.394129s CPU processus, dont7.946690791s de chargement.
Les temps n'incluent pas acquisition/développement; énergie/coût matériel inconnus.
Aucun achat/API fournisseur ou QPU; inférence hors ligne, pas de code distant.

Sous-ensemble sélectionné sans labels :16 cas dans8groupes, huit cas par famille;
après relecture historique indépendante, dix supportés et six hors contrat.
Le contrôleur compile déterministement le contrat proposé par le LLM, qui ne
génère pas les coefficients. Le benchmark n'est pas un LLM seul de formulation.

| Méthode | Contrats supportés acceptés /10 | Hors contrat acceptés /6 | Risque parmi acceptations |
|---|---:|---:|---:|
| Strict |0|0|non défini (aucune acceptation)|
| Mots-clés |3|1|1/4|
| Local sans dossier |5|2|2/7|
| Local avec dossier |4|2|2/6|

Les dix refus sur supportées du strict et les refus de schéma ne prouvent pas
une bonne abstention du LLM. Parmi les propositions conformes, aucun modèle
n'a choisi explicitement l'abstention. Le contrôleur sans dossier bloque une
proposition sur données invalides; deux autres erreurs de contrat MIS passent
son certificat numérique. Le dossier n'apporte pas de gain sur ces16 paires :
une acceptation correcte devient refus de schéma, aucune mauvaise acceptation
n'est éliminée. Il utilise18642 tokens d'entrée contre8146 et216.7480s de
génération contre152.7597s, sans égalité de budget d'entrée.

Par famille : sans dossier,5/5 MIS supportés acceptés mais2/3hors contrat;
avec dossier4/5et2/3. Photonique :0/5supportés acceptés dans chaque bras,
car les huit réponses par bras déclarent family=mis et la tâche photonique.
Cette contradiction est refusée. Deux réponses MIS documentées utilisent une
tâche inconnue. Il s'agit de conformité/contradictions de schéma, pas forcément
de JSON syntaxiquement invalide; aucun contenu n'est réparé après score.

Les raisons libres contiennent aussi des interprétations incorrectes; leur
qualité complète n'est pas certifiée par l'évaluation de l'action/tâche. Le
certificat numérique ne lit pas le texte, et son succès sur les acceptations
est attendu puisque la formulation est déterministe après validation des données.
Les labels sont issus de rôles distincts mais non humains aveugles et peuvent
partager le modèle des concepteurs. Les métriques C08 sont auto-vérifiées.

Protocole, sélection, réponses, génération et scoring ont leurs manifests v2.
Prochaine expérience : C09 préenregistré après ces erreurs, schéma sans famille
redondante et veto textuel borné, testé sur les groupes non générés en C08.
Ne pas fusionner ces deux étapes comme un test aveugle unique.
