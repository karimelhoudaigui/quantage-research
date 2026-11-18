# C21 — pilote de feedback arithmétique concret

15 novembre2026, avant inférenceC21. C20a produit2patchesvalides maisaucunefidélité ; diagnosticsconfondent référence/candidat et satisfactiondespropreslignes. DeuxmêmesancienscasC19/C20DEVELOPPEMENT, initialesjamaisrééchantillonnées. Deuxnouveauxappelsguidésmaximum, aucunretry. Aucun nouveautest ni gainconfirmatoire.

Le vérificateur renvoie le même verdictminimal (bits et booléens/scalaires), accompagné d’une évaluationexacte des PROPRES lignes du candidat : index,lhs,relation,rhs,satisfied,objectif. Aucun nom de clause,coefficient,lignede référence ou correctiongold. Un glossanglais explicite acceptation/réjection des deux modèles sans informationadditionnelle. Le LLM reste auteur du diagnostic et de chaque édition. Appliqueur atomique identiqueàC20,objectifresteéditable, aucune réparationautomatique.

Cap1024tokensnouveauxincluantdiagnostic ; diagnostic≤768caractèresASCII,contexte4096avec réservecomplète1024+1. Même4B/Q4_K_M/b12359/MetalM2,T.7p.8k20,seedSHAID+1,180s/call,480srunner/1650sinterne,réservedisque3GiBstartup/1GiBentre. UnseulGPUserver. Le changement conjoint feedback/gloss/cap/diagnostic ne permet pas d’attribuer un effet causal au seul outil. Toute futurecomparaison doit égaliser les nouveauxplafondsentrebras et figerunnouveautest.

Mesures : replaypatch,valide/fidèle,erreursrésiduelles,diagnosticnoncertifié,coûtspropres+initialesattribuées,2solveursréelsparmodèlevalide. Anciennesinitialesetcoûtsne sontpasgratuits. Sources/inputsfigésavantrun ; stop suréchec,absentssansimputation. Deuxcasposthoc ne démontrentaucunegénéralisation. Aucunachat,secret,publication,push,messageexterneouQPU.
