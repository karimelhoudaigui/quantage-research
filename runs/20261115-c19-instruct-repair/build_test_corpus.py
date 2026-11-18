#!/usr/bin/env python3
"""Private C19 test author builder. Never pass this script or gold to an LLM.

Uses public history for collisions and C15/C16 gold only for the inventory of
previously exposed family sets. No inference, scorer, production verifier,
response, metric or new-test result is imported or read.
"""

import hashlib
import itertools
import json
from pathlib import Path
import random
import runpy


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
C16_BUILDER = ROOT / "runs/20261115-c16-quantized-repair/build_corpus.py"
C16_BUILDER_SHA256 = "f31f5cbd322a282bb1847198f30e5a10a59d7d714fb1cb2fec6a12d003843ae7"
KEYS = {"B": "budget", "F": "forbidden", "I": "implications", "L": "min_count",
        "M": "required", "U": "max_count"}
EXPECTED_REMAINING = ["BFILM", "BFIM", "BFIMU", "BFIU", "FILM", "FILMU",
                      "FILU", "FIMU", "FLMU", "ILMU"]
INFEASIBLE = {("FILM", "en"), ("FILMU", "fr"), ("ILMU", "fr")}
SIZE_SWAPS = {("BFIMU", "en"): 5, ("FIMU", "en"): 4}
MAX_ATTEMPTS_PER_CASE = 50000


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def empty():
    return {"budget": None, "min_count": None, "max_count": None,
            "required": [], "forbidden": [], "implications": []}


def signature(spec):
    return "".join(family for family, key in KEYS.items() if spec[key] is not None and spec[key] != [])


def feasible_mask(data, spec, mask, drop=None):
    chosen = {i for i in range(data["n"]) if (mask >> i) & 1}
    if any(i in chosen and j in chosen for i, j in data["edges"]):
        return False
    if drop != "B" and spec["budget"] is not None and sum(data["costs"][i] for i in chosen) > spec["budget"]:
        return False
    if drop != "L" and spec["min_count"] is not None and len(chosen) < spec["min_count"]:
        return False
    if drop != "U" and spec["max_count"] is not None and len(chosen) > spec["max_count"]:
        return False
    if drop != "M" and not set(spec["required"]) <= chosen:
        return False
    if drop != "F" and set(spec["forbidden"]) & chosen:
        return False
    if drop != "I" and any(i in chosen and j not in chosen for i, j in spec["implications"]):
        return False
    return True


def author_checks(data, spec, want_infeasible):
    domain = range(1 << data["n"])
    accepted = {mask for mask in domain if feasible_mask(data, spec, mask)}
    if bool(accepted) == want_infeasible:
        return None
    drops = {}
    for family in signature(spec):
        additional = sorted(mask for mask in domain if mask not in accepted
                            and feasible_mask(data, spec, mask, drop=family))
        if not additional:
            return None
        drops[family] = {"additional_count": len(additional), "witness_mask": additional[0],
                         "witness": [(additional[0] >> i) & 1 for i in range(data["n"])]}
    values = {mask: sum(weight for i, weight in enumerate(data["weights"]) if (mask >> i) & 1)
              for mask in accepted}
    optimum = max(values.values(), default=None)
    return {"feasible_count": len(accepted), "feasible_masks": sorted(accepted), "optimum": optimum,
            "optimal_masks": sorted(mask for mask, value in values.items() if value == optimum),
            "family_drop_checks": drops, "assignments": 1 << data["n"]}


def historical_inventory():
    public = []
    gold = []
    paths = []
    for cycle in ("20261114-c15-formulation-repair", "20261115-c16-quantized-repair"):
        base = ROOT / "runs" / cycle
        for split in ("dev", "test"):
            path = base / (split + "_cases.json")
            public.extend(json.loads(path.read_text()))
            paths.append(path)
        path = base / "gold.json"
        annotated = json.loads(path.read_text())
        gold.extend(annotated["cases"] if isinstance(annotated, dict) else annotated)
        paths.append(path)
    exposed = {signature(row["constraints"]) for row in gold}
    all_combinations = {"".join(group) for size in range(3, 7)
                        for group in itertools.combinations(KEYS, size)}
    remaining = sorted(all_combinations - exposed)
    if remaining != EXPECTED_REMAINING:
        raise ValueError("historical signature inventory changed: " + repr(remaining))
    return public, exposed, remaining, {str(path.relative_to(ROOT)): sha256(path) for path in paths}


