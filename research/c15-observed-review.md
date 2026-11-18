# C15 — revue indépendante finale des observations et du blocage

## Conclusion

C15 doit rester **blocked pour sa comparaison H15**, sans score comparatif
inventé. Les observations finales sont 16 réponses de développement et
**une réponse initiale réservée, avec 15 cas absents**. Aucune phase directe,
auto ou guidée réservée n'a été exécutée. Les absents ne sont ni des refus,
ni des erreurs de format, ni des observations de fidélité.

L'inspection avant arrêt comptait zéro réponse ; le JSONL final contient
une ligne complète. Le dernier flush doit être pris en compte. Le relevé
original d'inspection n'est pas modifié ; il doit être accompagné de la
réconciliation après arrêt. L'audit a détecté cette différence en vérifiant
le contenu et le SHA-256 du résultat final, plutôt qu'en reprenant le seul
compte annoncé avant SIGTERM.

## Indépendance et méthode

Les références sont les annotations indépendantes figées et leurs domaines
finis, conservés avant génération. Aucun gold auteur, générateur de corpus
ou fichier de provenance privé n'a été ouvert. Aucun modèle n'a été chargé
ou exécuté par cet audit. Le tokenizer rapide a seulement redécodé et
recompté les textes déjà observés.

Le script `research/c15-observed-audit-v2.py` n'importe ni le scorer ni les
solveurs QuantAge. Il contrôle indépendamment les formes effectivement
observées et énumère le modèle admis sur son cube binaire. Ses résultats
figurent dans `research/c15-observed-audit-v2/raw.json`, avec contrat et
manifest v2 du même nom de répertoire. Statut `completed`, validation avec
racine passée, empreintes avant/après inchangées. Python 3.9.6 et tokenizers
0.20.3, limite 30 s, thread conventionnel 1, sans aléa.

Commande enfant, sans inférence :

```bash
.venv-local-llm/bin/python research/c15-observed-audit-v2.py --output research/c15-observed-audit-v2/raw.json
```

La commande complète du runner et les 24 entrées sont dans le manifest. Le
premier contrôle `research/c15-observed-audit/` est conservé comme échec du
script d'audit : il exigeait l'option CLI explicite `--max-new-tokens`, alors
que le premier run utilisait sa valeur par défaut 384. La version v2 accepte
l'absence de ce flag, tout en vérifiant les métadonnées et chaque compte
réel. Il ne s'agit ni d'un nouveau run LLM, ni d'une correction des données.

## Contrôles de traces et de confidentialité

Les 17 réponses sauvegardées ont chacune : une seed conforme à la règle
SHA-256 de l'ID, le bon texte et les bonnes données publiques, les
instructions de leur version, exactement deux messages système/utilisateur,
un hash de prompt reconstruit et un compte d'entrée retrouvé par tokenisation.
Les IDs de tokens redécodent exactement la réponse brute. Les
log-probabilités individuelles et leur moyenne sont finies et concordantes.
EOS correspond à un ID de fin du checkpoint ; les sorties à limite ont
exactement 384 tokens. Toutes les entrées observées respectent 4096 tokens
et toutes les sorties 384. Aucun champ de référence ou feedback n'apparaît
dans ces prompts initiaux, et aucun argument `--gold`, `--feedback` ou
`--initial` n'est passé à leurs commandes d'inférence.

Les métadonnées de développement déclarent le checkpoint
Qwen2.5-0.5B-Instruct, révision
`7ae557604adf67be50417f59c2c2f167def9a775`, Python 3.9.6, torch 2.8.0,
Transformers 4.45.2, float32 CPU, quatre threads, température 0.2, top-k 50,
top-p 1. Les hashes de toutes les sorties déclarées des trois processus
concordent avec les manifestes ; leurs entrées historiques inspectées
concordent aussi avec les sources présentes. La lecture des fichiers de
gold auteur reste exclue du contrôle indépendant.

La moyenne de log-probabilité reste celle des tokens choisis après les
processeurs de sampling, EOS inclus, sans interprétation comme probabilité
de justesse. Aucune sélection best-of-two ne peut être évaluée puisque ses
secondes propositions réservées sont absentes.

## Développement : faits finis, pas comparaison réservée

| Trace | Réponses | Schéma admis | Fidèles | EOS / limite |
|---|---:|---:|---:|---:|
| Développement v1 | 8 | 0 | 0 | 7 / 1 |
| Développement v2 | 8 | 1 | 0 | 8 / 0 |

Les sept propositions v2 rejetées contiennent notamment des structures de
lignes que le frontend n'admet pas. Aucun regroupement de chaînes n'est
aplati et aucune clause n'est réparée automatiquement. La sortie v2 admise
`31d8b6f0` est enveloppée dans une unique fence JSON, retirée et signalée par
la normalisation documentée. Elle contient quatre inégalités de paires avec
des bornes qui les rendent toutes inactives sur le cube binaire.

