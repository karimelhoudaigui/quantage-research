# Amendement avant tout appel génératif C16

Le premier démarrage charge le modèle mais s'arrête avant /completion,
faute de logs de placement au niveau par défaut3. Aucune proposition,
aucun score LLM, aucun texte test reçu par le modèle. Échec conservé.
Correction d'instrumentation : niveau4, préfixesMetal/MTL, autre dossier
préflightv2. Aucun poids, coefficient, feedback, instruction ou seed changé.
La limite reste deux appels génératifs de préflight maximum et180s/appel.
Ce redémarrage corrige une garde avant génération; ce n'est pas un retry
de sortie LLM. Les sources du premier démarrage et son manifest sont archivés.
La revue distincte avait couvert l'architecture et signalé cleanup/probabilité.
Le quota natif est désormais épuisé; correction et contrôle final par
l'intégrateur, sans prétendre à une nouvelle revue indépendante.
