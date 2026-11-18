# C14 bloqué — aucune performance du modèle plus grand établie

Exécuté : acquisition publique Qwen2.5-1.5B, un essai float16CPU arrêté,
un diagnosticforward float16, un diagnosticbfloat16, puis un essai bfloat16
arrêté pour coût. Uneseuleréponseparconfiguration surlemêmepremiercas.
Float16 :151936logitsNaN et128!; bfloat16 :logitsfinis etuncontratconforme
49tokens en493.62s. Les deux échecs de génération sont desarrêts anticipés,
conservés comme manifestfailed. Le contrôle bfloat16 a un manifestcompleted.

H14nonrésolue : pas de matrice32, aucun score comparatif, aucune imputation
des31réponsesabsentes. Budgetmatériel8GiB, temps32estimé impraticable sous
1650s. Pas de modèle sémantiquement condamné àpartir d'un échec numérique.

Manuscrit : ajouter le contrôle de runtime et cette limite; conserver C11
inchangé. Reprise : runtime/budgetadapté etnouveauprotocole; nouvelle méthode
etnouveauxgroupes à annoterséparément quandlesressourceslepermettent.
