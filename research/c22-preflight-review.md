# C22 — revue prospective indépendante du préflight 8B

Statut : **pas de défaut bloquant restant pour les deux probes de
développement prévues**, sous le runner de groupe de processus de 480 s et
avec exactement les deux cas publics fixés. Aucun modèle, serveur, tokenizer,
téléchargement ou nettoyage n'a été exécuté par le relecteur. Les seules
écritures sont ce rapport et son JSON compagnon.

## Sources et contrôle prospectif

Relus : `repair_patch_scale_inference.py`, son diff avec le driver C21,
le protocole C22, `research/c22-model-candidate.md`, l'acquisition enregistrée,
le parseur de patches et le feedback d'évaluation du candidat. Le JSON
`research/c22-preflight-review.json` conserve date, périmètre, SHA-256 des
neuf sources et résultats des contrôles. Le driver finalement relu porte
SHA-256 `ae99264343b27391d1d6201541abcb9a52ea55e86eb464ae934b9dc57c87e523`.

Le document candidat est une note antérieure portant sur les métadonnées.
L'acquisition locale actuelle est `completed` et rapporte le fichier officiel
`Qwen3-8B-Q4_K_M.gguf`, commit
`7c41481f57cb95916b40956ab2f0b139b296d974`, 5 027 783 488 octets, SHA-256
attendu et observé
`d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785`.
Le relecteur n'a pas relu les cinq gigaoctets ; le driver vérifie les octets
complets et le runtime acquis avant le serveur. Le tag b12359 et le commit
runtime sont enregistrés dans le JSON. Aucun fit en mémoire n'en découle.

## Garde-fou non-thinking

Le serveur reçoit `--jinja` et `--chat-template-kwargs
{"enable_thinking":false}`. Avant chaque `/completion`, le driver appelle
`/apply-template`, sauvegarde la requête et la réponse, puis impose le
marqueur final `<|im_start|>assistant` suivi d'un LF et le suffixe exact :

```python
re.fullmatch(r"<think>\s*</think>\s*", suffix)
```

L'ancienne version du prédicat admettait l'absence du marqueur assistant ou
du texte avant `<think>`. Ce point a été signalé et durci par l'intégrateur
avant toute completion 8B, puis relu. Sept sondes autonomes du prédicat
acceptent le bloc vide fermé et refusent : absence de marqueur, bloc ouvert,
contenu de pensée non vide, texte avant/après et deux blocs successifs.
Ce sont des contrôles de chaîne, sans appel au runtime ou au modèle.

La portée défendable est : pas de bloc de pensée ouvert ni appel auxiliaire
de raisonnement dans ce chemin de génération. Cela ne prouve rien sur une
cognition latente. Le prompt natif réellement rendu devra rester dans les
bruts ; une incompatibilité de template arrête avant `/completion`.

## Données, patches et budgets

Les initiales historiques sont authentifiées contre leurs anciennes
instructions et requêtes publiques ; elles ne sont pas régénérées. Le
nouveau modèle reçoit ces réponses, les instructions et le feedback composé
du verdict minimal et des évaluations exactes de **ses propres lignes**.
Le producteur de feedback ne construit pas les lignes cibles et ne fournit
pas de patch canonique. Son gloss exprime les verdicts ; aucune justesse du
diagnostic libre produit par le modèle n'est présumée.

Le parseur applique les éditions littérales en ordre, sur une copie de la
réponse initiale. Tous les coefficients et indices modifiés viennent du
texte LLM ; aucune donnée ou référence n'est consultée pour les compléter.
Le diagnostic est limité à 768 caractères ASCII imprimables et n'a aucun
effet sémantique. L'application est atomique, les listes et valeurs sont
bornées et le modèle final doit satisfaire le schéma/compilateur existant.

Les constantes et requêtes observées dans le code sont conformes au plan :
1024 nouveaux tokens, contexte total 4096 avec réserve complète de sortie,
T=0.7, top-p=0.8, top-k=20, min-p=0, seed SHA(ID)+1, quatre threads CPU,
MTL0 demandé et 99 couches demandées. Les probabilités sont appariées au
token choisi, jamais remplacées par le top-1 ; leur portée reste l'API
épinglée avec les réserves de normalisation liées à la grammaire.

Le driver vérifie 3 GiB libres avant le serveur et 1 GiB avant chaque appel.
Chaque completion a une limite dure de 180 s. Le serveur appartient au
groupe de processus parent, possède un watchdog et est arrêté/récolté dans
`finally`, avec erreur conservée en cas d'échec. Le programme s'arrête au
premier échec et conserve les lignes déjà flushées, sans imputation.

Le module reste générique : son plafond interne de phase est 1650 s et son
watchdog de secours 1800 s. **Le caller doit donc imposer les deux cas et le
runner externe de 480 s annoncés par C22.** Ces limites du plan ne sont pas
automatiquement remplacées par les valeurs internes. Le message d'une
exception mentionne encore «1..512», alors que la condition réelle et les
métadonnées utilisent bien 1024 ; ce libellé ancien ne modifie pas le cap.

## Calibration et suite

Le champ `copied_driver_sha256` conserve un ancêtre ancien ; les SHA des
fichiers C21 et C22 effectivement comparés sont enregistrés séparément dans
ce rapport JSON. Les temps de téléchargement, hashing, chargement,
completions, client Python et serveur doivent rester séparés ; les temps
inclusifs ne s'additionnent pas sans précaution. Ni fit 8 GiB, ni latence,
ni succès de réparation ne sont établis avant les appels.

Les deux cas sont des erreurs de développement post-hoc déjà consultées.
Passer du 4B Instruct au 8B hybride change aussi la variante, l'entraînement
et la quantification ; aucun effet causal isolé du nombre de paramètres,
aucune généralisation ou nouveauté n'est inféré. Une nouvelle expérience
réservée devra disposer d'un protocole et d'annotations séparés. Aucun
fichier C23 n'a été consulté pour cette revue.
