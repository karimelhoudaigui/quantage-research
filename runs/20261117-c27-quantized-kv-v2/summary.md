# C27 — résumé et interprétation

Date de clôture : 18 novembre 2026. Statut `complete` signifie que cette question de pilote a été exécutée et documentée; il ne signifie pas que l'hypothèse scientifique générale est confirmée.

## Question et priorité

C27 teste si une configuration locale Qwen3-8B-Q4_K_M, Flash Attention explicite et caches K/V `q8_0` permet un appel complet sur l'état de développement C24 après les échecs de ressources C24/C25. Cette question est prioritaire parce que la capacité locale conditionne une éventuelle étude C23, mais elle n'est pas le résultat principal de l'article.

## Protocole et sources

Le protocole C27 a autorisé un seul nouvel appel guidé sur le même cas de développement C24, avec l'état composé des réponses effectivement enregistrées. Aucun nouvel initial, retry, continuation ou gold n'a été transmis au modèle. Contexte 6144, plafond de sortie 1024, réserve fixe de sortie 1024 (entrée observée 1795/5119 maximum), batch/ubatch 128, placement GPU demandé 99 couches, quatre threads, Flash Attention `on`, K/V `q8_0`, requête 180 s et watchdog de groupe 480 s.

Sources d'exécution : `protocol.md`, `freeze-round2-v1.json`, `contract-guided-round2-v1.json`, `guided-round2-v1/manifest.json`, `guided-round2-v1/driver/generation.json` et `guided-round2-v1/driver/raw.jsonl`. Le manifeste donne le commit de départ `fee83eb4575198e3e142d41c621300b4d11361d8` et signale un arbre déjà modifié; aucune assertion de reproductibilité à partir d'un commit propre n'est faite.

## Résultats

- Une réponse complète a été reçue : 143 tokens jusqu'à EOS, sur 1795 tokens d'entrée. Le runtime a rapporté Metal, 37/37 couches déchargées, Flash Attention activé et K/V `q8_0`. Cela établit un appel complet dans cette exécution, pas une marge mémoire, un débit garanti ou une exécution exclusivement GPU.
- Le préremplissage a pris 131,227 s (13,68 tokens/s), la génération 10,844 s (13,10 tokens/s); `wall_seconds` du driver vaut 188,489 s et le chargement 40,794 s. Mesures d'un seul appel, non comparatives.
- Le processus serveur a été répertorié comme reap; son statut de sortie est `-9`. `error` et `cleanup_error` sont nuls dans les métadonnées. Le statut de sortie inhabituel est conservé, pas requalifié en arrêt normal.
- Le replay indépendant du scorer rejoue littéralement la lignée C19 → C22 → C24 → C27. Avant C27, le modèle a un désaccord de faisabilité sur 1 des 16 affectations (`[1,1,0,0]`). Après le patch C27, les 16 affectations ont zéro désaccord de faisabilité et d'objectif. Ce résultat porte uniquement sur ce cas fini et son annotation.
- DFS exhaustif et SciPy HiGHS ont tous deux retourné `optimal`, objectif 78 et solution `[1,1,0,0]`. La sélection a choisi DFS après exécution des deux solveurs; ce profilage ex post n'est pas un routeur appris.
- Aucun effet causal du cache `q8_0`, aucune généralisation, aucune performance sur C23 et aucun résultat QPU ne sont établis.

L'audit est reproductible avec :

```text
python scripts/audit_c27.py
```

Il écrit `verification.json`, dont les sources et entrées sont hashées. Environnement d'audit : Python 3.11.15, macOS 26.2 arm64, SciPy 1.17.1. L'audit ne lance ni modèle ni requête réseau. Les tests ciblés exécutés sont `python -m unittest discover -s tests -p 'test_repair_second_round_q8.py' -v` (2 tests) et `python -m unittest discover -s tests -p 'test_repair_study_c23.py' -v` (5 tests); ils valident le logiciel, pas la performance du modèle.

## Article et portée

Le manuscrit garde C19 comme évaluation principale et ses dénominateurs inchangés. Une note posthoc C27 et une citation sur l'antériorité des portefeuilles de solveurs sont ajoutées au template générateur et au manuscrit généré, avec leur portée et leurs limites. Le PDF issu de cette version est dans `../../paper/build-c27-v1/main.pdf`; la compilation locale avec Tectonic a réussi avec un avertissement de mise en page non bloquant. La revue ciblée de nouveauté est enregistrée dans `literature-review.md`; la revue matérielle dans `hardware-review.md`.

## Suite et blocage

C23 n'a pas reçu d'appel modèle. Son prérequis protocolaire exigeait une proposition complète C25 sous la configuration à placement partiel et cache antérieur; C25 n'en a pas fourni. C27 a généré avec 99 couches demandées et cache `q8_0`, configuration différente, donc ne satisfait pas ce prérequis. Ne pas lancer C23 sans soit respecter le gate initial (qui demeure bloqué), soit obtenir une décision explicite et un amendement prospectif documenté. La nouveauté et la maturité de soumission de l'article restent non établies.
