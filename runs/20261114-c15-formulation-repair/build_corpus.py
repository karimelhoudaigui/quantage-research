#!/usr/bin/env python3
"""Author-only C15 corpus builder; contains private annotations, never a prompt.

All public requests are hand-authored here before model inference. The only
automated generation is serialization and exhaustive author sanity checking.
No model, scorer, verifier, earlier corpus or external source is imported.
"""

import hashlib
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
START_COMMIT = "fee83eb4575198e3e142d41c621300b4d11361d8"
GOLD_KEYS = ("budget", "min_count", "max_count", "required", "forbidden", "implications")
FAMILY_KEYS = {"B": "budget", "L": "min_count", "U": "max_count",
               "M": "required", "F": "forbidden", "I": "implications"}


def annotation(budget=None, min_count=None, max_count=None,
               required=(), forbidden=(), implications=()):
    return {"budget": budget, "min_count": min_count, "max_count": max_count,
            "required": list(required), "forbidden": list(forbidden),
            "implications": [list(pair) for pair in implications]}


def specimen(identifier, split, language, data, constraints, intention,
             infeasibility_reason=None):
    return {"id": identifier, "split": split, "language": language,
            "data": data, "constraints": constraints, "intention": intention,
            "infeasibility_reason": infeasibility_reason}


