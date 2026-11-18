# QuantAge Research

Programme cumulatif sur la chaîne intention → compréhension → formulation → sélection du solveur, avec fournisseurs quantiques français comme cibles conditionnelles. L'infrastructure soutient l'évaluation; elle ne constitue pas à elle seule la contribution scientifique.

**C19 a maintenant exécuté une vraie boucle de formulation et réparation.** Le modèle écrit les variables, l'objectif et toutes les contraintes ; le vérificateur transmet des contre-exemples, puis le modèle révise sa proposition. Sur20nouveaux cas : direct15/20,auto12/20,guidé13/20 fidèles. Une correction mathématique guidée est réelle, mais le gain préenregistré échoue. DFS et HiGHS sont réellement exécutés. Résultats et limites dans [le rapport C19](runs/20261115-c19-instruct-repair/summary.md), [la revue](research/c19-observed-review.md) et [le PDF compilé](paper/main.pdf).

C20 puis C21 explorent des diagnostics et éditions explicites ; leurs anciens cas C19 sont du développement, jamais un nouveau test réservé. L'article reste un document de travail, sans nouveauté ou maturité de soumission démontrée.

Le pilote C28 sous la configuration C23 a expiré après 180 s sans réponse complète; le corpus réservé C23 n'a pas été appelé. Le gate reste bloqué, sans retry autorisé par le protocole. Le [rapport C28](runs/20261118-c28-c23-config-probe/summary.md) et [l'état de recherche](research/state.md) détaillent le résultat. Cette limite opérationnelle est consignée dans [l'article](paper/article.md), sans modifier les résultats C19/H19.

La recherche a dépassé le prototype C01–C10. **C11 a produit 256 réponses réelles sur 128 nouvelles requêtes**, annotées séparément avant génération. Le veto v4 réduit les mauvaises acceptations de 44 à 12 mais les bonnes de 55 à 23 : le critère préenregistré de rétention échoue. Le consensus avec SmolLM2 refuse tout. **Perceval et Pulser ont réellement été exécutés**, avec oracles et revues distincts, dans C12/C13. C14 reste bloqué pour une comparaison complète du modèle plus grand après diagnostic numérique et arrêt de ressources. Aucun résultat historique n'est écrasé.

**L'article n'est pas déclaré prêt pour soumission.** Les preuves, limites et critères manquants figurent dans [l'état](research/state.md), [le manuscrit](paper/article.md), [la maturité](research/maturity.json) et [les blocages](research/blockers.json). Le contrôleur v4 reste figé pour reproductibilité; son prototype ne certifie pas le sens d'un texte libre.

## Utiliser le prototype à LLM local

Dans ce workspace, l'environnement isolé et les poids sont déjà acquis. Choisir un répertoire de traces neuf :

~~~bash
.venv-local-llm/bin/python -m quantage.local_agent_cli --request examples/freeform-photon.json --record-dir /tmp/quantage-demo-neuf
~~~

Le modèle génère réellement un contrat; le contrôleur conserve la donnée d'origine, refuse les clauses hors portée reconnues, formule et résout localement. Le résultat et le texte brut sont enregistrés. Code de sortie 0 = accepté par le prototype, 2 = abstention. La sortie conserve semantic_certificate=false : le veto lexical ne prouve pas toute la sémantique d'un texte arbitraire. L'entrée est toujours un texte avec données JSON structurées, pas une extraction générale de documents.

Pour une nouvelle installation, les dépendances optionnelles sont dans requirements-local-llm.txt. Les poids et le venv sont ignorés par Git. Si absents seulement : créer un venv avec Python 3.9+, installer les versions fixées puis exécuter scripts/acquire_local_model.py avec les chemins indiqués dans C07. Le téléchargement public avoisine 1 Go et ne requiert ni token ni API payante. L'inférence est hors ligne, CPU, sans code distant; le coût machine/énergie n'est pas chiffré.

## Utiliser la chaîne locale

Python 3.9+; testé avec Python 3.9.6, bibliothèque standard uniquement. Depuis la racine :

~~~bash
python3 -m quantage examples/mis.json
python3 -m quantage examples/photon.json
~~~

Entrée JSON : exactement deux champs, intention et données. Les phrases reconnues sont celles des exemples; les variantes inconnues donnent une abstention (code de sortie 2). La sortie contient problème normalisé, formulation, vérification, route locale et solution. MIS : graphe simple, 1 à 12 sommets, poids entiers positifs, tous les optima par énumération. Photonique : deux modes, un photon, angles réels en radians, pertes nulles; modèle idéal flottant, sans bruit ou shots.

Un candidat Pasqal ou Quandela dans la sortie conserve le statut matériel «unverified». Le module quantage.routing examine séparément des propositions de solveur. Aucun exécuteur QPU ni accès réseau dans la chaîne.

## Vérifier et reproduire

~~~bash
python3 scripts/check.py
python3 -m unittest discover -s tests -v
python3 scripts/audit_results.py
python3 scripts/replay.py
python3 scripts/audit_continuation.py
python3 scripts/audit_local_agents.py
python3 scripts/audit_c11.py
python3 scripts/audit_c14.py
~~~

check.py valide le registre et les handoffs, pas la vérité scientifique. audit_results.py réagrège les lignes et contrôle les empreintes des entrées/sorties. replay.py reproduit les quatre expériences dans un répertoire temporaire neuf et compare toutes les lignes et métriques, hors temps d'exécution; il ne lance aucun appel Codex. Les tests du runner utilisent un exécuteur injecté et des mocks, sans fournir de performance scientifique.

Les commandes originales sont dans runs/*/results/manifest.json (schéma v2 du runner de provenance Mathbox). Chaque cycle conserve protocol.md, contract.json, données brutes, métriques, verification.md, summary.md et completion.json. Ne pas écraser ces sorties. Les quatre commandes scientifiques peuvent aussi être rejouées séparément avec une destination neuve :

~~~bash
python3 -m quantage.benchmark foundation --output /tmp/quantage-c01-new
python3 -m quantage.faultstudy --output /tmp/quantage-c02-new
python3 -m quantage.routingstudy --cases runs/20261113-c03-routing/cases.json --policy config/policy.json --output /tmp/quantage-c03-new
python3 -m quantage.transferstudy --cases runs/20261113-c04-transfer/cases.json --output /tmp/quantage-c04-new
~~~

## Reprise de recherche

Ouvrir ce dossier et demander à Codex de lire AGENTS.md, README.md, state/backlog/claims et les derniers cycles. Les fiches agents/ définissent les rôles. Le dernier état évite de réexécuter un résultat déjà vérifié.

Le runner optionnel exige Codex CLI authentifié pour ses appels réels. Aucune boucle Codex imbriquée ne doit être lancée depuis une session active. Son dry-run ne lance aucun modèle :

~~~bash
python3 scripts/run_cycles.py --cycles 1 --dry-run
~~~

Hors session imbriquée, une invocation réelle est bornée par config/policy.json et exige un arbre Git propre après revue et commit. Le runner conserve les logs, vérifie les handoffs et s'arrête sur timeout, échec, résultat manquant ou statut blocked. Une erreur antérieure doit être examinée et résolue avant reprise; ne pas supprimer son historique. Un verrou existant exige d'inspecter le processus avant suppression manuelle. Sur POSIX, le timeout termine le groupe de processus; le test de cette logique est simulé. La durée ne borne pas exactement les tokens ni le coût.

## Recherche et article

Les huit axes restent couverts par le backlog; deux familles servent ici le même problème de fiabilité. Sources primaires ciblées, versions et sections consultées dans research/sources/index.json; pas de revendication de nouveauté. Les claims antérieurs sont conservés, y compris ceux réfutés. «complete» signifie cycle clos, pas hypothèse confirmée ou programme scientifique achevé.

paper/article.md et paper/main.tex sont reconstruits ensemble par `python3 scripts/build_paper.py` depuis les résultats enregistrés. Le détail C01–C10 est conservé dans paper/archive/. La figure C11 existe en PDF/PNG avec provenance; ce PDF de figure ne constitue pas un manuscrit compilé. Tectonic0.17.0 officiel est acquis localement et vérifié ; cache et ressources restent dans le projet. Le PDF C19 est compilé, les PDF historiques ne sont pas rétroactivement validés. Avec une installation existante, depuis la racine :

~~~bash
pdflatex -halt-on-error -interaction=nonstopmode -output-directory=paper paper/main.tex
~~~

Aucune soumission QPU, dépense externe, publication, push ou message externe automatique. Aucun secret lu ou copié. Prochaine expérience proposée : [vérification des clauses et nouvelle validation indépendante](research/next-experiment.md). Les données C11/C14 seront du développement pour toute nouvelle méthode.

## Propositions externes et traces existantes

quantage/contracts.py valide explicitement les modèles externes avant les oracles finis. Les preuves C01–C04 restent figées; quantage/agent_pipeline.py traite un problème normalisé, une formulation et une référence locale sans appeler de fournisseur. Il annonce explicitement l'absence de certificat sémantique du texte.

Une proposition enregistrée conforme au schéma du protocole C06 peut être traitée avec cette commande (les deux chemins doivent désigner des fichiers réels) :

~~~bash
python3 -m quantage.proposal_cli --request request.json --proposal proposal.json
~~~

quantage.evaluation compare hors ligne ces propositions à des labels séparés. Les traces manquantes n'ont aucun score. Le corpus C06 contient 32 cas, 19 supportés après arbitrage; les tâches natives ont échoué par quota et cet échec reste conservé. La recherche publique C07 a ensuite acquis traces QCV/PQID et checkpoint libre. Les archives ne sont pas rebaptisées cas C06; leurs identités de modèles sont déclarées par les auteurs. C08–C09 produisent nos propres générations locales sous protocoles distincts. Voir [la provenance](research/existing-traces.md). Les réponses C08/C09, la première correction v3 et le test réservé à une erreur restent immuables.

Pour rejouer une génération complète, reprendre l'argv de son manifest en choisissant une destination neuve. C08 compare instruction seule/dossier sur 16 cas; C09 génère les 16 autres cas. C10 réutilise ces réponses pour les corrections, donc son zéro erreur ne constitue pas un nouveau test réservé. Les trois intégrations reproduisent exactement trois textes connus dans cette configuration. Aucun SDK quantique, accès matériel ou run QPU.

## Expériences SDK locales

C12 exécute Perceval 1.3.1 sur trois modes/deux photons; C13 exécute Pulser 1.7.2 et QuTiP 5.2.3 sur deux atomes. Les versions et commandes originales sont dans leurs manifestes. Le venv SDK Python 3.11 reste distinct du venv LLM Python 3.9; requirements-quantum-sdk.txt fixe l'installation Perceval observée, l'inventaire Pulser séparé est dans C13/environment.json.

~~~bash
.venv-quantum-sdk/bin/python -m quantage.sdk_photon --output /tmp/quantage-sdk-photon-neuf
/opt/homebrew/bin/python3.11 -m quantage.sdk_rydberg --output /tmp/quantage-sdk-rydberg-neuf
~~~

Destinations neuves requises. Ces commandes simulent localement et ne soumettent aucun QPU. La validation d'un constructeur Device est partielle; 101 ns peuvent être arrondis à 104 ns et des exigences backend restent distinctes. Les modèles locaux ignorés par Git occupent environ 4.4 Go de poids/fichiers; C14 a rencontré des NaN en float16 CPU et un coût prohibitif en bfloat16 dans la configuration mesurée. Les échecs restent disponibles, sans score comparatif inventé.
