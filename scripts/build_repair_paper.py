"""Build the C16 manuscript from complete recorded results, without inference."""
import json
from pathlib import Path
import sys

from build_paper import latex

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs/20261115-c16-quantized-repair"
METHODS = [("initial", "Initiale, un appel"), ("direct", "Direct, deux candidats"),
           ("self", "Auto-révision"), ("guided", "Guidée")]
CODE = chr(96)


def read(path):
    return json.loads(path.read_text())


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def table(header, body):
    return "\n".join(["| " + " | ".join(header) + " |",
                      "|" + "---|" * len(header)] +
                     ["| " + " | ".join(map(str, row)) + " |" for row in body])


def code(value):
    return CODE + json.dumps(value, ensure_ascii=False, separators=(",", ":")) + CODE


def example(raw, traces, public):
    # Descriptive example, chosen only after test scoring; no model is changed.
    candidates = [r for r in raw if r["results"]["guided"]["verification"]["faithful"]
                  and r["results"]["initial"]["verification"]["stage"] == "finite_cube"
                  and not r["results"]["initial"]["verification"]["faithful"]]
    kind = "réparation mathématique"
    if not candidates:
        candidates = [r for r in raw if r["results"]["guided"]["verification"]["faithful"]
                      and not r["results"]["initial"]["verification"]["faithful"]]
        kind = "réparation après échec de format"
    if not candidates:
        candidates = [r for r in raw if r["results"]["initial"]["verification"]["stage"] == "finite_cube" and not r["results"]["initial"]["verification"]["faithful"]]
        kind = "échec mathématique conservé"
    if not candidates:
        candidates = raw
        kind = "échec de format conservé"
    chosen = min(candidates, key=lambda r: r["id"])
    identity = chosen["id"]
    case = public[identity]
    initial = traces["initial"][identity]
    guided = traces["guided"][identity]
    lines = ["### Exemple descriptif : " + kind,
             "", "Cas " + identity + ", choisi après scoring par le premier identifiant admissible; "
             "cet exemple ne constitue pas une nouvelle évaluation.", "",
             case["intention"], "",
             "Données : poids " + code(case["data"]["weights"]) + ", coûts " +
             code(case["data"]["costs"]) + ", exclusions " + code(case["data"]["edges"]) + ".", ""]
    for name, candidate in [("Initiale", initial), ("Révision guidée produite", guided)]:
        parsed = candidate["parsed"]
        lines += [name + " :"]
        if parsed["valid"]:
            authored = parsed.get("authored_model", parsed["model"])
            lines += ["", "- Variables : " + code(authored["variables"]) + ".",
                      "- Objectif : " + code(authored["objective"]) + "."]
            for constraint in authored["constraints"]:
                lines += ["- Contrainte : " + code(constraint) + "."]
        else:
            # Retain the literal response in source traces; report its exact parse failure.
            lines += ["", "Proposition invalide : " + parsed["error"] +
                      ". Réponse brute intégrale conservée dans le JSONL correspondant."]
        lines += [""]
    feedback = chosen["initial_feedback"]
    lines += ["Retour effectivement transmis : " + code(feedback) + ".", "",
              "Verdict final guidé : " +
              ("fidèle sur le cube fini." if chosen["results"]["guided"]["verification"]["faithful"]
               else "non fidèle; le système conserve cet échec.") ]
    return "\n".join(lines)


