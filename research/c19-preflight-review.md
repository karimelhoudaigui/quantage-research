# C19 — revue préalable du langage et du comparatif

15 novembre 2026. Verdict : **cohérent dans le domaine borné annoncé, sous les
conditions de provenance et d'exécution ci-dessous; aucun défaut bloquant
subsistant identifié par cette revue**. Aucun test C19, brut de test, modèle ou
serveur n'a été exécuté ou consulté. Les sources actuelles et le protocole ont
été lus; les seuls calculs exécutés sont des sondes logicielles synthétiques.

Artefacts : c19-preflight-review.json et scripts/audit_c19_preflight.py.
Le JSON conserve les empreintes exactes des cinq sources auditées, l'environnement,
les assertions et leurs limites. Le rôle relecteur est distinct de l'auteur
du driver/scorer, mais il est l'auteur historique du compilateur repair_language.py
et des solveurs : la partie compilateur est une auto-relecture, pas une
nouvelle revue indépendante. L'auteur du corpus C19/relecteur des annotations
reste une responsabilité distincte.

## Formulation réellement produite

FORM_GRAMMAR est une constante indépendante de n, weights, costs, edges et du
gold. Elle fixe ordre des champs, types, indices possibles 0..7, entiers
génériques ≤10000, au plus huit valeurs par vecteur, 32 lignes et 32 termes par
expression. Elle ne fournit aucune valeur numérique d'instance, aucune arête,
aucune relation ou borne cible, aucun nombre correct de lignes. Les longueurs
de variables/objectifs restent libres; des propositions invalides ou fausses
restent donc possibles. Cette aide de langage doit être déclarée séparément
de la compréhension et de la fidélité.

Les six familles ont une dérivation explicite dans ce langage : budget
sum c_i*x_i<=B, cardinalité sum x_i>=L et sum x_i<=U, obligation x_i==1,
interdiction x_i==0, implication x_i-x_j<=0. L'exclusion de base s'écrit
x_i+x_j<=1. Cette représentabilité vaut pour n≤8 et les coefficients/bornes
du contrat; elle ne couvre pas tous les programmes linéaires arbitraires.
Le corpus prévu n≤7 reste dans ce domaine.

Le compilateur ne lit que le modèle écrit : AST d'addition/soustraction et
produit par constante, déplacement exact des termes, validation entière.
Il ne complète ni ne répare de clause, conserve authored_model et ne lit aucun
oracle. Le vérificateur compare ensuite faisabilité et objectif sur tout le
cube binaire, y compris points infaisables. Le feedback est un objet fermé
contenant au plus trois affectations témoins; aucun modèle corrigé n'y passe.
La référence annotée reste un oracle de confiance, pas un certificat général
du sens d'une phrase libre.

## Driver et sélection

Pas d'argument gold dans le driver. Les requêtes publiques sont filtrées;
direct n'accepte pas d'initiale, auto ne lit pas le feedback et guidé ne reçoit
que le feedback validé. Le template est celui du GGUF épinglé via
/apply-template avec enable_thinking=false; aucune génération cachée de
raisonnement n'est ajoutée. L'original est un modèle instruct Qwen; le GGUF
communautaire bartowski, sa quantification et son commit sont distincts et
conservés dans les métadonnées d'acquisition.

La réception contrôle IDs choisis, probabilités positives finies, compte de
tokens, paramètres effectifs, absence de contexte tronqué, arrêts EOS/limite,
réserve complète 512+1 dans 4096 et API spéculative désactivée. Le champ
speculative.types accepte déjà chaîne ou liste : la régression C16 potentielle
n'est plus présente. Les probabilités sont bien celles du jeton choisi,
et non un remplacement par la probabilité top-1.

