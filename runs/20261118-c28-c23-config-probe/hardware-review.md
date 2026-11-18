# C28 — revue matérielle

## Configuration et preuve

La commande réellement enregistrée dans `initial-v1/driver/generation.json` demande `--ctx-size 6144`, quatre threads, batch et ubatch 128, 30 couches GPU et `MTL0`. Elle ne passe pas `--flash-attn` ni `--cache-type-k/v`; le `--help` b12359 épinglé indique Flash Attention `auto` et K f16 par défaut, et les logs d'exécution observent `flash_attn = auto`, K/V `f16`, 432 MiB par cache.

Le chargeur rapporte Metal, 30/37 couches déchargées, et des buffers modèle `486.87 MiB` et `3176.72 MiB`. L'ajustement initial estime 4409 MiB projetés contre 5460 MiB disponibles et prédit 1051 MiB restants. C'est l'estimation de `common_fit_params`, pas une mesure de la mémoire dynamique pendant génération ni une garantie de réserve.

## Limite observée

Le serveur a reçu un prompt de 740 tokens. Les logs signalent 640 tokens (86 %) après 126,05 s, puis le sampler; le client n'a pas reçu de réponse dans les 180 s. Le driver a conservé zéro réponse achevée et le décompte de tokens générés réellement par le serveur reste inconnu. Le serveur est reap avec code `-9`, sans erreur de cleanup consignée.

Cette tentative confirme le placement demandé/observé et l'activation des valeurs par défaut, mais **ne franchit pas le gate d'exécution**. Aucun marqueur explicite d'OOM n'apparaît; le timeout ne prouve ni manque de mémoire ni marge suffisante. Ce n'est pas un benchmark comparatif, une preuve de performance de population, une exécution QPU ou une validation de solveur. Pas de QPU ni dépense externe.

## Source primaire

Les options et valeurs par défaut sont documentées dans le [README officiel du serveur llama.cpp à b12359](https://raw.githubusercontent.com/ggml-org/llama.cpp/b12359/tools/server/README.md). Pour cette tentative, le `--help` local épinglé et les journaux du processus sont les preuves de configuration effectivement observée; la documentation ne remplace pas ces mesures.
