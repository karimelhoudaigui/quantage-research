# C15 — correction du rendu Markdown vers TeX

Date : 2026-11-15. Périmètre : fonctions latex() et pre() de
scripts/build_paper.py, tests/test_manuscript_math.py et ce rapport.
Les modules C15 d'inférence, formulation, vérification, score et boucle restent
gelés. Aucun fichier paper/ n'a été écrit par cette intervention.

Les diagnostics de départ sont
[l'audit indépendant](c15-manuscript-audit.md) et
[l'erratum](c15-manuscript-erratum.md). Les cinq corps d'équations déjà réparés
restent des régressions obligatoires. Cette correction de conversion ne modifie
pas les formules scientifiques ni le contenu de TEMPLATE.

## Corrections

- Le découpage des cellules ignore les barres protégées par les dollars
  mathématiques ou par un délimiteur de code, y compris plusieurs backticks.
  Une barre échappée hors de ces spans reste un caractère de la cellule.
  Les normes $|x|$ et les extraits de code avec une barre ne créent donc pas
  de colonnes supplémentaires. Une arité de ligne incohérente ou un span
  mathématique/code non terminé produit une erreur explicite.
- Les tableaux utilisent longtable, avec colonnes de paragraphes, entêtes
  répétés et pieds de page. Ils ne sont pas enfermés dans un environnement
  center, un flottant ou une boîte tabularx empêchant leur pagination.
  L'alignement Markdown gauche/droite/centre est conservé. Pour n colonnes,
  chaque largeur vaut (linewidth - 2(n-1)tabcolsep)/n, en tenant compte des
  marges extérieures supprimées par les deux directives @{}.
- Les longs chemins et identifiants de code dans les cellules reçoivent des
  coupures TeX facultatives après des groupes de quatre caractères. Retirer
  ces commandes redonne le même littéral échappé; aucun caractère imprimé
  n'est ajouté ou supprimé.
- Le collecteur de displays conserve tous les caractères entre les deux
  délimiteurs $$, notamment les vrais LF, les antislashs, les accolades et
  les commandes de matrices. Il n'envoie pas les lignes intermédiaires vers
  l'échappement de prose. Un display non terminé ou du texte après sa
  fermeture produit une erreur. Les délimiteurs $$ hors d'un bloc sont
  également refusés, sauf quand ils sont du code littéral ou la frontière
  de deux expressions inline adjacentes. Ils ne sont plus échappés
  silencieusement comme de la prose.
- Le rejet des contrôles C0 précède toujours le découpage des lignes. Seuls
  tabulation et LF sont permis parmi les caractères de codes 0 à 31.

Le préambule pre(title), isolé du contenu scientifique, charge array et
longtable. Leurs rôles de colonnes programmables et de tableaux multipages
sont décrits dans les notices primaires
[array](https://ctan.org/pkg/array) et
[longtable](https://ctan.org/pkg/longtable). Il s'agit de source TeX générée;
aucune installation ou compilation LaTeX n'a été effectuée.

## Validation exécutée

Commande :

    python3 -B -m unittest discover -s tests -p test_manuscript_math.py -v

Sortie finale de validation : 13 tests, OK, 0.038 s. Les trois méthodes de test
préexistantes, portant notamment sur les cinq expressions TeX et le contrôle
C0, sont conservées. Les ajouts couvrent le corps multiligne exact, les
displays incomplets, tous les C0 interdits, les barres dans maths/code/texte
échappé, les délimiteurs de code multiples, les alignements, la largeur et
la structure d'un tableau de 120 lignes, les délimiteurs $$ dans la prose et
leur distinction avec du code ou des expressions inline adjacentes. Ce temps est celui des tests
logiciels locaux, pas une mesure de performance scientifique.

Le SHA-256 de la valeur de TEMPLATE, extrait par AST avant et après la
correction, est identique :

    f2e0e15f2cebc358b81d953961d5c0e37e1401eeee400ff5b6c140f8aba9d657

Extraction utilisée, sans exécuter main() ni reconstruire le manuscrit :

    import ast, hashlib
    from pathlib import Path
    tree = ast.parse(Path('scripts/build_paper.py').read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == 'TEMPLATE' for t in node.targets
        ):
            print(hashlib.sha256(ast.literal_eval(node.value).encode()).hexdigest())

Une sonde additionnelle a lu paper/article.md, appelé latex(source) en mémoire,
et comparé par expressions régulières tous les corps $$ du Markdown aux corps
\[ du TeX. Elle n'a écrit aucun fichier. Sortie brute :

    {"artifact":"paper/article.md read only","display_count":5,"display_bodies_exact":true,"longtables":3,"unsupported_c0":0,"paper_files_written":false}

La recherche locale par shutil.which a donné :

    {"pdflatex":null,"xelatex":null,"lualatex":null,"tectonic":null}

## Revue et limites

Relecture personnelle du code et des corps mathématiques selon
mathbox:proofread-math : aucun changement de jeton mathématique scientifique.
Une courte revue indépendante en lecture seule du renderer a été effectuée
par le sous-agent corpus, distinct de l'auteur du renderer. Elle confirme
l'arithmétique des largeurs et la structure longtable, et reproduit les douze
tests précédant le dernier correctif. Elle a trouvé le contre-exemple
"Avant $$x=1$$", auparavant altéré silencieusement. Le rejet explicite de
ce cas et le treizième test ont ensuite été vérifiés par l'auteur; cette
dernière modification n'a pas de seconde revue indépendante annoncée.
Aucune de ces vérifications ne remplace une compilation et une inspection
du PDF.

Les coupures de page de longtable ont lieu entre ses lignes : une ligne
unique plus haute qu'une page ne devient pas automatiquement sécable.
La source TeX doit encore être compilée et inspectée pour établir la mise
en page réelle, les dépassements éventuels et la disponibilité des paquets.
Le renderer vise le document article à une colonne; il ne fournit pas une
prise en charge générale de Markdown, des tables imbriquées ou des pages à
deux colonnes. Le relecteur a aussi reproduit une limite préexistante
d'inline() pour un dollar de devise échappé suivi de mathématiques inline;
cette fonction n'a pas été modifiée et cette syntaxe n'est pas validée par
ce travail. La fidélité d'un corps mathématique ne prouve pas la validité
scientifique de ce corps. Aucun PDF compilé n'est déclaré validé.