# These are 24 separate requests, not translations or perturbations of four
# templates. Item numbers always mean zero-based indices into the data arrays.
SPECS = [
    specimen("9e2a4c71", "dev", "fr",
             {"n": 4, "weights": [9, 5, 8, 6], "costs": [7, 2, 4, 3],
              "edges": [[0, 1], [1, 2]]}, annotation(budget=8),
             "Pour ces quatre dossiers numérotés de 0 à 3, x_i vaut 1 si le dossier i est retenu et 0 sinon. "
             "Maximiser la somme des weights des dossiers retenus. Chaque paire donnée dans edges est une exclusion : "
             "on ne peut retenir ses deux dossiers. La somme des costs retenus doit être au plus 8. "
             "Il n'y a pas d'autre contrainte."),
    specimen("31d8b6f0", "dev", "en",
             {"n": 5, "weights": [4, 10, 6, 8, 3], "costs": [2, 7, 4, 3, 1],
              "edges": [[0, 2], [1, 3], [2, 4]]}, annotation(min_count=2),
             "Use a binary decision x_i for each of the five projects, indexed 0 through 4: 1 selects it and 0 leaves it out. "
             "The objective is the largest possible total of selected weights. Any pair in edges is incompatible, "
             "so its two projects cannot both be selected. We need at least 2 projects. No other restrictions apply."),
    specimen("a7f03d2c", "dev", "fr",
             {"n": 6, "weights": [7, 2, 11, 5, 9, 4], "costs": [4, 1, 6, 3, 5, 2],
              "edges": [[0, 4], [1, 2], [3, 5]]}, annotation(max_count=2),
             "Parmi les six expériences 0, 1, 2, 3, 4 et 5, retenir au maximum 2 expériences. "
             "Associer à chacune une variable binaire x_i égale à 1 exactement quand elle est retenue. "
             "Les deux indices de toute paire de edges ne doivent jamais être retenus ensemble. "
             "Chercher le maximum de la somme des weights retenus, sans autre contrainte."),
    specimen("68c1e9b4", "dev", "en",
             {"n": 7, "weights": [6, 12, 4, 9, 5, 7, 3], "costs": [3, 6, 2, 5, 4, 1, 2],
              "edges": [[0, 2], [1, 4], [3, 6], [4, 5]]}, annotation(required=(2, 5)),
             "Select a portfolio from items numbered 0 to 6. Items 2 and 5 must be in the portfolio. "
             "Let x_i be binary, with x_i=1 meaning item i is chosen. Every pair in edges forbids taking both endpoints. "
             "Maximize the sum of weights of the chosen items. These are all the requirements."),
    specimen("c2b7460d", "dev", "en",
             {"n": 4, "weights": [6, 13, 5, 8], "costs": [2, 5, 1, 4],
              "edges": [[0, 3], [1, 2]]}, annotation(forbidden=(1,)),
             "There are four candidate modules, indexed from 0. A binary variable x_i records whether module i is installed. "
             "Choose the modules with maximum total weight, counting only installed modules. "
             "For each pair listed in edges, at most one of the two modules can be installed. "
             "Module 1 is unavailable and must be excluded. No further constraints are imposed."),
    specimen("f40a8e53", "dev", "fr",
             {"n": 5, "weights": [12, 5, 8, 3, 9], "costs": [6, 2, 4, 1, 5],
              "edges": [[0, 2], [1, 3], [2, 4]]}, annotation(implications=((0, 3),)),
             "On décide pour chacun des objets 0 à 4 s'il est choisi : x_i est binaire et vaut 1 dans ce cas. "
             "Choisir l'objet 0 oblige à choisir aussi l'objet 3 ; choisir 3 seul reste autorisé. "
             "Toute paire de edges interdit de choisir simultanément ses deux objets. "
             "L'objectif est de maximiser la somme des weights des objets choisis. Aucune autre condition ne s'ajoute."),
    specimen("0b5d97a2", "dev", "en",
             {"n": 6, "weights": [11, 4, 9, 6, 8, 3], "costs": [8, 2, 5, 4, 3, 1],
              "edges": [[0, 4], [1, 3], [2, 5]]}, annotation(budget=10, min_count=2),
             "Plan a selection of the six tasks indexed 0 through 5, using binary x_i=1 for a selected task. "
             "The total selected cost must not exceed 10, and at least 2 tasks must be selected. "
             "The pairs in edges are mutual exclusions: never select both tasks in one pair. "
             "Maximize the total selected weight. There are no additional requirements."),
    specimen("7d139ac8", "dev", "fr",
             {"n": 7, "weights": [8, 5, 14, 7, 4, 10, 12], "costs": [4, 2, 6, 3, 1, 5, 7],
              "edges": [[0, 3], [1, 5], [2, 4], [3, 6]]},
             annotation(max_count=2, forbidden=(2, 6)),
             "Construire un lot avec les articles d'indices 0 à 6. Les articles 2 et 6 sont interdits et le lot "
             "contient au plus 2 articles. Pour chaque article, x_i appartient à {0,1} et indique sa présence. "
             "Une paire de edges ne peut pas avoir ses deux articles présents. Maximiser la somme des weights "
             "des articles du lot ; aucune autre contrainte n'est demandée."),
    specimen("e84b2f19", "test", "fr",
             {"n": 4, "weights": [8, 11, 5, 7], "costs": [5, 7, 2, 3],
              "edges": [[1, 3]]}, annotation(budget=10, min_count=1, max_count=2),
             "Pour sélectionner des ateliers parmi les indices 0 à 3, poser x_i binaire, égal à 1 pour un atelier retenu. "
             "La sélection doit comporter entre 1 et 2 ateliers, bornes incluses, et son coût total doit rester inférieur "
             "ou égal à 10. Les paires de edges sont incompatibles et ne peuvent être retenues ensemble. "
             "Maximiser la somme des weights sélectionnés. Il n'y a aucune autre obligation."),
    specimen("4a6d90c3", "test", "en",
             {"n": 5, "weights": [10, 7, 4, 12, 6], "costs": [6, 3, 2, 7, 4],
              "edges": [[0, 1], [2, 3]]}, annotation(budget=10, min_count=2, required=(4,)),
             "Choose at least 2 of the five indexed components, 0 to 4, with component 4 compulsory. "
             "Represent each choice by a binary x_i that is 1 for inclusion. Spending, computed as the sum of costs "
             "of included components, may be 10 or less. Each edge forbids including its two endpoints together. "
             "The aim is to maximize total included weight. Those are the only constraints."),
    specimen("b91c5e72", "test", "fr",
             {"n": 6, "weights": [9, 15, 7, 11, 13, 5], "costs": [5, 2, 4, 7, 3, 2],
              "edges": [[0, 2], [1, 3], [2, 5], [3, 4]]},
             annotation(budget=11, min_count=2, forbidden=(1, 4)),
             "Les options portent les indices 0 à 5. On souhaite un ensemble d'au moins 2 options, mais ni l'option 1 "
             "ni l'option 4 ne doit y figurer. Le coût cumulé des options choisies ne doit pas dépasser 11. "
             "Définir x_i dans {0,1}, avec 1 pour une option choisie ; chaque paire de edges interdit la présence "
             "simultanée de ses deux options. Maximiser la somme des weights choisis, sans autre restriction."),
    specimen("23e8a6d0", "test", "en",
             {"n": 7, "weights": [13, 8, 6, 12, 5, 4, 7], "costs": [5, 4, 2, 6, 1, 3, 2],
              "edges": [[0, 2], [1, 4], [2, 6], [3, 5]]},
             annotation(budget=12, min_count=3, implications=((0, 5), (3, 6))),
             "For the seven proposals indexed 0 through 6, find the maximum sum of selected weights. "
             "Use one binary x_i per proposal, set to 1 if selected. Select at least 3 proposals and spend at most 12 "
             "in total costs. Selecting proposal 0 requires proposal 5; selecting proposal 3 requires proposal 6. "
             "Neither requirement runs in reverse. The pairs in edges prohibit jointly selecting their endpoints. "
             "There are no other rules."),
    specimen("d062f4b9", "test", "fr",
             {"n": 5, "weights": [12, 6, 10, 5, 9], "costs": [7, 2, 5, 3, 4],
              "edges": [[0, 1], [2, 3]]},
             annotation(budget=9, max_count=2, required=(3,)),
             "Le comité retient au plus 2 actions parmi les indices 0 à 4 et doit retenir l'action 3. "
             "Chaque action est représentée par une variable binaire x_i, valant 1 si elle est retenue. "
             "Le total des costs retenus est plafonné à 9. Pour toute paire de edges, les deux actions ne peuvent "
             "pas être retenues ensemble. Maximiser le total des weights retenus ; ces conditions sont exhaustives."),
    specimen("5fc7a138", "test", "en",
             {"n": 4, "weights": [14, 8, 6, 9], "costs": [2, 8, 3, 4],
              "edges": [[0, 2], [1, 3]]}, annotation(budget=7, max_count=1, forbidden=(0,)),
             "Build a kit from item indices 0, 1, 2 and 3. Item 0 is forbidden. The kit may contain no more than "
             "1 item, with total cost at most 7. An item's binary x_i is 1 exactly when it is in the kit. "
             "Both items of a pair listed in edges cannot be in the kit together. "
             "Maximize the sum of the weights in the kit; no additional constraints apply."),
    specimen("8b2e6c40", "test", "fr",
             {"n": 7, "weights": [7, 15, 8, 10, 6, 9, 4], "costs": [3, 4, 3, 6, 2, 3, 1],
              "edges": [[0, 4], [1, 3], [2, 5], [3, 6]]},
             annotation(budget=10, max_count=3, implications=((1, 4), (4, 6))),
             "Avec les candidats 0 à 6, chercher une sélection de poids total maximal, en additionnant les weights "
             "des candidats sélectionnés. Chaque x_i est binaire et indique une sélection par la valeur 1. "
             "On autorise au maximum 3 candidats et un coût total d'au plus 10. Si 1 est sélectionné alors 4 doit "
             "l'être ; si 4 est sélectionné alors 6 doit l'être. Ces implications sont à sens unique. "
             "Les paires de edges sont des exclusions mutuelles. Aucune autre règle n'est imposée."),
    specimen("1c94d7a6", "test", "en",
             {"n": 6, "weights": [6, 11, 8, 5, 9, 16], "costs": [4, 7, 5, 2, 6, 1],
              "edges": [[0, 2], [1, 3], [2, 4], [4, 5]]},
             annotation(budget=12, required=(0,), forbidden=(5,)),
             "The six experiments use indices 0 to 5 and a binary inclusion variable x_i for each. "
             "Experiment 0 must run, while experiment 5 must not run. The sum of costs for experiments that run "
             "must be at most 12. For every pair in edges, the experiments cannot both run. "
             "Maximize the sum of their selected weights. There is no other requirement."),
    specimen("6e3a08f5", "test", "fr",
             {"n": 4, "weights": [10, 5, 8, 6], "costs": [5, 2, 4, 3],
              "edges": [[0, 1], [1, 3]]},
             annotation(budget=7, required=(0,), implications=((0, 2),)),
             "Il faut choisir parmi quatre équipements d'indices 0 à 3. L'équipement 0 est obligatoire, et le choisir "
             "impose de choisir également l'équipement 2, sans réciproque. Le budget, somme des costs des équipements "
             "choisis, est au plus 7. Les variables x_i sont binaires, 1 signifiant choisi. Les deux extrémités "
             "d'une paire de edges ne peuvent être choisies ensemble. Maximiser la somme des weights choisis. "
             "Aucune autre contrainte n'est prévue.",
             "Required item 0 triggers item 2; their costs 5+4=9 exceed the budget 7."),
    specimen("f7a1d269", "test", "en",
             {"n": 5, "weights": [7, 10, 12, 6, 14], "costs": [3, 6, 1, 4, 2],
              "edges": [[0, 1], [1, 4], [2, 3]]},
             annotation(budget=9, forbidden=(2,), implications=((4, 2),)),
             "Take a subset of jobs numbered 0 through 4 to maximize its summed weights. "
             "Each job has binary x_i, with value 1 when taken. Job 2 is prohibited. Taking job 4 requires also "
             "taking job 2, with no converse requirement. Total cost of jobs taken is limited to 9. "
             "A pair in edges cannot have both jobs taken. These are the complete rules."),
    specimen("3d5b9e01", "test", "fr",
             {"n": 6, "weights": [9, 4, 11, 8, 6, 7], "costs": [4, 2, 6, 3, 5, 1],
              "edges": [[0, 2], [0, 4], [2, 4]]},
             annotation(min_count=2, max_count=3, required=(1,)),
             "La liste finale doit compter entre 2 et 3 opérations, bornes comprises, parmi les indices 0 à 5. "
             "L'opération 1 est imposée. Une variable binaire x_i vaut 1 si l'opération i est dans la liste. "
             "Chaque paire de edges interdit d'inscrire ses deux opérations. Maximiser la somme des weights "
             "des opérations inscrites. Il n'existe pas d'autre condition."),
    specimen("a063c8f2", "test", "en",
             {"n": 7, "weights": [8, 6, 10, 15, 7, 13, 5], "costs": [4, 3, 5, 2, 6, 1, 2],
              "edges": [[0, 1], [0, 2], [0, 4]]},
             annotation(min_count=3, required=(0,), forbidden=(3, 5)),
             "Choose at least 3 entries from indices 0 to 6. Entry 0 is compulsory; entries 3 and 5 are forbidden. "
             "Let each x_i be binary and equal to 1 for a chosen entry. For each pair in edges, choosing both "
             "entries is disallowed. Maximize the sum of chosen weights. No other restrictions should be added.",
             "Required item 0 excludes 1, 2 and 4; forbidden items 3 and 5 leave only 0 and 6, fewer than the required 3."),
    specimen("74f20b8d", "test", "fr",
             {"n": 4, "weights": [13, 5, 9, 7], "costs": [6, 2, 4, 3],
              "edges": [[0, 1]]},
             annotation(min_count=1, max_count=2, implications=((0, 1),)),
             "On sélectionne de 1 à 2 pièces, bornes incluses, parmi les indices 0 à 3. "
             "La sélection de la pièce 0 exige celle de la pièce 1 ; la réciproque n'est pas exigée. "
             "Les paires figurant dans edges sont des exclusions : jamais leurs deux pièces ensemble. "
             "Pour chaque pièce, x_i est binaire et vaut 1 si elle est sélectionnée. L'objectif est le maximum "
             "de la somme des weights sélectionnés, sans aucune autre restriction."),
    specimen("ce1964a7", "test", "en",
             {"n": 5, "weights": [8, 6, 11, 7, 9], "costs": [3, 4, 5, 2, 1],
              "edges": [[0, 2], [2, 4]]},
             annotation(required=(1,), forbidden=(4,), implications=((1, 3), (3, 4))),
             "For candidates indexed 0 through 4, use binary x_i=1 to mean included, and maximize the sum of "
             "included weights. Candidate 1 must be included and candidate 4 must be excluded. Inclusion of 1 "
             "requires inclusion of 3; inclusion of 3 requires inclusion of 4. Each implication is one-way. "
             "The two candidates in any pair in edges must not both be included. There are no further constraints.",
             "Required item 1 triggers 3, which triggers forbidden item 4; no binary selection satisfies all three clauses."),
    specimen("2f8c05e1", "test", "fr",
             {"n": 6, "weights": [16, 7, 10, 6, 8, 5], "costs": [2, 9, 7, 3, 5, 1],
              "edges": [[0, 3], [1, 2], [2, 4]]},
             annotation(budget=13, min_count=2, max_count=2, required=(4,), forbidden=(0,)),
             "Former un ensemble d'options d'indices 0 à 5 : l'option 4 est obligatoire et l'option 0 est interdite. "
             "L'ensemble doit contenir au moins 2 et au plus 2 options, avec une somme des costs d'au plus 13. "
             "À chaque option associer x_i dans {0,1}, où 1 indique qu'elle appartient à l'ensemble. "
             "Chaque paire de edges exclut de prendre ses deux options ensemble. Maximiser la somme des weights "
             "des options prises. Ces contraintes sont les seules à appliquer."),
    specimen("905e3b6a", "test", "en",
             {"n": 7, "weights": [11, 8, 6, 9, 7, 10, 5], "costs": [2, 5, 3, 2, 6, 3, 2],
              "edges": [[0, 1], [1, 6], [3, 4]]},
             annotation(budget=11, min_count=3, max_count=3, required=(2,), forbidden=(6,),
                        implications=((2, 5), (0, 3))),
             "Maximize the total weights selected from packages indexed 0 through 6, with one binary x_i per package "
             "and x_i=1 for selection. Package 2 is mandatory; package 6 is forbidden. Choose at least 3 and at most "
             "3 packages, and keep their total costs at or below 11. Selecting package 2 also requires package 5; "
             "selecting package 0 also requires package 3. These implications do not run backwards. Every pair "
             "in edges forbids selecting both endpoints. This list gives all constraints."),
]