L'énumération indépendante trouve 32 affectations faisables dans le modèle
proposé, contre neuf dans la référence. Les 23 autres affectations sont des
désaccords de faisabilité ; les valeurs de l'objectif sont correctes sur
les 32 affectations. Il s'agit de 23 affectations d'un seul problème, pas de
23 requêtes ou essais indépendants. Le vecteur nul est déjà un témoin : le
modèle l'admet alors que le texte exige au moins deux projets.

L'optimum du candidat vaut 31 et sélectionne les cinq objets. L'optimum
indépendant de référence vaut 17. Les deux solveurs enregistrés retrouvent
31 et sont donc concordants sur le modèle faux ; le scorer refuse bien le
marqueur `usable_for_original_problem`. Les scores de développement
`23 F / 0 objectif / 32 affectations comparées` sont reproduits. Les sept
échecs de schéma ne comptent pas comme zéro désaccord mathématique prouvé.

Le feedback de développement est vérifié exactement : sept messages de
schéma constants et trois témoins lexicographiques pour le seul modèle
admis. Aucun modèle corrigé, nom de clause, paramètre de référence ou compte
complet n'est transmis dans `minimal.json`. Les métriques restent
`development_only`. La consultation de v1 a motivé v2 ; aucune amélioration
causale ou performance réservée entre ces versions ne peut être revendiquée.

## Test interrompu : une observation, pas une matrice

Le run `test-initial-v2` a le statut runner `failed`, sortie `-15` après
519.331055 s, sous une limite externe de 1800 s. C'est l'arrêt opérateur par
SIGTERM pour ressources décrit dans les traces, pas un timeout automatique
atteint ni une réfutation de H15. `generation.json` manque réellement et
n'est pas synthétisé après coup.

Le résultat final contient `1c94d7a6` : 565 tokens d'entrée, 203 de sortie,
EOS, 483.21496775 s de temps de requête enregistré. La proposition est non
conforme au schéma : des lignes sont des listes de plusieurs chaînes au
lieu d'une comparaison par ligne ou d'une ligne dense. Elle n'a pas de
certificat de faisabilité/objectifs, et aucun score de cube ne lui est
attribué. Les 15 autres cas initiaux sont absents. Les secondes phases et
leurs métriques comparatives sont absentes également.

Le relevé `test-initial-resource-stop.json` rapporte zéro observation au
moment de l'inspection préalable. Le fichier final et son hash de manifest
établissent une observation flushée avant la fin du processus ; l'ordre
détaillé des opérations d'inspection/flush/signal n'est pas enregistré à la
ligne près. Cette course justifie le compte final 1/15, sans réécrire la
première observation du relevé.

Le snapshot `vm_stat` montre l'état de compression mémoire de l'hôte. Ses
compteurs cumulatifs ne sont pas des deltas de ce processus, une mesure
d'énergie ou une expérience isolant la cause du ralentissement. Les valeurs
instantanées RSS/CPU évoquées par l'opérateur ne sont pas reprises comme
mesures indépendamment vérifiées dans ce rapport faute de sortie brute
correspondante parmi ces fichiers.

## Coûts et provenance temporelle

| Phase | Tokens entrée / sortie achevés | Temps des lignes (s) | Temps wrapper (s) |
|---|---:|---:|---:|
| Développement v1 | 4717 / 1468 | 576.578 | 594.621 |
| Développement v2 | 4517 / 1108 | 313.936 | 330.799 |
| Test initial partiel | 565 / 203 | 483.215 | 519.331 |

Les temps de lignes et de wrapper se recouvrent et ne s'additionnent pas.
Le travail éventuellement engagé après le premier flush et avant l'arrêt
n'a aucun compte de tokens final : il n'est pas mis à zéro. Le temps total
de session, l'énergie, le coût d'annotation et l'historique complet ne sont
pas déduits de cette table.

Une anomalie d'horodatage v1 reste ouverte : `started_at` plus la durée
monotone du wrapper mène vers 21:02:34 UTC, tandis que le JSON de génération
porte 22:54:13 UTC, soit environ 6698.924 s de décalage. Les hashes de ces
artefacts concordent ; aucune cause de la discordance n'est établie.
L'audit conserve les durées monotones rapportées mais ne reconstruit pas
une chronologie complète de session à partir de ces UTC.

## Suite et statut recommandé

Conserver C15 blocked, H15 non résolue, les deux développements, le run
initial failed, ses fichiers manquants et la réconciliation du flush final.
Aucune nouvelle tentative C15 n'est exécutée par cette revue. Une étude de
runtime différente doit avoir son propre protocole et sa propre provenance.
Les données déjà consultées ne doivent pas être présentées à nouveau comme
un test inédit si une méthode y est adaptée ; l'intégrateur annonce un
corpus entièrement nouveau pour C16.

La correction mathématique du manuscrit et les audits logiciels antérieurs
restent décrits dans leurs rapports propres. Ils ne remplacent pas la
comparaison d'agents manquante. Aucun QPU, avantage quantique, publication,
push, dépense externe ou lecture de secret n'est effectué par cet audit.