def numerical_data(rng, n):
    return {"n": n, "weights": [rng.randint(17, 61) for _ in range(n)],
            "costs": [rng.randint(13, 39) for _ in range(n)]}


def candidate(rng, n, families, want_infeasible):
    data, spec = numerical_data(rng, n), empty()
    if not want_infeasible and families == "BFIMU" and n == 5:
        # Positive costs in the prescribed narrow range make a uniform search
        # inefficient here. These witnesses guarantee B and U remain distinct.
        base_costs = [rng.randint(13, 39), rng.randint(13, 16), rng.randint(13, 16),
                      rng.randint(35, 39), rng.randint(13, 26)]
        permutation = rng.sample(range(n), n)
        data["costs"] = [0] * n
        for i, cost in enumerate(base_costs):
            data["costs"][permutation[i]] = cost
        safe_edges = [(1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
        selected_edges = rng.sample(safe_edges, rng.randint(1, 4))
        data["edges"] = sorted(sorted([permutation[i], permutation[j]]) for i, j in selected_edges)
        spec.update(budget=sum(base_costs[:3]), max_count=2,
                    required=[permutation[0]], forbidden=[permutation[4]],
                    implications=[[permutation[1], permutation[2]]])
        return data, spec, permutation
    if want_infeasible:
        if families == "FILM":
            assert n == 6
            base_edges = [[0, 2], [3, 4]]
            spec.update(required=[0], forbidden=[5], implications=[[1, 2]], min_count=3)
        elif families == "FILMU":
            assert n == 5
            base_edges = [[2, 3], [0, 4]]
            spec.update(required=[0], forbidden=[3], implications=[[1, 2], [2, 1]],
                        min_count=2, max_count=2)
        elif families == "ILMU":
            assert n == 5
            base_edges = [[0, 3], [0, 4]]
            spec.update(required=[0], implications=[[1, 2], [2, 1]], min_count=2, max_count=2)
        else:
            raise ValueError("unregistered infeasible family set")
        permutation = rng.sample(range(n), n)
        data["edges"] = sorted(sorted([permutation[i], permutation[j]]) for i, j in base_edges)
        for key in ("required", "forbidden"):
            spec[key] = sorted(permutation[i] for i in spec[key])
        spec["implications"] = sorted([permutation[i], permutation[j]] for i, j in spec["implications"])
        return data, spec, permutation
    data["edges"] = sorted(sorted(pair) for pair in rng.sample(
        list(itertools.combinations(range(n), 2)), rng.randint(1, 4)))
    if "B" in families:
        spec["budget"] = rng.randint(min(data["costs"]), sum(data["costs"]) - 1)
    if "L" in families:
        spec["min_count"] = rng.randint(1, max(1, n - 2))
    if "U" in families:
        spec["max_count"] = rng.randint(spec["min_count"] or 1, n - 1)
    if "M" in families:
        spec["required"] = [rng.randrange(n)]
    if "F" in families:
        spec["forbidden"] = [rng.randrange(n)]
    if "I" in families:
        spec["implications"] = [rng.sample(range(n), 2)]
    return data, spec, None


def check_original_template_correction():
    """Retain the falsification of the supplied one-direction templates."""
    for families, edges, forbidden in (("FILMU", [[2, 3], [0, 4]], [3]),
                                        ("ILMU", [[0, 3], [0, 4]], [])):
        data = {"n": 5, "weights": [17] * 5, "costs": [13] * 5, "edges": edges}
        original = empty()
        original.update(required=[0], forbidden=forbidden, implications=[[1, 2]], min_count=2, max_count=2)
        assert feasible_mask(data, original, (1 << 0) | (1 << 2)), families
        original["implications"].append([2, 1])
        checks = author_checks(data, original, True)
        assert checks is not None and set(checks["family_drop_checks"]) == set(families)


def render(index, language, data, spec, c16_request):
    # Exactly C16 wording for one implication, except the C19 batch reference.
    text = c16_request(index, language, data, spec).replace("C16-", "C19-")
    if len(spec["implications"]) > 1:
        i, j = spec["implications"][0]
        if language == "fr":
            old = "Retenir l'indice " + str(i) + " impose aussi de retenir l'indice " + str(j) + " ; la réciproque n'est pas imposée."
            explicit = " ".join("Retenir l'indice " + str(a) + " impose aussi de retenir l'indice " + str(b) + "."
                                for a, b in spec["implications"])
        else:
            old = "Selecting entry " + str(i) + " requires also selecting entry " + str(j) + "; the converse is not required."
            explicit = " ".join("Selecting entry " + str(a) + " requires also selecting entry " + str(b) + "."
                                for a, b in spec["implications"])
        assert text.count(old) == 1
        text = text.replace(old, explicit)
    return text


def write_frozen(path, content):
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError("refuse to alter a frozen author artifact: " + str(path))
    else:
        path.write_bytes(content)


def main():
    if sha256(C16_BUILDER) != C16_BUILDER_SHA256:
        raise ValueError("C16 author renderer differs from its pinned source")
    c16_request = runpy.run_path(str(C16_BUILDER))["request"]
    check_original_template_correction()
    old_public, exposed, remaining, historical_pins = historical_inventory()
    old_ids = {row["id"] for row in old_public}
    graphs = {(row["data"]["n"], digest(row["data"]["edges"])) for row in old_public}
    data_digests = {digest(row["data"]) for row in old_public}
    old_texts = {row["intention"] for row in old_public}
    initial_graphs = graphs.copy()
    cases, gold = [], []
    for group, families in enumerate(remaining):
        for language_index, language in enumerate(("fr", "en")):
            index = 2 * group + language_index
            n = 4 + ((group + 2 * language_index) % 4)
            n = SIZE_SWAPS.get((families, language), n)
            want_infeasible = (families, language) in INFEASIBLE
            design_seed = 2026111900 + index
            rng = random.Random(design_seed)
            rejected_graphs = rejected_activity = 0
            for attempt in range(1, MAX_ATTEMPTS_PER_CASE + 1):
                data, spec, permutation = candidate(rng, n, families, want_infeasible)
                graph = (n, digest(data["edges"]))
                if graph in graphs or digest(data) in data_digests:
                    rejected_graphs += 1
                    continue
                checks = author_checks(data, spec, want_infeasible)
                if checks is None:
                    rejected_activity += 1
                    continue
                break
            else:
                raise RuntimeError("bounded author search exhausted for " + families + " / " + language)
            assert signature(spec) == families
            identifier = hashlib.sha256(("QuantAge-C19-new-test-" + str(index)).encode()).hexdigest()[:12]
            text = render(index, language, data, spec, c16_request)
            assert identifier not in old_ids and text not in old_texts
            cases.append({"id": identifier, "language": language, "intention": text, "data": data})
            gold.append({"id": identifier, "split": "test", "constraints": spec, "families": families,
                         "intended_infeasible": want_infeasible,
                         "author_check": dict(checks, design_seed=design_seed, attempts=attempt,
                                              rejected_graph_or_data_collisions=rejected_graphs,
                                              rejected_feasibility_or_family_activity=rejected_activity,
                                              base_index_permutation=permutation)})
            old_ids.add(identifier)
            graphs.add(graph)
            data_digests.add(digest(data))
            old_texts.add(text)
    assert len(cases) == len(gold) == 20
    assert {row["families"] for row in gold}.isdisjoint(exposed)
    assert all(sum(row["families"] == families for row in gold) == 2 for families in remaining)
    assert all(sum(row["data"]["n"] == n for row in cases) == 5 for n in range(4, 8))
    assert sum(row["language"] == "fr" for row in cases) == 10
    assert sum(row["intended_infeasible"] for row in gold) == 3
    assert len(graphs) - len(initial_graphs) == 20
    for case, row in zip(cases, gold):
        n, data = case["data"]["n"], case["data"]
        assert 1 <= len(data["edges"]) <= 4
        assert all(0 <= a < b < n for a, b in data["edges"])
        assert all(17 <= weight <= 61 for weight in data["weights"])
        assert all(13 <= cost <= 39 for cost in data["costs"])
        assert author_checks(data, row["constraints"], row["intended_infeasible"]) is not None
    artifacts = {"test_cases.json": (json.dumps(cases, ensure_ascii=False, indent=2) + "\n").encode(),
                 "private_gold.author.json": (json.dumps(gold, ensure_ascii=False, indent=2) + "\n").encode()}
    hashes = {name: hashlib.sha256(content).hexdigest() for name, content in artifacts.items()}
    hashes["build_test_corpus.py"] = sha256(__file__)
    lines = [
        "# C19 — provenance privée du test auteur", "",
        "Création et gel auteur : 2026-11-15, avant toute génération de test C19.",
        "Ce fichier, build_test_corpus.py et private_gold.author.json restent privés.",
        "Seul test_cases.json est communiqué au LLM et au relecteur public-only.", "",
        "## Inventaire et construction", "",
        "Inventaire automatique des contrats structurés gold.json C15 et C16, tous splits :",
        "les 10 signatures de taille 3..6 absentes de leur union sont exactement :",
        ", ".join(remaining) + ". Deux nouvelles instances par signature, une FR et une EN.",
        "Ce sont des signatures globalement réservées, pas des problèmes mathématiques nouveaux.",
        "Tailles initiales : n_FR=4+(j mod4), n_EN=4+((j+2) mod4), puis échange",
        "approuvé BFIMU_EN : 4→5 et FIMU_EN : 5→4 ; cinq cas par n=4,5,6,7.",
        "Poids entiers 17..61, coûts entiers 13..39, une à quatre arêtes, indices zéro.",
        "Les 20 données, textes et IDs sont distincts de l'historique et entre eux.",
        "Les 20 graphes étiquetés normalisés (n,edges) sont tous distincts entre eux et",
        "de ceux des 48 publics C15/C16 ; aucune unicité à isomorphisme près n'est affirmée.", "",
        "Recherche pseudo-aléatoire déterministe, un seed par cas, au plus 50000 candidats",
        "par cas. Rejet uniquement sur collision, faisabilité prévue et activité exacte",
        "de chaque famille : retirer une famille doit ajouter une affectation faisable.",
        "Les comptes, témoins et optima viennent d'une énumération des 2^n masques.",
        "Ce filtrage mathématique d'auteur ne mesure aucune performance de modèle.", "",
        "## Réfutations conservées et corrections avant génération", "",
        "La première recherche bornée a épuisé 50000 essais pour BFIMU_EN à n4",
        "sans écrire de public. Ce cas faisable ne peut rendre B et U essentiels :",
        "M oblige au moins un élément et F en interdit au moins un, donc au plus",
        "trois indices sont autorisés. U=1 ne permet que le singleton obligatoire",
        "s'il existe, donc B est redondant. Pour U=2, l'activité de U exige que les",
        "trois autorisés passent B ; leurs coûts étant positifs, B accepte alors",
        "tous leurs sous-ensembles et est redondant. U≥3 est lui-même redondant.",
        "L'intégrateur a approuvé avant génération l'échange n de BFIMU_EN et FIMU_EN",
        "décrit ci-dessus. Aucun résultat LLM n'a motivé ce changement de plan.", "",
        "Une deuxième recherche uniforme, à n5 après correction, a aussi atteint",
        "le plafond de50000 pour BFIMU_EN. Le générateur final utilise pour BFIMU n5",
        "une construction faisable ciblée : M0,F4,U2,I1→2, coûts1/2 en13..16, coût3",
        "en35..39, coût0 en13..39, coût4 en13..26 et B=cost0+cost1+cost2, puis",
        "permutation. Les témoins de retrait sont U:{0,1,2}, B:{0,3}, I:{0,1},",
        "F:{0,4}, M:∅. Les arêtes sont tirées parmi (1,3),(1,4),(2,3),(2,4),(3,4)",
        "avant permutation pour préserver ces témoins. Chaque candidat est néanmoins",
        "recontrôlé exactement et rejeté en cas de collision. Ces deux recherches",
        "avortées précèdent le gel et n'ont produit aucune donnée de génération LLM.", "",
        "Les gabarits initialement transmis FILMU/ILMU avec seulement I={1→2}, M={0}",
        "et L=U=2 étaient faisables : {0,2} est un contre-exemple, aussi après ajout de",
        "l'indice 4 bloqué par l'arête (0,4). Cette réfutation n'est pas effacée.",
        "Correction approuvée par l'intégrateur avant génération : I={1→2,2→1}.",
        "Le bloc indivisible {1,2} crée alors le trou de cardinalité requis.",
        "FILMU_FR (n5) : M0,F3,L=U2,E={(2,3),(0,4)}, cycle1↔2 avant permutation.",
        "ILMU_FR (n5) : M0,L=U2,E={(0,3),(0,4)}, cycle1↔2 avant permutation.",
        "FILM_EN (n6) conserve le gabarit valide M0,F5,I1→2,L3,E={(0,2),(3,4)}.",
        "Ces trois cas seuls sont infaisables. Tous ont chaque famille essentielle ;",
        "les permutations d'indices sont privées dans le gold. Aucune arête n'a été",
        "ajoutée aux trois gabarits minimaux, et les témoins sont recalculés exactement.", "",
        "## Texte, connaissance préalable et séparation", "",
        "Le renderer request() du builder C16 est importé à empreinte fixe, sans appeler",
        "son main. Son texte est conservé, à remplacement du repère C16- par C19- près.",
        "Extension mécanique pour les deux cycles : toutes les implications sont",
        "verbalisées explicitement et la mention 'réciproque non imposée' est retirée.",
        "Les 18 autres cas reprennent exactement le renderer à une implication.",
        "Cette correction garantit que le texte expose tout le contrat ; elle n'est",
        "fondée ni sur une réponse LLM ni sur une sélection de performances.", "",
        "L'auteur connaît les bilans agrégés C15–C18 et le développement C19 communiqués",
        "par l'intégrateur/research/continuation-c19.md. Il a auparavant conçu C15 et",
        "travaillé sur le driver C16. Aucune nouvelle trace ou métrique de test C19",
        "n'est lue ; aucun appel modèle ou code de vérification de production n'est",
        "exécuté/importé ici. Le corpus est synthétique, pas une population naturelle.",
        "Une relecture distincte réextraira les contrats depuis les seuls publics.",
        "Indépendance de modèle/humaine non démontrée. Aucun quota observé à cette reprise.", "",
        "Commande : python3 -B runs/20261115-c19-instruct-repair/build_test_corpus.py",
        "Une répétition identique contrôle les mêmes octets ; aucune divergence n'est écrasée.", "",
        "| ID | Langue | n | Familles privées | Faisables | Optimum | Essais auteur |",
        "|---|---|---:|---|---:|---:|---:|",
    ]
    for case, row in zip(cases, gold):
        check = row["author_check"]
        lines.append("| {} | {} | {} | {} | {} | {} | {} |".format(
            case["id"], case["language"], case["data"]["n"], row["families"],
            check["feasible_count"], check["optimum"], check["attempts"]))
    lines.extend(["", "Empreintes des entrées historiques et du renderer :", ""])
    for name, value in sorted({**historical_pins, str(C16_BUILDER.relative_to(ROOT)): C16_BUILDER_SHA256}.items()):
        lines.append("- " + name + ": " + value)
    lines.extend(["", "Empreintes du gel auteur avant inférence :", ""])
    for name, value in sorted(hashes.items()):
        lines.append("- " + name + ": " + value)
    artifacts["test-corpus-provenance.md"] = ("\n".join(lines) + "\n").encode()
    # Validate every existing artifact before writing any new one.
    for name, content in artifacts.items():
        if (HERE / name).exists() and (HERE / name).read_bytes() != content:
            raise ValueError("different frozen author artifact: " + name)
    for name, content in artifacts.items():
        write_frozen(HERE / name, content)
    print(json.dumps({"status": "author_checks_passed", "test_cases": 20,
                      "signatures": remaining, "infeasible": 3,
                      "author_attempts": sum(row["author_check"]["attempts"] for row in gold),
                      "sha256": hashes}, indent=2))


if __name__ == "__main__":
    main()
