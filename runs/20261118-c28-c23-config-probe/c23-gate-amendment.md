# Amendement prospectif du gate C23

Le gate historique exigeait une proposition complète C25 sous placement partiel et cache f16. C25 a expiré sans proposition; C27 n'est pas substituable, car il utilisait une configuration différente. À la demande de reprise et avec l'autorisation explicite reçue dans la conversation le 18 novembre 2026, cet amendement remplace, **avant tout appel C23**, l'exigence C25 par le pilote C28 borné et préenregistré dans `protocol.md`.

Le remplacement est limité : une unique proposition initiale doit être parser-valide et complète sous la configuration du driver C23; le critère complet figure dans le protocole. Un échec bloque C23 sans retry. Un succès autorise uniquement la préparation et le gel d'un protocole C23 séparé; il n'est pas un résultat scientifique et ne déclenche pas l'étude réservée.

Les notes et rapports historiques C25/C27 restent inchangés. Le champ `runtime_precondition` des drivers actuels est mis à jour pour refléter C28; cette déclaration est une métadonnée, et l'orchestration demeure responsable de faire respecter le gate.
