# QuantAge — état de recherche au 15 novembre 2026

Mission active : obtenir une contribution scientifique nouvelle, vérifiée et reproductible, avec manuscrit défendable. Le prototype C01–C10 était un socle; il ne réalisait pas cette mission plus large. **L'article n'est pas déclaré prêt pour soumission.**

## C19 clos ; C20 négatif ; C21 pilote effectué ; C22 capacité préparée

La vraie boucle est exécutée : LLM écrit variables, objectif et contraintes,
contre-exemples finis, nouvelle formulation/éditions LLM, DFS et HiGHS réels.
C19 :80réponses uniques sur20nouveaux problèmes/10signatures réservées.
Fidélités initial/direct/auto/guidé =13/15/12/13. Sur17faisables10/12/9/10 ;
3infaisables réussis partout. Une réparation mathématique faisable réelle,
une régression d’objectif46→48. H19gain≥4 échoue(+1). Six des sept modèles
initialement faux sont recopiés malgré feedback. Pas de supériorité démontrée.

Annotations public-only distinctes20/20, oracle indépendant20/20domaines,
recalcul final23 506contrôles/80HTTP/160sorties solveurs. L’auditeur final est
aussi auteur du corpus : pas revue aveugle indépendante des données.
Deux reprises de ressources conservent tous les appels : lancementv1 sans
inférence puis auto13+7cas jamais appelés, aucune répétition/imputation.
748.058s de lignes,907.255s de phases ; CPU du nettoyage parent non compris.

C20 :2ancienscasC19 deviennent développement,2patches valides mais0fidèle.
Diagnoses tronqués à256caractères et contradictoires ; aucun coefficient
réparé par le code.615contrôles de revue,4sorties solveurs,8tests adversariaux.
C21 : mêmes2ancienscas, outil exact d’évaluation des PROPRES lignes candidates,
gloss des booléens, cap1024/diagnostic768 :1/2fidèle, implication5→4 ajoutée
par l’agent ; mauvaise orientation2→1 persistante dans l’autre cas. Revue
finale en cours. Pas nouveau test ni attribution causale des changements joints.

C22 proposé : capacité du Qwen3-8B-GGUF officiel, avant nouvelle campagne.
Sources/fitdisque/RAM à vérifier ; aucun poids8B acquis ou appel8B à ce checkpoint.
Le matériel8GiB et les échecs de formulation motivent un pilote borné,
pas une promesse de réussite. Les tests C19 ne seront jamais réannoncés aveugles.

C15 reste bloqué (16dev,1test/15absents,H15nonrésolue). C16clos :63réponses
réelles/64tentatives, direct1/16,auto1/16,guidé[1,2]/16, gain[0,1] inférieur3
pour toute issue inconnue ; unique certificat sur domaine vide. Revue distincte
26 863contrôles. C17nonthinking2B :0/2fidèle malgré2schémas valides ; C18thinking :
2caps1024sansréponsefinale. Tous incidents et sources préservés.

Article C19 : paper/article.md, main.tex et main.pdf compiléTectonic0.17.0.
Huitpages relues, équations complètes, Unicode et JSONmultiligne réparés,
revue distincte du manuscrit et clarifications locales appliquées. Archives
et sources exactes dans paper/build-c19-v5/ ; pas de soumission. Originalité
et maturité scientifique de soumission restent non établies.

Des tmp_pack Git anciens/fermés/classés déchets saturent encore le disque.
Nettoyage ciblé borné, refs et objets valides conservés ; rapports séparés.
Les réglages locaux gc.auto/maintenance.auto ont été essayés, sans preuve
qu’ils arrêtent cette accumulation ; restauration des valeurs initiales à
faire en fin de campagne. Aucun autre projet/processus utilisateur touché.
Caches publics C07/C16 restaurés, cachefloatC14absent avec URL épinglée.

## Résultats de la nouvelle campagne

C11, runs/20261113-c11-frozen-transfer, est terminé. Nouveau corpus de 128requêtes/64 groupes, deux familles et deux langues équilibrées. Auteur et relecteur distincts, accord 128/128 action+tâche avant génération; gold original et revue conservés, normalisation séparée. Le relecteur connaissait v4; aucune indépendance humaine ou de modèle n'est démontrée.

256 réponses réellement générées, Qwen2.5-0.5B-Instruct et SmolLM2-135M-Instruct, CPU float32 hors ligne. Référence Qwen+numérique : 55 bonnes/44 mauvaises acceptations. Avec veto v4 figé : 23/12. Retrait de 32 erreurs et de 32 bonnes réponses; H1 préenregistrée échoue (rétention 41.8 %, seuil 90 %).44 mauvaises acceptations ont un certificat numérique valide pour une interprétation hors contrat. Un contrat modifié peut parfois partager ses optima avec le contrat canonique; erreur de portée ne signifie pas toujours solution numérique erronée.

Smol : 0 contrat conforme sous 128 tokens,106 troncatures/22 EOS; consensus 0 acceptation, risque non défini et couverture nulle. Aucun refus de format n'est crédité comme compréhension du LLM. L'ablation numérique est nulle parce que la formulation est déterministe; pas un benchmark de coefficients LLM. Détails : results/metrics.json et verification.md. Annotations et protocole revus séparément; scores finaux auto-audités après épuisement du quota natif.