def build():
    partial = not (RUN / "test-score-v1/metrics.json").exists()
    score_dir = RUN / ("partial-score/paired-results" if partial else "test-score-v1")
    metrics = read(score_dir / "metrics.json")
    assert metrics["cases"] == (15 if partial else 16)
    assert metrics["physical_generation_calls"] == (60 if partial else 64)
    raw = rows(score_dir / "raw.jsonl")
    public = {r["id"]: r for r in read(RUN / "test_cases.json")}
    traces = {phase: {r["id"]: r for r in rows(RUN / ("test-" + phase + "-v1/driver/raw.jsonl"))}
              for phase in ("initial", "direct", "self", "guided")}
    if partial:
        traces["guided"].update({r["id"]: r for r in rows(
            RUN / "test-guided-continuation-v1/driver/raw.jsonl")})
    m = metrics["methods"]
    direct, self_count, guided = [m[k]["faithful"] for k in ("direct", "self", "guided")]
    replacements = {
        "ABSTRACT_RESULTS": "Le direct obtient {}/16 formulations fidèles, l'auto-révision {}/16 et le guidé {}/16. "
                            "Le gain guidé contre auto est de {} cas; le critère H16 est {}.".format(
                                direct, self_count, guided, guided - self_count,
                                "satisfait dans ce test fini" if metrics["H16"]["status"] == "supported_in_finite_test" else "non satisfait"),
        "MAIN_TABLE": table(["Méthode", "Schéma valide /16", "Fidèle /16",
                             "Équiv. optimisation /16", "Utilisable /16"],
                            [[label, m[key]["schema_valid"], m[key]["faithful"],
                              m[key]["optimization_equivalent"], m[key]["usable_for_original_problem"]]
                             for key, label in METHODS]),
        "PRIMARY_RESULT": "H16 : {}. Guidée moins auto = {}; régressions guidées = {}. "
                          "Les {} erreurs initiales donnent {} réparations guidées jusqu'à fidélité, "
                          "dont {} après format invalide et {} après modèle au schéma valide mais faux.".format(
                              metrics["H16"]["status"], metrics["H16"]["guided_minus_self_faithful"],
                              m["guided"]["regressions_from_faithful"], m["guided"]["initial_errors"],
                              m["guided"]["repairs_to_faithful"], m["guided"]["format_repairs_to_faithful"],
                              m["guided"]["mathematical_repairs_to_faithful"]),
        "STRATA_TABLE": table(["Strate", "Direct fidèle", "Auto fidèle", "Guidée fidèle"],
                              [[axis + " : " + value + " (n=" + str(counts["initial"]["observed"]) + ")",
                                *[str(counts[k]["faithful"]) for k in ("direct", "self", "guided")]]
                               for axis, values in metrics["strata"].items() for value, counts in values.items()]),
        "ERROR_TABLE": table(["Méthode", "Désaccords faisabilité", "Désaccords objectif",
                              "Affectations comparées", "Régressions"],
                             [[label, m[key]["feasibility_mismatches"], m[key]["objective_mismatches"],
                               m[key]["assignments_compared"], m[key]["regressions_from_faithful"]]
                              for key, label in METHODS]),
        "WORKED_EXAMPLE": example(raw, traces, public),
    }
    dev = read(RUN / "dev-score-v1/metrics.json")["methods"]["initial"]
    replacements["DEV_SIGNATURES"] = ", ".join("".join(sorted(x["families"])) for x in read(RUN / "gold.json") if x["split"]=="dev")
    replacements["DEVELOPMENT"] = (
         "Développement C16 : {}/8 schémas valides et {}/8 formulations fidèles, avec deux réponses sous v1 et six sous v2. "
        "Ces huit réponses restent séparées du test et ne mesurent pas un prompt uniforme.".format(dev["schema_valid"], dev["faithful"]))
    portfolios = [value["portfolio"] for r in raw for value in r["results"].values() if value["portfolio"]]
    concordant = sum(p["concordance"] for p in portfolios)
    selected = {}
    for p in portfolios:
        selected[p["selected_solver"]] = selected.get(p["selected_solver"], 0) + 1
    replacements["SOLVER_RESULTS"] = (
        "{} profils candidats, soit {} appels solveurs réellement exécutés; {} profils concordants. "
        "Choix observés : {}. Temps total des profils : {:.6f} s; somme des seuls temps sélectionnés : {:.6f} s. "
        "Un candidat identique sélectionné dans plusieurs bras peut être exécuté plusieurs fois; ces profils "
        "ne sont pas des observations indépendantes. Le chargement initial de SciPy est hors de ces timers "
        "et appartient au temps du processus de scoring.".format(
            len(portfolios), 2 * len(portfolios), concordant, json.dumps(selected, ensure_ascii=False),
            metrics["scored_portfolio_seconds_total"],
            sum(p["selected_solver_seconds"] or 0 for p in portfolios)))
    costs = metrics["attributable_cost_per_arm"]
    replacements["COST_TABLE"] = table(
        ["Périmètre", "Appels", "Tokens entrée", "Tokens sortie", "Temps réponses (s)"],
        [[label, 2 * metrics["cases"], costs[key]["input_tokens"], costs[key]["output_tokens"],
          "{:.2f}".format(costs[key]["wall_seconds"])] for key, label in METHODS if key != "initial"] +
        [["Physique test", metrics["physical_generation_calls"],
          metrics["physical_generation_cost"]["input_tokens"],
          metrics["physical_generation_cost"]["output_tokens"],
          "{:.2f}".format(metrics["physical_generation_cost"]["wall_seconds"])]])
    if partial:
        bounds = read(RUN / "partial-score/metrics.json")
        replacements["ABSTRACT_RESULTS"] = (
            "Une panne d'espace disque laisse une réponse guidée inconnue sur seize. "
            "Les quinze cas complètement appariés donnent une formulation fidèle par méthode, "
            "toutes sur une référence infaisable. Le gain guidé contre auto sur les seize cas "
            "appartient à [0,1], quel que soit le résultat manquant : le seuil préenregistré de trois "
            "cas n'est donc pas atteint. Aucun résultat manquant n'est imputé.")
        replacements["MAIN_TABLE"] = (
            "Sous-ensemble descriptif des quinze cas complètement appariés; aucune observation "
            "n'est régénérée après la panne.\n\n" +
            replacements["MAIN_TABLE"].replace("/16", "/15"))
        replacements["PRIMARY_RESULT"] = (
            "Sur le test prévu de seize cas, direct et auto obtiennent chacun 1/16. "
            "Guidée a 1/15 observé et une réponse inconnue, donc entre 1 et 2 formulations "
            "fidèles sur seize. Son gain contre auto est entre 0 et 1; H16 n'est satisfaite "
            "dans aucune complétion possible de la réponse perdue. Ces bornes sont logiques "
            "sur l'issue inconnue, pas des intervalles de confiance. Aucune réparation fidèle "
            "d'un modèle initialement faux n'est observée dans les quinze paires complètes.")
        replacements["COST_TABLE"] = (
            "Les coûts ci-dessous portent seulement sur les soixante réponses des quinze paires "
            "complètes. Le test a tenté 64 appels et conserve 63 réponses : "
            "{:,} tokens d'entrée, {:,} de sortie, {:.2f} s de requêtes enregistrées au total. "
            "Le coût de l'appel interrompu et du serveur dans la phase perdue reste inconnu.\n\n".format(
                bounds["observed_physical_cost"]["input_tokens"],
                bounds["observed_physical_cost"]["output_tokens"],
                bounds["observed_physical_cost"]["wall_seconds"]) +
            replacements["COST_TABLE"].replace("Physique test", "Sous-ensemble apparié"))
    markdown = (ROOT / "paper/template-repair.md").read_text()
    if partial:
        markdown = markdown.replace(
            "Le test partage physiquement les initiales : 64 appels distincts, contre 96 attribuables aux trois bras isolés.",
            "Le protocole prévoit 64 appels physiques, contre 96 attribuables aux trois bras isolés; une réponse est perdue après panne d'espace disque.")
        markdown = markdown.replace(
            "## Résultats de formulation et réparation",
            "## Résultats de formulation et réparation\n\nUne panne ENOSPC interrompt le sixième appel guidé. "
            "Cinq réponses sont préservées; seuls les dix cas jamais tentés sont poursuivis, avec les mêmes "
            "sources, consignes et graines figées. L'appel interrompu 54969ba6bb41 est laissé inconnu. "
            "Le manifest final de la première partie guidée n'a pas pu être écrit; le journal d'incident "
            "enregistre les hashes des fichiers survivants après arrêt, sans inventer d'enveloppe complète.")
    for key, value in replacements.items():
        token = "{{" + key + "}}"
        if token not in markdown:
            raise ValueError("missing replacement " + key)
        markdown = markdown.replace(token, value)
    if "{{" in markdown:
        raise ValueError("unresolved template")
    tex = latex(markdown).replace(r"\date{14 novembre 2026}", r"\date{15 novembre 2026}")
    (ROOT / "paper/article.md").write_text(markdown)
    (ROOT / "paper/main.tex").write_text(tex)
    print(json.dumps({"cases": metrics["cases"], "partially_observed": partial,
                      "methods_faithful": {k: m[k]["faithful"] for k, _ in METHODS},
                      "H16": metrics["H16"]["status"], "pdf_compiled": False}))


if __name__ == "__main__":
    build()
