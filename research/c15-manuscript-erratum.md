# Rectification du générateur de manuscrit — C15

La dégradation signalée était présente dans le gabarit Python et propagée au
Markdown/LaTeX. Cinq form feeds remplaçaient des antislashs de fraction; des
commandes de somme, produit, kets et espaces mathématiques étaient également
corrompues. Les contrôles de structure C11–C14 ne détectaient pas cette erreur.
Leur conclusion sur la validité des sources du manuscrit était insuffisante;
elle ne remet pas en cause les données brutes ou manifestes expérimentaux.

Le diagnostic indépendant est conservé dans c15-manuscript-audit.md/.raw.json.
Les sources corrompues et leur générateur sont copiés sans modification dans
paper/archive/c11-c14-before-c15-* avec empreintes. Le gabarit restaure les
cinq expressions données par les définitions et la revue indépendante, ainsi
que d_i\geq1. Aucun signe/coefficient physique n'est changé par cette réparation.

La conversion rejette désormais les contrôles C0 avant découpage des lignes.
Les tests vérifient les opérateurs attendus et la conservation des cinq corps
mathématiques, au-delà de l'équilibrage de braces. Une compilation et une
inspection visuelle restent distinctes; aucun PDF compilé n'est inventé.