def family_signature(gold):
    return "".join(f for f, key in FAMILY_KEYS.items() if gold[key] is not None and gold[key] != [])


def enumerated_feasible(data, gold):
    """Direct bit-set enumeration; independent review must use its own code."""
    feasible = []
    for bits in itertools.product((0, 1), repeat=data["n"]):
        selected = {i for i, bit in enumerate(bits) if bit}
        if any(i in selected and j in selected for i, j in data["edges"]):
            continue
        if gold["budget"] is not None and sum(data["costs"][i] for i in selected) > gold["budget"]:
            continue
        if gold["min_count"] is not None and len(selected) < gold["min_count"]:
            continue
        if gold["max_count"] is not None and len(selected) > gold["max_count"]:
            continue
        if not set(gold["required"]).issubset(selected):
            continue
        if set(gold["forbidden"]) & selected:
            continue
        if any(i in selected and j not in selected for i, j in gold["implications"]):
            continue
        feasible.append(tuple(sorted(selected)))
    return feasible


def family_drop_checks(data, gold, feasible):
    original = set(feasible)
    checks = {}
    for family, key in FAMILY_KEYS.items():
        if gold[key] is None or gold[key] == []:
            continue
        relaxed = dict(gold)
        relaxed[key] = None if key in ("budget", "min_count", "max_count") else []
        added = sorted(set(enumerated_feasible(data, relaxed)) - original)
        checks[family] = {"added_feasible_count": len(added),
                          "example_added_selection": list(added[0]) if added else None}
    return checks


