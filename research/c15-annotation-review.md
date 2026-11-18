# C15 — annotations indépendantes gelées et oracle fini

## Contrat et indépendance

Les 8 textes publics de développement et les 16 textes publics réservés sont
annotés depuis leur seule `intention`. Tous décrivent des variables binaires,
la maximisation du poids sélectionné et les exclusions `edges`. Les champs
`costs` n'imposent aucun budget en l'absence d'une clause textuelle. Les
implications sont dirigées et ne sont pas remplacées par leurs conséquences.
Les contraintes absentes sont `null` ou des listes vides.

`runs/20261114-c15-formulation-repair/private_gold.review.json` contient une
ligne par identifiant : `id`, `split`, `language`, `constraints`, `rationale`.
Le gel horodaté est dans `research/c15-annotation-review-freeze.json` ; le
SHA-256 du gold de revue est
`1bb31ff6323f79987c2d53a541b0738a625e56019475b02095169bcb8bfaa4e2`.
Il a été écrit avant toute comparaison à l'auteur.

Au moment du gel et du présent calcul, le relecteur n'a ouvert ni
`private_gold.author.json`, ni `build_corpus.py`, ni `corpus-provenance.md`.
Il n'a pas lu/importé le futur solveur ou le futur scorer de production.
Le rôle est distinct ; une indépendance de modèle ou d'annotation humaine
aveugle n'est pas établie. Les prompts publics restent des données, et
aucune inférence LLM n'a été exécutée par cet audit.

## Calcul exact autorisé

Question finie : quels sous-ensembles binaires satisfont les clauses extraites
par le relecteur, et lesquels maximisent le poids entier ?

Le script `research/c15-annotation-oracle.py` n'importe aucun module QuantAge.
Il parcourt `itertools.product((0,1), repeat=n)`, avec le bit d'indice `i`
signifiant l'inclusion de l'objet `i`. Il contrôle directement chaque clause
avec des ensembles et des sommes entières. Six contrôles calculables à la
main couvrent l'indexation, coûts distincts des poids, sens d'une implication,
exclusion, cardinalités contradictoires et optima ex æquo.

Le contrat est `research/c15-annotation-oracle.contract.json` et le résultat
brut `research/c15-annotation-oracle/raw.json`. Le manifest v2
`research/c15-annotation-oracle/manifest.json` a le statut `completed` ; sa
validation avec racine de projet passe. Il conserve la commande, le commit,
l'arbre modifié, les empreintes avant/après, Python 3.9.6 et les sorties
hashées. Le temps limite est 30 s et le nombre de threads conventionnel 1.
L'exhaustion couvre chaque masque des 24 cas à 4–7 variables ; aucune
exécution n'est tronquée ni imputée.

Commandes :

```bash
python3 /Users/karimelhoudaigui/.codex/plugins/cache/openai-curated-remote/mathbox/4.0.0/skills/computation-audit/scripts/run_experiment.py \
  --root /Users/karimelhoudaigui/Downloads/quantage-research \
  --contract research/c15-annotation-oracle.contract.json \
  --input research/c15-annotation-oracle.py \
  --input runs/20261114-c15-formulation-repair/dev_cases.json \
  --input runs/20261114-c15-formulation-repair/test_cases.json \
  --input runs/20261114-c15-formulation-repair/private_gold.review.json \
  --output research/c15-annotation-oracle \
  --result research/c15-annotation-oracle/raw.json \
  --timeout 30 --max-output-bytes 1048576 --max-threads 1 \
  -- python3 research/c15-annotation-oracle.py \
  --output research/c15-annotation-oracle/raw.json
```

La destination existante est immuable ; tout replay exige un répertoire
nouveau et l'adaptation des deux arguments `--output` et de `--result`.

## Résultat et interprétation

Les domaines et tous les optima sont enregistrés par cas. Les trois cas
infaisables sont réservés :

- `6e3a08f5` : 0 obligatoire impose 2 ; leurs coûts 5+4 dépassent déjà 7.
- `a063c8f2` : 0 obligatoire exclut 1, 2 et 4 ; 3 et 5 sont interdits. Seuls
  0 et 6 peuvent rester, alors qu'au moins 3 entrées sont exigées.
- `ce1964a7` : 1 obligatoire impose 3, qui impose 4 ; 4 est interdit.

Ces contradictions ont une lecture directe et ne sont pas des erreurs de
format. Les autres 21 domaines sont non vides. Les optima sont des résultats
exacts dans les domaines finis annotés, pas des scores d'agent ni une garantie
sur des textes arbitraires. Le calcul ne certifie pas à lui seul l'extraction
sémantique : celle-ci repose sur la lecture séparée des 24 intentions.

Statut : annotations et calcul fini terminés ; comparaison à l'auteur et
audit des générations à effectuer par la suite, sans modifier le gold figé.