L'API native sérialise ces valeurs et peut employer une acceptation puis un
rééchantillonnage dépendant de la grammaire. Le libellé actuel décrit donc
correctement une moyenne des probabilités traitées rapportées par l'API,
heuristique de sélection; il ne promet pas une vraisemblance conditionnelle
normalisée après grammaire.
[Sérialisation b12359](https://github.com/ggml-org/llama.cpp/blob/b12359/tools/server/server-task.cpp),
[échantillonnage b12359](https://github.com/ggml-org/llama.cpp/blob/b12359/common/sampling.cpp).

Direct choisit validité de schéma, puis moyenne, égalité à la première réponse;
auto/guidé choisissent la seconde valide sinon l'initiale valide. Aucun de ces
choix ne consulte le certificat final, l'optimum ou le gold. Le scorer C19
utilise H19, gain minimal quatre et au plus une régression, 512 tokens/appel,
4096 de contexte; le protocole doit fixer les 20 cas avant test.

Metal MTL0/99 couches est demandé et les journaux doivent confirmer un buffer
Metal positif et des couches effectivement déportées. Le driver borne la
complétion par timer mural, la phase par 1650 secondes, conserve les lignes
achevées et exige le watchdog de groupe externe à 1800 secondes. Le cleanup
cible son Popen; ses erreurs rendent désormais le manifest partial_error.
Le client désactive proxies/redirections et ne contacte que son adresse
127.0.0.1; le serveur est offline, avec environnement réduit. Ces propriétés
statiques ne sont pas une inspection des paquets ou une preuve d'utilisation
exclusive du GPU.

Les hashes du binaire, des fichiers runtime listés dont les dylibs et du GGUF
sont contrôlés avant démarrage. L'acquisition figée est l'ancre de confiance;
elle ne s'authentifie pas elle-même si son contenu était remplacé. L'ownership
du port demeure conditionnel à l'absence de course entre port éphémère libéré
et bind serveur; le processus tué/rejoint est, lui, bien celui créé par le driver.

## Régressions concrètes trouvées et état

Deux faiblesses du scorer ont été signalées avant test et corrigées par
l'intégrateur :

- La comparaison abs(moyenne-calculée − moyenne-stockée)>tol laissait passer
  NaN. Le type et math.isfinite de la moyenne stockée sont désormais contrôlés.
- input_tokens≤4096 ne vérifiait pas la réserve pour 512+1 tokens.
  Le contrôle actuel exige un entier strictement positif ≤3583.

Le script reproduit le refus de NaN/inf, de 3584 tokens d'entrée et d'un
booléen, sans modifier une source historique. La comparaison des bras a aussi
été vérifiée avec des candidats synthétiques, sans référence.

Limite conservée : SCHEMA_MESSAGE historique demande encore des « integer
rows », formulation ambiguë lorsque la grammaire impose des chaînes. La
consigne C19 et le langage explicite précisent ces chaînes; aucun module
historique n'a été corrigé rétroactivement. Cette incohérence de vocabulaire
reste déclarée, plutôt que présentée comme une garantie de compréhension.

## Vérification bornée et coûts

Commande : python3 -B scripts/audit_c19_preflight.py

Sortie : 15 contrôles passés, zéro modèle exécuté, zéro requête réseau, zéro
brut de test C19 lu. Les sept primitives ci-dessus sont contrôlées sur les
128 affectations de sondes n=7, avec prédicats arithmétiques distincts.
Les expressions ont des dérivations manuelles dans GBNF; aucun validateur
GBNF natif n'a été invoqué. Ce résultat ne mesure pas le taux de conformité,
la fidélité ou la performance du LLM.

Les coûts par ligne sont ceux du client HTTP et de la requête de complétion,
pas tout le CPU du moteur. Le scorer conserve aussi coût serveur, chargement
et wrapper par phase, calcul des témoins et coût total des deux solveurs.
Énergie GPU, annotations, développement et session restent inconnus. Deux
appels et un plafond de sortie égal n'impliquent pas des coûts effectifs égaux.
Le portfolio est un profilage ex post; son temps sélectionné ne remplace pas
le coût des deux exécutions.

L'adaptation nouvelle quantage/repair_loop_linear.py est écrite, sans modifier
repair_loop.py. Elle exige une initiale enregistrée, en vérifie le texte,
les messages publics, les instructions, la phase initiale et les tokens, puis
la copie sans changer sa source. Elle préserve language, emploie sys.executable
et le driver/serveur/GGUF/acquisition C19 fixes, sans argument gold vers
l'inférence. Au plus une réparation guidée de 512 tokens est possible; une
initiale déjà fidèle provoque zéro appel supplémentaire. Le dossier de sortie
doit être neuf et --execute explicite, sous watchdog de groupe externe.

Le contrôle logiciel de cette adaptation a employé une initiale synthétique
infidèle sur exclusions+budget+cardinalité, un unique générateur de contrôle
retournant une réparation correcte et les deux solveurs classiques réels.
Il confirme un appel guidé, la conservation de la source et de la langue,
puis zéro appel si l'initiale est déjà fidèle. Zéro modèle GPU a été exécuté.
Le JSON sépare ces assertions sous new_controller_self_check et conserve
l'empreinte du nouveau module. Il s'agit d'une **auto-vérification d'auteur**,
sans revue indépendante de cette adaptation, et non d'une performance LLM.
La démonstration réelle sur développement demandée par l'intégrateur reste
à exécuter par lui; elle est distincte du test scientifique C19.