C12, runs/20261113-c12-sdk-photon, est terminé et revu par auteur distinct. Perceval 1.3.1 réellement exécuté,486 évaluations, 3 modes/2 photons,2 916 probabilités. Erreur maximale auteur 2.22e-16 sous 1e-10; recalcul orthogonal 3.33e-16. Six sondes SDK : 5 rejets et 3 photons acceptés légitimement hors contrat. Programme SDK idéal seulement, aucune machine Quandela précise validée.

C13, runs/20261113-c13-sdk-rydberg, est terminé et revu par auteur distinct. Pulser 1.7.2/QuTiP 5.2.3 réellement exécutés,162 séquences AnalogDevice à 2 atomes. Comparaison nominal/SDK :probabilités 4.7265e-4 sous 0.005, H initial 6.12e-17 sous 1e-10, normalisation 1.61e-9 sous 1e-8. L'origine temporelle de l'écart est plausible, non isolée. Sur 9 sondes : 7 rejets; 101 ns arrondis à 104 ns; registre sans layout accepté localement malgré une exigence backend distincte. Pas de compatibilité QPU ou bruit Pasqal établi.

C14, runs/20261113-c14-model-scale, est bloqué pour sa comparaison complète. Le sous-ensemble de 32 cas/16 groupes C11 est sélectionné sans scores, après consultation du test : analyse exploratoire seulement. Qwen2.5-1.5B, révision 989aa7980e4cf806f80c7fef2b1adb7bc71aa306, RAM physique 8 GiB. Float16 CPU : 128 exclamations, 151 936 logits NaN au contrôle du premier prompt. Bfloat16 : 151 936 logits finis, puis un contrat conforme de 49 tokens en 493.62 s. Les deux bras sont arrêtés précocement, sans faire passer les absents pour des abstentions. Un seul cas unique observé par configuration; H14 non résolue. Les manifestes failed et les métadonnées manquantes restent tels quels. Le diagnostic float16 standalone n'a pas de hash avant observé; aucun enregistrement v2 inventé. Pas de retry supplémentaire C14.

## Preuves et code

28 claims conservés : 21 verified, 6 refuted, 1 inconclusive. 20 handoffs : 17complete et3blocked. Les succès de contrôles ne prouvent ni nouveauté ni mission achevée. BaseGit fee83eb4575198e3e142d41c621300b4d11361d8, arbre modifié sans commit/push.

Le preflight C11 préserve 184 fichiers C01–C10 et ne trouve aucun doublon exact parmi 1 385 requêtes historiques distinctes inspectées. scripts/audit_c11.py contrôle les 256 traces, identités/tokens, labels, scores, routes et solutions numériques sans importer les modèles ou le scorer. Les 109 cas C05 et les résultats antérieurs restent vérifiables par les audits existants.45 tests passent à ce stade; vérifications finales dans research/c11-c14-validation.json.

quantage/core.py, verification.py, contracts.py et compact_v2/v3/v4 restent figés. Les nouveaux codes sont séparés : c11_inference.py,c11_score.py,sdk_photon.py,sdk_rydberg.py et variantesC14. Runtime LLM .venv-local-llm (Python3.9.6); SDK Perceval .venv-quantum-sdk (Python3.11), Pulser Python 3.11 déjà installé. Pas de modification du venv LLM par SDK.

paper/article.md et main.tex sont désormais reconstruits ensemble par scripts/build_paper.py depuis les résultats enregistrés. Question, positionnement, contrats, architecture, protocoles, résultats et menaces structurent le texte; historique détaillé dans paper/archive/, copié avant réécriture. Aucun PDF validé : aucun compilateur disponible. Les manuscrits historiques restent intacts.

## Faiblesses et suite

La revue primaire de 17 sources (NL4Opt,OptiMUS,Opti-Agent-Bench,Opt-Verifier,VeriSimpl,SOVER,etc.) montre des précédents proches. Une architecture modulaire, un veto ou le risque sélectif ne sont pas nouveaux à eux seuls. Matrice dans research/c11-comparison.json; aucune recherche globale exhaustive ou nouveauté démontrée. La seconde passe déléguée a échoué par quota; l’intégrateur a ajouté trois sources primaires et un rapport ciblé, sans prétendre à une revue exhaustive.

Les sous-agents ont livré audit historique, corpus, annotations, revue pré-exécution et revues SDK, puis deux ont échoué par quota (message 11:33 PM, fuseau/date de réinitialisation inconnus). Ne pas boucler sur ce quota. Les scores C11/C14 et le nouveau manuscrit n'ont pas de nouvelle revue indépendante finale.

Prochaines priorités : conserver le blocage C14 et ses diagnostics; établir des baselines plus fortes; une nouvelle méthode sémantique évaluée sur groupes encore inédits (C11 sera alors développement); étude contrôlée du temps échantillonné Pulser; lien évalué entre décision d'agent et contraintes backend. Ne pas adapter v4 puis réappeler C11 test aveugle. Pas de statistiques populationnelles sur ce corpus de convenance.

Zéro dépense externe, QPU, publication, push ou message externe automatique. Aucun secret volontairement lu/copié. Simulations et SDK acceptés ne sont jamais présentés comme une exécution matérielle. Coût machine/énergie/session inconnu; temps/tokens/RSS des processus enregistrés.
