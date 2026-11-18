# C18 — raisonner puis formuler, réparation bornée

15 novembre2026. Étape développement préenregistrée avant générationC18.
C17non-thinking a2propositionsréelles,2modèlesanalysables mais faux :
tousdeux créent une cardinalitéminimum égale au nombre d'options disponibles.
Aucun test C17; garder ce résultatnégatif. C18 active le mode de raisonnement
du même Qwen3.5-2B communautaire. C'est une nouvelle configuration et un
nouveau budget, pas une amélioration isolée attribuée au seul vérificateur.

Probe de capacité :2anciens casdéveloppementC16 (080d034c34b2,4e0256180e89),
un appel initial chacun, aucun gold en inférence, pas de retry.réserve disque3GiBavantmodèle/1GiBavantappel, contexte4096,1024nouveaux
tokens MAXIMUMincluant TOUTle raisonnement et le JSON,180s/complétion,
480sphaseprobe. Température0.6,top-p0.95,top-k20, pas de pénalité de présence.
Même graineSHA256ID. Aucun code candidat exécuté, secret, achatouQPU.

Le template natif GGUF est rendu par /apply-template avec enable_thinking=true.
Vérifier que le préfixe ouvre<think>. Ne pas contraindre la génération par
grammaire : le modèle peut raisonner puis doit fermer</think> et rendre un
JSON complet. Le parseur n'extrait que l'unique suffixe après cette fermeture;
il ne répare aucun coefficient et conserve le brut entier. Tout dépassement
de1024 sans réponse finale reste un échec observé. Aucun raisonnement/API
supplémentaire gratuit horsbudget.

Préciser dans la consigne : n est le nombre d'options DISPONIBLES, pas le
nombre imposé de sélections. Seules les arêtes listées sont des exclusions.
Coûts présents ne signifient pas qu'un budget existe. Les indices imposés
désignent des variables, pas une borne de coût. Cette précision traite les
erreurs de développement, sans lire de nouveau test.

Si au moins un modèle fidèle est obtenu et le coût viable, constituer un corpus
entièrement nouveau pour direct/auto/guidée, même2appels et2048tokens parbras.
Nouveau protocole testet gel avanttoutegénérationtest. Sinon conserver échec
et diagnostiquer; pas de prétention de solution. Quota natif épuisé : contrôles
finaux séquentiels de l'intégrateur, non indépendants; référencesC16 restent
annotées indépendamment avant l'ensemble de ces probes.
