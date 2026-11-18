# C19 — annotation indépendante des vingt intentions publiques

Les vingt textes ont été annotés depuis le seul fichier
`runs/20261115-c19-instruct-repair/test_cases.json`, SHA-256
`742301bb909289baaf1f34f328032851aa1ca8b935ede5b34e4081aa903d223b`.
Aucun autre fichier C19 n'a été ouvert avant gel : ni gold auteur,
générateur, provenance, protocole de test, template, prompt ou réponse.

Le résultat est `private_gold.review.json` dans ce même répertoire, au format
`{cases:[...]}` avec identifiant, split, langue, contraintes, familles et
justification. Le gel horodaté et son SHA-256 sont consignés dans
`research/c19-annotation-review-freeze.json` avant la comparaison par
l'intégrateur. Aucun gold auteur n'est consulté par le relecteur.

Les six familles sont extraites du texte. Une donnée de coût ne crée pas de
budget ; les absences restent `null` ou listes vides. Les clauses réciproques
explicitement énoncées dans `409b79d93348` et `70cc302cf8a4` sont conservées
comme deux implications, sans les confondre avec une implication unilatérale.
Les contraintes éventuellement contradictoires ne sont pas corrigées.

Il s'agit d'une lecture par un rôle LLM distinct, sans indépendance humaine
aveugle ou de modèle démontrée. Aucune inférence ni énumération d'oracle n'a
été exécutée avant ce gel. Le contrôle fini ultérieur attend la comparaison
et l'autorisation de l'intégrateur ; aucun résultat de faisabilité ou de
performance n'est revendiqué par cette annotation.

## Oracle autorisé après gel et comparaison des annotations

Après l'accord 20/20 annoncé par l'intégrateur et son autorisation explicite,
`research/c19-annotation-oracle.py` a énuméré les vingt cubes binaires depuis
les seuls publics et mes labels. Les domaines, tous les optima et les retraits
de familles sont dans `research/c19-annotation-oracle/raw.json`. Le manifest
v2 `research/c19-annotation-oracle/manifest.json` a le statut `completed` et sa
validation avec racine passe. Les labels figés n'ont pas été modifiés.

Trois cas sont infaisables : `8c55da367b52`, `409b79d93348` et
`70cc302cf8a4`. Chaque famille énoncée est active sur le domaine faisable,
vérifié par 86 retraits séparés ; les autres 17 cas sont faisables. Ce sont
des faits finis sur les instances présentes, pas une garantie paramétrique.

Une fois l'oracle indépendant figé, les seuls champs `author_check` ont été
comparés, dans le gold auteur autorisé. Les vingt domaines/comptes/optima et
les 86 comptes de retraits et masques témoins concordent. Le code auteur n'a
jamais été importé ou exécuté. Comparaison, environnement, commande et hashes
avant/après sont conservés dans
`research/c19-annotation-oracle/author-comparison.json`.

Commande enfant du calcul borné, Python 3.9.6, bibliothèque standard, entiers
exacts, six contrôles calculables à la main, sans aléa, limite 30 s :

```bash
python3 research/c19-annotation-oracle.py --output research/c19-annotation-oracle/raw.json
```

La commande complète du runner et le contrat sont conservés ; tout replay
exige une destination neuve. Aucun prompt, réponse ou protocole de test C19
n'a été ouvert pour cet oracle. Aucune inférence n'a été lancée par le
relecteur. Les références finies indépendantes sont prêtes avant test.