def validate():
    assert len(SPECS) == 24
    assert len({s["id"] for s in SPECS}) == 24
    assert {s["split"] for s in SPECS} == {"dev", "test"}
    seen_data = set()
    for spec in SPECS:
        data, gold = spec["data"], spec["constraints"]
        assert set(data) == {"n", "weights", "costs", "edges"}
        n = data["n"]
        assert 4 <= n <= 7
        assert len(data["weights"]) == len(data["costs"]) == n
        assert all(type(v) is int and v > 0 for v in data["weights"] + data["costs"])
        assert len(data["edges"]) == len(set(tuple(e) for e in data["edges"]))
        assert 1 <= len(data["edges"]) <= 4
        assert all(0 <= i < j < n for i, j in data["edges"])
        assert data["edges"] == sorted(data["edges"])
        assert set(gold) == set(GOLD_KEYS)
        assert all(gold[key] is None or type(gold[key]) is int and gold[key] >= 0
                   for key in ("budget", "min_count", "max_count"))
        for key in ("required", "forbidden"):
            assert gold[key] == sorted(set(gold[key]))
            assert all(type(i) is int and 0 <= i < n for i in gold[key])
        assert all(0 <= i < n and 0 <= j < n and i != j for i, j in gold["implications"])
        encoded_data = json.dumps(data, sort_keys=True)
        assert encoded_data not in seen_data
        seen_data.add(encoded_data)
        feasible = enumerated_feasible(data, gold)
        assert bool(feasible) == (spec["infeasibility_reason"] is None), spec["id"]
        assert all(check["added_feasible_count"] > 0
                   for check in family_drop_checks(data, gold, feasible).values()), spec["id"]
    for split, count, per_size, per_language in (("dev", 8, 2, 4), ("test", 16, 4, 8)):
        group = [s for s in SPECS if s["split"] == split]
        assert len(group) == count
        assert all(sum(s["data"]["n"] == n for s in group) == per_size for n in range(4, 8))
        assert all(sum(s["language"] == lang for s in group) == per_language for lang in ("fr", "en"))
    dev_signatures = {family_signature(s["constraints"]) for s in SPECS if s["split"] == "dev"}
    test_signatures = {family_signature(s["constraints"]) for s in SPECS if s["split"] == "test"}
    assert dev_signatures == {"B", "L", "U", "M", "F", "I", "BL", "UF"}
    assert len(test_signatures) == 16
    assert all(len(signature) >= 3 for signature in test_signatures)
    assert not dev_signatures & test_signatures


