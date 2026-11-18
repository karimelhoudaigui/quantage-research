# Probe v1 — zéro proposition, défaut d'adaptateur et disque plein
Le modèlecharge26/26couches surMetal, environ1204.91MiB de poidsGPU.
Le client hérité ne whiteliste pas encore /apply-template; cet appel lève
avant /completion. La sérialisation de l'échec est empêchée parENOSPC
(risque enregistré par le runner). Manifestfailedconservé, aucun raw ni
generation.json. Ce n'est pas une mesure de capacité du modèle.
V2 dans un autre module ajoute uniquement cet endpoint local de formatage
et relève les gardes disque à3GiBavantchargement/1GiBavantchaqueappel.
Les11GiBdeGitgarbagefermés sontnettoyés avec preuvesmetadata/références.
Aucune instruction/seed/température ou poids modifié, aucun appelLLM àrépéter.
Sourcev1 inchangée; nouvel essai borné2appels dans un autre dossier.
