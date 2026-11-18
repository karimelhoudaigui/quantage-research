# C15 — audit indépendant de la syntaxe du manuscrit

Question : les rendus `sum`, `qquad` et l'Hamiltonien tronqué proviennent-ils
du lecteur, du convertisseur ou de la source ? Réponse : les sources sont
objectivement corrompues. Le convertisseur amplifie cette corruption. Aucune
validation scientifique ni compilation PDF n'est revendiquée ici.

## Périmètre et provenance

Relecture indépendante du rôle intégrateur, en lecture seule pour
`scripts/build_paper.py`, `paper/article.md` et `paper/main.tex`. Compétence
appliquée : `mathbox:proofread-math`, mode review-only. Instructions lues :
AGENTS.md, README.md, agents/orchestrator.md, agents/verifier.md, état,
backlog, claims et résumés C13/C14. Aucun gold C15 ni générateur de corpus C15
n'a été lu pour cet audit. Aucun fichier `paper/` ou builder modifié.

L'inventaire d'octets, les empreintes SHA-256, les numéros de lignes LF,
l'environnement Python et la sonde de conversion sont conservés dans
`research/c15-manuscript-audit.raw.json`. Base Git observée :
`fee83eb4575198e3e142d41c621300b4d11361d8`, arbre non présenté comme propre.
Python 3.9.6, macOS arm64. Aucun `pdflatex`, `xelatex`, `lualatex` ou
`tectonic` disponible. Il s'agit d'une inspection locale et d'une reproduction
du convertisseur, pas d'un run LLM, SDK ou QPU, ni d'un nouvel échec de quota.

## Constats classés

1. **Altération des commandes et du sens typographique.** Le gabarit Python
   contient des caractères U+000C (form feed), octet hexadécimal `0c`, aux
   emplacements où le contexte impose `\frac`. Ils sont déjà présents dans
   le fichier source, même si `TEMPLATE` est actuellement une chaîne raw.
   Ajouter seulement un préfixe `r` ne réparerait donc pas ces octets.
   Occurrences dans le builder : lignes LF 137 (deux), 159 (une), 165 et 167
   (une chacune). Dans `article.md` : 36 (deux), 58, 64 et 66. Le dump brut
   précise chaque position d'octet. Aucun U+000D n'a été observé.

2. **Commandes privées de leur antislash.** Les displays de couverture,
   QUBO, probabilités bosoniques et Hamiltonien contiennent `sum`, `qquad`,
   `max`, `in`, `prod`, `Omega`, `iphi`, `deltasum`, `anglelangle`, au lieu
   des commandes TeX voulues. Le texte en ligne `$d_igeq1$` est également
   corrompu. Cela n'est pas détectable par un simple équilibre d'accolades.
   `R(t)` et ses commandes de matrice sont, elles, intacts dans le périmètre
   examiné.

3. **L'Hamiltonien est interrompu par de vrais sauts LF.** Dans le builder,
   les deux fragments `|r_j\nanglelangle` et `|g_j\nanglelangle` comprennent
   un saut de ligne, à l'emplacement compatible avec une ancienne
   interprétation de `\rangle` puis une normalisation des fins de ligne.
   L'historique exact de cette transformation n'est pas prouvé ; la
   corruption actuelle l'est. Restaurer seulement `sum` et `qquad` serait
   insuffisant.

4. **Le convertisseur perd le mode mathématique.** `latex()` appelle
   `markdown.splitlines()`, qui coupe également sur U+000C. Son traitement
   d'une équation `$$...$$` exige un début et une fin sur la même ligne.
   Les displays C, P et H passent alors dans `inline()`/`escape()` et
   deviennent des dollars, accolades et indices échappés. Le TeX actuel ne
   contient aucun U+000C, mais demeure corrompu. Le Markdown possède dix
   délimiteurs `$$` pour cinq displays ; le TeX ne possède que deux paires
   `\[`/`\]`, celles de Q et R, et six `\$\$` littéraux pour les trois
   displays perdus. La sonde read-only reproduit ce comportement sur C,
   puis conserve correctement l'équation lorsqu'on lui fournit la chaîne
   corrigée.

## Réparations typographiques proposées à l'intégrateur

