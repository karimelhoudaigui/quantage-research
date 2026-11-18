# C23 — oracle indépendant après annotation publique figée

Les vingt labels publics sont restés inchangés après leur gel : SHA-256
`d874ff3b11a15d817a38a3c32698351a08512b80e8b3f11341fd7a7a9165f002`.
La comparaison de contrats 20/20 a été effectuée par l'intégrateur avant
qu'il autorise ce calcul et la lecture ultérieure des certificats auteur.
L'ordre d'indépendance est conservé : textes seuls, gel des labels, oracle
propre figé, puis seulement comparaison des masques de l'auteur.

`research/c23-annotation-oracle.py` utilise des ensembles de choix, des sommes
entières et une énumération complète de `{0,1}^n`, sans importer de code de
production ou d'auteur. Le coefficient du bit `i` signifie l'inclusion de
l'option `i`. Les deux clauses réciproques d'une paire et les trois arcs
d'un cycle restent séparés. Six contrôles calculables à la main couvrent le
sens d'une implication, les coûts distincts des poids, l'indexation,
l'exclusion, la contradiction de cardinalités et les optima ex æquo.

Résultats finis :

- Les vingt domaines sont non vides ; tous les optima et leurs poids sont
  conservés par cas.
- Les 80 retraits de familles présentes, incluant la famille d'exclusions
  E, agrandissent chacun le domaine.
- Chacune des 60 implications énoncées est individuellement essentielle :
  retirer uniquement cet arc sous les autres contraintes ajoute un masque.
- Chacune des 32 exclusions individuelles est également active.

Les domaines complets et tous les masques ajoutés, pas seulement les comptes,
figurent dans `research/c23-annotation-oracle.output/raw.json`, figé au SHA-256
`8f000b0f298b72d65d2e2f4f47afa9bb4f2cb916bf0d7abe61ea7eaf90f42c2e`
avant lecture auteur. Le manifest v2 du même répertoire est `completed` et
sa validation avec racine passe. Python 3.9.6, bibliothèque standard,
arithmétique exacte, sans aléa, limite 30 s et thread conventionnel 1.
Commande enfant :

```bash
python3 research/c23-annotation-oracle.py --output research/c23-annotation-oracle.output/raw.json
```

Le contrat et la commande complète du runner sont conservés. Toute
reproduction exige une nouvelle destination, sans écraser ces preuves.

Après ce gel, les `author_certificate` autorisés ont été comparés par ID,
famille et paire de clause. Les vingt domaines/comptes/optima, les 80
retraits de familles, les 60 retraits d'implications et les 32 retraits
d'exclusions concordent exactement, y compris les listes de masques ajoutés
et leurs témoins minimaux. L'ordre différent des implications dans le gold
auteur n'affecte pas cette comparaison par paire. Le fichier
`author-crosscheck.private.json` annonce aussi ces propriétés, mais reste
explicitement une auto-vérification de l'auteur.

La comparaison, ses hashes avant/après, l'environnement et sa commande sont
consignés dans `research/c23-annotation-review.json`. Aucun modèle, serveur,
appel LLM, donnée nouvelle ou fichier scientifique d'intégration n'a été
modifié. Aucun contrôleur n'a complété des clauses pour l'inférence.
L'activité vérifiée est propre à ces instances finies ; elle ne prouve ni
un sens universel du texte libre, ni une performance d'agent, ni une garantie
de population. Les références sont prêtes pour une revue prospective du
code puis pour l'audit des observations réelles.

## Revue statique initiale du code prospectif

Le driver `repair_scale_full_inference.py` et le scorer `repair_study_c23.py`
ont ensuite été relus, avec leurs différences par rapport aux drivers
précédents et leurs dépendances de patch/feedback. Les sources et SHA sont
consignés dans la section prospective du JSON. Aucun défaut bloquant n'est
identifié par cette lecture ; les fixtures n'ont pas été exécutées par le
relecteur et ce verdict n'est pas une validation de runtime.

Le driver complet limite les phases à initial/direct, refuse toute entrée
d'historique ou de feedback et conserve le garde-fou natif de préfixe
assistant vide fermé. Sa grammaire linéaire est bornée et indépendante des
instances. Le scorer rejoue les éditions atomiques sur le texte initial
exact et vérifie son hash. Il compare le message guidé au feedback calculé
sur les véritables lignes de ce candidat, exige le même système pour auto
et guidée et le même prompt pour initial/direct. Les choix restent fondés
sur schéma/moyenne de log-probabilité, sans sélection par le certificat
final de référence. Moyenne non finie, seed ou compte incorrects sont rejetés.

Les caps sont 1024 nouveaux tokens et 3071 tokens d'entrée, avec réserve
totale de 4096. Les patches portent diagnostic libre et éditions littérales,
tandis que le bras direct émet une formulation complète : la comparaison
primaire annoncée est donc guidée contre auto au même format patch ; le
direct complet reste secondaire. Le plan physique est quatre appels par
cas et six attribués aux trois bras. Les diagnostics, matérialisations,
échecs, temps de replay et solveurs candidats sont conservés séparément.

Le H23 visible dans le code reste une proposition à figer avant test, avec
les wrappers, instructions, seeds et hashes réels. Les contrôles logiciels
restants et l'audit des données effectivement observées sont encore à
effectuer ; aucun appel de modèle ou nouveau corpus n'est produit ici.
