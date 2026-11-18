# Préflight v1 — instrumentation, aucune proposition
Le serveur charge le modèle en environ3.5s mais le niveau de logs par défaut3
n'émet pas les preuves de placement tenseur attendues. La garde arrête avant
tout /completion :0appel génératif,0réponse. Manifest failed conservé.
Le code exact avant correction est archivé sous dev-preflight-v1/source-snapshot;
le seul fichier GGUF est un hardlink immuable pour économiser1.12Go, hashes
vérifiables. Aucun résultat de test ou développement n'est consulté pour ce fix.
Correction prévue : logs de chargement niveau4 et préfixe moderneMTL0 admis;
nouveau préflight borné2appels, sortie distincte, pas un retry stochastique.