Corriger d'abord le gabarit, puis reconstruire les deux manuscrits. Les
corrections de commandes suivantes sont forcées par le contexte local et les
définitions voisines ; elles ne proposent pas une nouvelle démonstration.

```latex
C=\frac{\sum_i A_i}{N},\qquad
R=\frac{\sum_i A_i L_i}{\sum_i A_i}.

Q(x)=-\sum_i w_i x_i+P\sum_{(i,j)\in E}x_i x_j,\qquad
P=1+\max_i w_i.

d_i\geq1

P(s|t)=\frac{|U_{i_1j_1}U_{i_2j_2}+U_{i_1j_2}U_{i_2j_1}|^2}
{\prod_k s_k!\prod_k t_k!}.

H=\frac{\Omega}{2}\sum_{j=0}^1
(e^{i\phi}|r_j\rangle\langle g_j|
+e^{-i\phi}|g_j\rangle\langle r_j|)
-\delta\sum_{j=0}^1 n_j+\frac{C_6}{r^6}n_0n_1.
```

Le passage des kets locaux à l'opérateur sur le produit tensoriel est implicite
dans la notation existante ; ce rapport ne modifie pas cette convention et
n'audite pas l'équivalence avec les implémentations SDK.

## Vérification proportionnée recommandée

- Rejeter tout contrôle C0 hors tabulation/LF dans le gabarit **et** dans le
  Markdown avant conversion. Cela détecte le défaut à sa source et évite que
  `splitlines()` le masque. Inclure un diagnostic avec fichier et position.
- Figer des attentes explicites pour chacun des cinq displays : équation C
  avec `\frac`, `\sum` et `\qquad` ; Q avec `\sum`, `\in`, `\max` ; P avec
  `\frac` et `\prod` ; H avec `\Omega`, `\sum`, `\phi`, `\rangle`,
  `\langle`, `\delta` ; matrice R inchangée. Contrôler aussi le fragment
  en ligne `d_i\geq1`. Une comparaison de chaînes attendues ou de jetons
  TeX serait utile, car `sum` et `max` peuvent compiler sans erreur tout en
  produisant des lettres mathématiques.
- Extraire les displays Markdown et les displays TeX et vérifier leur
  bijection et la conservation exacte des corps, sous une normalisation
  documentée des seuls espaces. Refuser `\$\$` dans ce manuscrit et les
  délimiteurs mathématiques orphelins. Pour les displays multilignes,
  utiliser un état explicite, ou rejeter clairement la syntaxe non supportée
  au lieu de l'échapper silencieusement.
- Reconstruire dans une destination temporaire ou comparer les sorties à
  celles attendues, puis vérifier Markdown/TeX synchronisés. Une compilation
  LaTeX et une inspection visuelle du PDF seront complémentaires lorsqu'un
  compilateur sera disponible ; elles ne remplacent pas les attentes sur
  les commandes mathématiques.

La vérification actuelle du dépôt ne couvre pas ces invariants : la recherche
de `build_paper`, `braces`, `qquad` et des commandes de somme dans
`scripts/check.py` et `tests/` n'a trouvé aucun contrôle correspondant.

## Commandes de reproduction

Inspection principale (sans reconstruire) :

```bash
python3 - <<'PY'
from pathlib import Path
for name in ('scripts/build_paper.py', 'paper/article.md', 'paper/main.tex'):
    data = Path(name).read_bytes()
    print(name, [(i, hex(b)) for i, b in enumerate(data)
                 if b < 32 and b not in (9, 10)])
    print('LF lines', [(i + 1, repr(s)) for i, s in
          enumerate(data.decode().split('\n'))
          if '$$' in s or r'\[' in s or 'd_igeq' in s])
PY
```

La sonde consignée dans le JSON charge uniquement les définitions
`escape`, `inline`, `latex` par AST avec leurs imports ; elle n'exécute ni
`main()` ni les écritures du builder. Son fragment corrompu commence par
`\$\$C=\nrac...`, tandis que le fragment corrigé commence par
`\[C=\frac{\sum_i A_i}{N},\qquad...`.

Statut : audit de diagnostic terminé ; correction et validation après
correction à intégrer. Aucun résultat de performance ou de généralisation
n'est ajouté par ce rapport.
