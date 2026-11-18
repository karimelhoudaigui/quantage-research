# C14 — bras différé avec modèle plus grand, analyse exploratoire

Préenregistré le14novembre2026 avant toute réponse du nouveau modèle, après
consultation de C11. Motivation : SmolLM2 n'a aucun JSON conforme à128tokens
(106troncatures), le consensus n'accepte rien; les modèles minuscules constituent
une faiblesse des baselines. Ne pas réparer v4 ou les instructions.

32requêtes reprises de C11,16groupes : quatre premiers IDs opaques de chaque
strate famille×langue, sans sélection sur les scores. Les deux membres de chaque
paire sont conservés. Modèle non entraîné sur ces données; auteur connaît déjà
C11, donc cette analyse n'est pas un nouveau test réservé indépendant.

Modèle Qwen2.5-1.5B-Instruct public à révision fixe, hashSafetensors vérifié.
RAMphysique observée8GiB; utiliser float16 CPU plutôt que float32 pour limiter
les poids àenviron3.1GoRAM. Cela confond taille, modèle et précision : aucune
conclusion causale isolée sur la capacité. Même instructionC09, greedy,4threads,
seed20261113, entrée4096tokens, sortie128tokens. Un appel par requête, pas de
retry/réparation, labels jamais lus par l'inférence. Mesurer temps/tokens/RSS,
EOS/troncatures. Pas d'API payante, entraînement, QPU ou nouvel accès matériel.

H14 exploratoire : fidélité brute action+tâche du nouveau modèle au moins
20points plus élevée que Qwen0.5 sur les mêmes32cas (soit au moins7décisions
correctes supplémentaires). Rapporter aussi les7comparateurs, les refus et
la rétention des bonnes acceptations aprèsv4, sans recalibrer H1 deC11.
Le seuil est un critère fini, pas un test populationnel. Si format/runtime
float16 CPU non pris en charge, conserver échec et arrêter ce bras.

Comparer le Qwen0.5 existant par simple sous-échantillonnage de ses32traces,
pas de régénération. Smol correspondant peut être inclus comme contrôle
format/couverture et consensus; aucun nouveau résultat d'architecture ne sera
présenté comme indépendant deC11. Les preuves antérieures restent inchangées.

Budget : téléchargement public<=3.3GiB et300s; génération interne1650s,
runner1800s/4threads; scores60s. Un seul checkpoint supplémentaire, disque
libre vérifié avant acquisition, aucune installation du runtime LLM nécessaire.
Si ressources insuffisantes, statusblocked avec traces réelles, pas de substitut.
