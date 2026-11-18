# Revue matérielle et runtime C27

## Conclusion

C27 établit qu'une requête locale donnée a complété avec llama.cpp b12359, Flash Attention activé, caches K/V `q8_0` et placement rapporté sur Metal. Cela n'établit ni fit mémoire général, ni débit garanti, ni exécution exclusivement GPU, ni résultat QPU.

## Observations conservées

Le driver a demandé `MTL0`, 99 couches GPU, contexte 6144, quatre threads, Flash Attention `on`, et `q8_0` pour K et V. Les journaux du chargeur rapportent 37/37 couches sur Metal, buffers Metal positifs, 459,00 MiB au total pour le cache K/V et Flash Attention activé. Le prompt de 1795 tokens a terminé son préremplissage en 131,227 s (13,68 tokens/s); les 143 tokens ont été générés en 10,844 s (13,10 tokens/s). `wall_seconds` vaut 188,489 s et le chargement 40,794 s. Ce sont des mesures d'un seul appel, sans baseline.

La réponse a été enregistrée entière et s'est terminée par EOS (`truncated = 0`). Le processus serveur a ensuite reçu TERM, a dépassé l'attente de nettoyage et a été forcé à s'arrêter puis reap; son statut de sortie observé est `-9`. Le manifeste donne `status=completed`, `error=null`, `cleanup_error=null`, et `server_reaped=true`. La raison du retard à l'arrêt n'est pas déterminée.

Les contrôles natifs de la révision du runtime acceptent `--flash-attn on|off|auto` et les options de type de cache K/V, dont `q8_0`. Sources primaires : [arguments llama.cpp, commit b1b770d](https://github.com/ggml-org/llama.cpp/blob/b1b770d90d94cad9e9ea5b993bdbc383a522fb28/common/arg.cpp#L1726-L1740), [options K/V](https://github.com/ggml-org/llama.cpp/blob/b1b770d90d94cad9e9ea5b993bdbc383a522fb28/common/arg.cpp#L280-L310), [options Flash Attention](https://github.com/ggml-org/llama.cpp/blob/b1b770d90d94cad9e9ea5b993bdbc383a522fb28/common/arg.cpp#L2409-L2433). La complétion C27 constitue une preuve pratique plus forte que la seule aide CLI pour cette requête/configuration.

## Limites d'application à C23

C23 ne peut pas être lancé sur la base de cette observation : son protocole de dépendance exige une proposition complète C25 sous placement partiel/cache f16. C25 n'a pas produit de réponse. C27 demandait 99 couches et utilisait les caches `q8_0`; il ne reproduit donc pas le gate ni la configuration évalués par C25. Aucun QPU n'a été sollicité.
