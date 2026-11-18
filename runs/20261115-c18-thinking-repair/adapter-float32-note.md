# Tolérance d'adaptateur, aucune nouvelle génération du premier cas
Le premier /completion a réellement retourné1024tokens(cap), sansfermeture
du raisonnement. Son JSONHTTP est conservé. La validation d'adaptateur lève
sur top_p0.949999988079071 comparé exactement à0.95; température est déjà
comparée avec tolérance. V2 ajoute la même tolérance relative1e-6 pourtop_p,
sans modifier la demande0.95 ou un token. Reconstituer le premier record
depuis ceHTTP, sans le régénérer, puis tenter uniquement le second cas jamais
appelé. Le dépassement reste un échec de réponse finale observé.
