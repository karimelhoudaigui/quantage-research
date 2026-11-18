# C11 — vérification et interprétation, 14 novembre 2026

Contrat : 128requêtes inédites/64groupes,64supportées/64horscontrat; deux
annotations distinctes concordent sur128actions/tâches avant toute génération.
Le preflight parcourt les JSON/JSONL historiques et préserve184fichiers; aucun
doublon exact de requête ou texte normalisé trouvé sur1385requêtes distinctes.
Aucune absence de contamination sémantique/préentraînement n'est prouvée.

Exécution réelle : Qwen0.5B128réponses et SmolLM2-135M128réponses, checkpoint,
versions, messages, tokens, temps et RSS enregistrés. Les deux manifestsgeneration
sontcompleted. Qwen120formats conformes/0abstentionsmodèleconformes; Smol0formats
conformes,106limitesdetokens/22EOS. Les réponses non conformes ne sont pas des
abstentions sémantiques réussies. Aucun remplacement de trace absente.

Comptes primaires : strict0bon/0faux; mots-clés23/26; directQwen55/65 (dont6
tâches erronées sur supportées); sans vérificateur55/44; numérique55/44; v423/12.
Les44erreurs du bras numérique obtiennent un certificat valide pour le problème
canonicalisé. Le veto retire32erreurs et32bonnes acceptations. H1échoue :
72.7%erreurs retirées mais41.8%bons retenus, seuil90%. H2suffisance réfutée
par cesnouveaux contre-exemples de contrat, sans revendication de nouveauté.
H3échoue : consensus128refus, rétention0. Risqueundefined quandaucuneacceptation.

L'ablation numérique nulle découle des formulations déterministes correctes;
aucune performance de détection de coefficients LLM n'en est inférée. Les
mauvaises acceptations portent sur fidélité/portée de contrat; leur solution
numérique peut coïncider accidentellement avec un optimum de la tâche modifiée.
Exemple : lesdeuxclausesdeparité omises ont néanmoins des optima de cardinalité4.
Àl'inverse, q_d794812ac7a6ed89 autorise sixsommets quand le texte impose au plus deux : la solution canonique de cardinalité6 laviole.
q_e32bebd83797a997 demande100échantillons etrefuse une distribution; le modèle
propose pourtant lesprobabilités etlecertificat passe. Ces exemples conservent
leurtexteexact etleursolution dans lesbruts, sanslescorrigeraprèsconsultation.

Audits : scripts/audit_c11.py réagrège indépendamment du scorer lescomptes,
risques/dénominateurs, identités/modèles/tokens, formulationsetoptima/probabilités,
route locale ethashes gelés. Leschecks s'exécutent sansimporter lesLLM.
L'auteur de cet audit final est l'intégrateur, pas un nouveau relecteur.
L'auteurcorpus etle relecteur de labels/protocole sontdistincts; modèle commun
possible, relecteurconnaissantv4, pasannotationhumaineaveugle. Leurquota échoue
aprèslivraison de cesartefacts etdesrevuesSDK; revuefinale C11indépendanteabsente.

Résultats finis vérifiés par l'intégrateur; généralisationetoriginalité ouvertes.
Pas d'intervalle populationnel sur cejeu de convenance apparié, pas QPU.
Le bras C14 est une analyse complémentaire post-C11 séparée, pas une réparation
ou un remplacement des résultats réservés C11.