def serialized(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_once(path, content):
    if path.exists():
        if path.read_bytes() != content:
            raise RuntimeError("Frozen corpus file differs; refuse overwrite: " + str(path))
    else:
        path.write_bytes(content)


def build():
    validate()
    public = {split: [{k: s[k] for k in ("id", "language", "intention", "data")}
                      for s in SPECS if s["split"] == split] for split in ("dev", "test")}
    private = []
    for spec in SPECS:
        data, gold = spec["data"], spec["constraints"]
        feasible = enumerated_feasible(data, gold)
        best = max((sum(data["weights"][i] for i in selection) for selection in feasible), default=None)
        optima = [list(selection) for selection in feasible
                  if sum(data["weights"][i] for i in selection) == best]
        private.append({"id": spec["id"], "split": spec["split"],
                        "constraints": gold, "families": family_signature(gold),
                        "author_check": {"feasible": bool(feasible), "feasible_count": len(feasible),
                                         "optimal_weight": best, "optimal_selections": optima,
                                         "family_drop_checks": family_drop_checks(data, gold, feasible),
                                         "deliberate_infeasibility_reason": spec["infeasibility_reason"]}})
    artifacts = {"dev_cases.json": serialized(public["dev"]),
                 "test_cases.json": serialized(public["test"]),
                 "private_gold.author.json": serialized({"schema_version": 1,
                     "warning": "PRIVATE AUTHOR ANNOTATION: never pass this file or build_corpus.py to a model",
                     "cases": private})}
    for filename, content in artifacts.items():
        write_once(ROOT / filename, content)
    hashes = {filename: hashlib.sha256(content).hexdigest() for filename, content in artifacts.items()}
    hashes["build_corpus.py"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    rows = []
    for spec, entry in zip(SPECS, private):
        check = entry["author_check"]
        rows.append("| {id} | {split} | {language} | {n} | {families} | {count} | {best} |".format(
            id=spec["id"], split=spec["split"], language=spec["language"], n=spec["data"]["n"],
            families=entry["families"], count=check["feasible_count"], best=check["optimal_weight"]))
    provenance = """# C15 — provenance du corpus, auteur

Document privé de conception, à ne jamais fournir au LLM évalué. `build_corpus.py`
contient aussi les annotations : seuls `dev_cases.json` et `test_cases.json` sont
des requêtes publiques. Aucun résultat de génération n'a été consulté pour les
concevoir. Date de création : 2026-11-14 ; commit Git de départ : `%s`.
L'arbre initial était déjà modifié ; aucun commit ni push n'est effectué ici.

Question soutenue : formuler puis réparer de véritables problèmes de sélection
pondérée, et non refuser toute extension d'un MIS. Ce corpus construit par
convenance n'est ni une distribution naturelle ni une preuve de nouveauté.

Les 24 textes ont été écrits individuellement en français ou en anglais par le
rôle d'auteur de cette session agentique, sans appel d'inférence au modèle
évalué, traduction de requêtes appariées ou lecture des corpus C11/C14. Le rôle
d'auteur a néanmoins lu les fichiers de reprise et connaît les résultats agrégés
C01–C14 et les limites de v4. Cette connaissance doit rester déclarée. Le rôle
de relecteur devra être distinct ; l'indépendance de famille de modèles ou une
annotation humaine aveugle ne sont pas établies. Aucun quota d'outil ou de
modèle n'a été rencontré par l'auteur dans cette mission.

Chaque requête définit x_i binaire, avec 1 pour la sélection de l'indice i
(indices commençant à 0), le maximum de la somme des poids sélectionnés, et les
exclusions de `edges`. Les poids et coûts sont des entiers strictement positifs,
sans unité physique revendiquée ; le budget utilise la même unité abstraite que
`costs`. Toutes les bornes sont inclusives. Une implication (i,j) signifie
x_i <= x_j et n'impose pas la réciproque. Aucune contrainte absente du texte ne
doit être ajoutée : le gold utilise null pour les trois bornes absentes, et []
pour les ensembles ou implications absents. Les paires `edges` sont non orientées.
Les textes ne promettent pas la faisabilité : une formulation infaisable demeure
une réponse correcte si elle préserve toutes les contraintes de la requête.

Développement : 8 cas, 4 FR / 4 EN, 2 par taille n=4,5,6,7. Les six familles
B (budget), L (minimum de cardinalité), U (maximum de cardinalité), M (inclusion
obligatoire), F (interdiction), I (implication) apparaissent séparément, puis
seulement deux combinaisons simples BL et UF. Tous ces cas sont faisables.
Test : 16 cas, 8 FR / 8 EN, 4 par taille, 16 signatures distinctes comportant
3 à 6 familles. Aucune signature test n'est vue au développement. Il s'agit
d'un transfert de combinaisons de clauses, pas d'un transfert de familles
mathématiques, et l'absence de signature commune n'implique pas l'indépendance
statistique. Les données et les textes des 24 requêtes sont distincts, les
identifiants opaques n'encodent ni famille ni faisabilité. Ils ne constituent
pas des traductions appariées.

Trois cas test sont volontairement infaisables : `6e3a08f5` exige 0 puis 2,
dont les coûts 5+4 dépassent 7 ; `a063c8f2` exige au moins trois éléments alors
que son obligation, ses interdictions et exclusions n'en permettent que deux ; `ce1964a7`
impose une chaîne 1 -> 3 -> 4 alors que 4 est interdit. Ils sont conservés,
sans réparation de leur intention. Le nombre de cas faisables ne sert pas
à une stratification ou une sélection après génération.

L'auto-contrôle auteur énumère les 2^n vecteurs binaires pour chaque cas, vérifie
schémas, positivité, indices, duplications de données, langues, tailles,
signatures et faisabilité prévue. Chaque graphe a entre 1 et 4 arêtes. Le contrôle
vérifie aussi que retirer chacune des familles présentes ajoute au moins une
sélection faisable, y compris pour les trois cas infaisables ; les comptes et
un témoin par famille sont privés dans `author_check.family_drop_checks`. Il
ne s'agit pas d'exiger une forme syntaxique particulière d'une formulation :
des contraintes ou lignes redondantes dans une réponse peuvent être équivalentes.
Cette qualité des instances a été ajustée avant gel et avant tout appel au modèle,
à partir des seuls ensembles faisables exacts d'auteur ; aucun filtrage selon
des résultats de LLM n'a eu lieu. Les cas faisables et infaisables doivent être
rapportés séparément lors de l'évaluation. Les optima ci-dessous sont des contrôles
exacts d'auteur, pas des performances de LLM. Une relecture indépendante doit
réextraire les clauses du texte et recalculer les ensembles faisables sans
importer ce script. Aucun vérificateur C15 futur ni sortie d'inférence n'est lu.
Sources : conception synthétique locale, sans source documentaire externe.

Commande exécutée à la racine du workspace :
`python3 runs/20261114-c15-formulation-repair/build_corpus.py`.
La génération des fichiers est déterministe, sans aléa ni seed caché. Une
réexécution identique les contrôle ; une divergence refuse de les écraser.
Les fichiers publics, le gold et le script sont figés par les empreintes
ci-dessous, avant tout appel au LLM. Le script doit rester privé même s'il est
conservé pour reproduction. Ces contrôles ne remplacent pas la revue distincte.

| ID | split | langue | n | familles privées | sélections faisables | optimum |
| --- | --- | --- | --- | --- | --- | --- |
%s

Empreintes SHA-256 :

%s
""" % (START_COMMIT, "\n".join(rows), "\n".join("- `%s`: `%s`" % item for item in sorted(hashes.items())))
    write_once(ROOT / "corpus-provenance.md", provenance.encode("utf-8"))
    print(json.dumps({"status": "author_checks_passed", "dev": 8, "test": 16,
                      "infeasible_test": 3, "sha256": hashes}, indent=2))


if __name__ == "__main__":
    build()
