"""Private C16 author builder; never supply this file or its gold to the LLM.

Seeded numerical design uses only author finite-set conditions before inference,
not scores or responses. No repair/verifier/inference module is imported.
Public C15 requests are read only to exclude exact request/data/graph collisions.
"""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FAMILIES = "BLUMFI"
KEY = dict(zip(FAMILIES, ("budget", "min_count", "max_count", "required", "forbidden", "implications")))
OLD_TEST = {"BLU", "BLM", "BLF", "BLI", "BUM", "BUF", "BUI", "BMF",
            "BMI", "BFI", "LUM", "LMF", "LUI", "MFI", "BLUMF", "BLUMFI"}
PLAN = [
    ("dev",4,"fr","B",False), ("dev",5,"en","L",False),
    ("dev",6,"fr","U",False), ("dev",7,"en","M",False),
    ("dev",4,"en","F",False), ("dev",5,"fr","I",False),
    ("dev",6,"en","BI",False), ("dev",7,"fr","LM",False),
    ("test",4,"fr","LUF",False), ("test",4,"en","UMI",True),
    ("test",4,"fr","LFI",True), ("test",4,"en","UMF",False),
    ("test",5,"fr","LMI",True), ("test",5,"en","UFI",False),
    ("test",5,"fr","BLUM",False), ("test",5,"en","BLUF",False),
    ("test",6,"fr","BLUI",False), ("test",6,"en","BLMF",False),
    ("test",6,"fr","BLMI",False), ("test",6,"en","BLFI",False),
    ("test",7,"fr","BUMF",False), ("test",7,"en","BUMI",False),
    ("test",7,"fr","BLUMI",False), ("test",7,"en","BLUFI",False),
]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def empty():
    return {"budget":None,"min_count":None,"max_count":None,"required":[],"forbidden":[],"implications":[]}


def feasible(data, spec, bits, drop=None):
    chosen = {i for i, value in enumerate(bits) if value}
    if any(i in chosen and j in chosen for i,j in data["edges"]): return False
    if drop != "B" and spec["budget"] is not None and sum(data["costs"][i] for i in chosen)>spec["budget"]: return False
    if drop != "L" and spec["min_count"] is not None and len(chosen)<spec["min_count"]: return False
    if drop != "U" and spec["max_count"] is not None and len(chosen)>spec["max_count"]: return False
    if drop != "M" and any(i not in chosen for i in spec["required"]): return False
    if drop != "F" and any(i in chosen for i in spec["forbidden"]): return False
    if drop != "I" and any(i in chosen and j not in chosen for i,j in spec["implications"]): return False
    return True


def check(data, spec, signature, want_infeasible):
    points = list(itertools.product((0,1), repeat=data["n"]))
    selected = {x for x in points if feasible(data,spec,x)}
    if (not selected) != want_infeasible: return None
    drops = {}
    for family in signature:
        additional = sorted(x for x in points if x not in selected and feasible(data,spec,x,drop=family))
        if not additional: return None
        drops[family] = {"additional_count":len(additional),"witness":list(additional[0])}
    values = [(sum(w*x for w,x in zip(data["weights"], bits)), bits) for bits in selected]
    optimum = max((value for value,_ in values), default=None)
    return {"feasible_count":len(selected),"optimum":optimum,
            "optimizers":[list(x) for value,x in sorted(values) if value==optimum],
            "family_drop_checks":drops,"assignments":len(points)}


def candidate(rng, n, signature, infeasible_case):
    data = {"n":n,"weights":[rng.randint(17,61) for _ in range(n)],
            "costs":[rng.randint(13,39) for _ in range(n)]}
    spec = empty()
    if infeasible_case:
        permutation = rng.sample(range(n),n)
        if signature == "UMI":
            a,b,c,d = permutation
            edges = [[c,d]]
            spec.update(max_count=1,required=[a],implications=[[a,b]])
        elif signature == "LFI":
            a,b,c,d = permutation
            edges = [[c,d]]
            spec.update(min_count=2,forbidden=[a],implications=[[b,a]])
        elif signature == "LMI":
            a,b,c,d,e = permutation
            edges = [[b,c],[b,d],[a,e]]
            spec.update(min_count=3,required=[a],implications=[[a,b]])
        else:
            raise ValueError("unregistered infeasible design")
    else:
        edges = rng.sample(list(itertools.combinations(range(n),2)),rng.randint(1,4))
        if "B" in signature: spec["budget"] = rng.randint(min(data["costs"]),sum(data["costs"])-1)
        if "L" in signature: spec["min_count"] = rng.randint(1,max(1,n-2))
        if "U" in signature:
            lower = spec["min_count"] or 1
            spec["max_count"] = rng.randint(lower,n-1)
        if "M" in signature: spec["required"] = [rng.randrange(n)]
        if "F" in signature: spec["forbidden"] = [rng.randrange(n)]
        if "I" in signature: spec["implications"] = [rng.sample(range(n),2)]
    data["edges"] = sorted(sorted(pair) for pair in edges)
    return data,spec


def request(index, language, data, spec):
    n = data["n"]
    if language == "fr":
        nouns = ("campagnes","dossiers","expériences","lots","projets","modules")
        noun = nouns[index % len(nouns)]
        beginning = [
            "Composer une sélection pour le lot de décision C16-" + str(index+1) + ".",
            "Le comité prépare le programme C16-" + str(index+1) + ".",
            "On doit arrêter le portefeuille C16-" + str(index+1) + ".",
            "La prochaine campagne porte le repère C16-" + str(index+1) + ".",
        ][index % 4]
        pieces = [beginning, "Les " + str(n) + " " + noun + " ont pour indices 0 à " + str(n-1) + ".",
                  "Définir x_i dans {0,1}, où 1 indique que l'indice i est retenu.",
                  "L'objectif est le maximum de la somme des weights des éléments retenus.",
                  "Chaque paire de edges est une incompatibilité : ses deux indices ne peuvent pas être retenus ensemble."]
        clauses = []
        if spec["budget"] is not None: clauses.append("Le coût cumulé, somme des costs retenus, est limité à " + str(spec["budget"]) + ", borne incluse.")
        if spec["min_count"] is not None: clauses.append("Le nombre d'éléments retenus est au moins " + str(spec["min_count"]) + ".")
        if spec["max_count"] is not None: clauses.append("Le nombre d'éléments retenus ne dépasse pas " + str(spec["max_count"]) + ".")
        if spec["required"]: clauses.append("L'indice " + str(spec["required"][0]) + " doit obligatoirement être retenu.")
        if spec["forbidden"]: clauses.append("L'indice " + str(spec["forbidden"][0]) + " est interdit dans la sélection.")
        if spec["implications"]:
            i,j = spec["implications"][0]
            clauses.append("Retenir l'indice " + str(i) + " impose aussi de retenir l'indice " + str(j) + " ; la réciproque n'est pas imposée.")
        ending = "Les conditions énumérées sont exhaustives; aucune autre restriction n'est demandée."
    else:
        beginning = ["Prepare decision batch C16-" + str(index+1) + ".",
                     "The committee is assembling portfolio C16-" + str(index+1) + ".",
                     "Plan the next selection under reference C16-" + str(index+1) + ".",
                     "The planning file is C16-" + str(index+1) + "."][index % 4]
        pieces = [beginning, "There are " + str(n) + " entries indexed from 0 to " + str(n-1) + ".",
                  "Assign a binary x_i to every entry, with x_i=1 exactly when entry i is selected.",
                  "Maximize the sum of the selected weights.",
                  "Every pair in edges is an incompatibility: never select both of its endpoints."]
        clauses = []
        if spec["budget"] is not None: clauses.append("The sum of selected costs is at most " + str(spec["budget"]) + ", including the bound.")
        if spec["min_count"] is not None: clauses.append("Select no fewer than " + str(spec["min_count"]) + " entries.")
        if spec["max_count"] is not None: clauses.append("Select no more than " + str(spec["max_count"]) + " entries.")
        if spec["required"]: clauses.append("Entry " + str(spec["required"][0]) + " is compulsory.")
        if spec["forbidden"]: clauses.append("Entry " + str(spec["forbidden"][0]) + " is forbidden.")
        if spec["implications"]:
            i,j = spec["implications"][0]
            clauses.append("Selecting entry " + str(i) + " requires also selecting entry " + str(j) + "; the converse is not required.")
        ending = "These are all the requirements; impose no additional restriction."
    # Fixed rotations vary clause order without selecting by model outputs.
    offset = index % len(clauses)
    return " ".join(pieces + clauses[offset:] + clauses[:offset] + [ending])


def write_identical(path, contents):
    if path.exists() and path.read_text() != contents:
        raise ValueError("refuse to overwrite a different frozen corpus artifact: " + str(path))
    path.write_text(contents)


def main():
    old_public = []
    for split in ("dev","test"):
        old_public += json.loads((ROOT / "runs/20261114-c15-formulation-repair" / (split+"_cases.json")).read_text())
    graph_signatures = {(row["data"]["n"],digest(row["data"]["edges"])) for row in old_public}
    old_data = {digest(row["data"]) for row in old_public}
    old_text = {row["intention"] for row in old_public}
    public = {"dev":[],"test":[]}
    gold = []
    for index,(split,n,language,signature,want_infeasible) in enumerate(PLAN):
        rng = random.Random(2026111500 + index)
        for attempt in range(1,50001):
            data,spec = candidate(rng,n,signature,want_infeasible)
            graph = (n,digest(data["edges"]))
            if graph in graph_signatures or digest(data) in old_data: continue
            checks = check(data,spec,signature,want_infeasible)
            if checks is not None: break
        else:
            raise RuntimeError("finite author search exhausted for " + signature)
        identity = hashlib.sha256(("C16-public-case-" + str(index)).encode()).hexdigest()[:12]
        text = request(index,language,data,spec)
        if text in old_text: raise ValueError("historical text collision")
        row = {"id":identity,"language":language,"intention":text,"data":data}
        public[split].append(row)
        gold.append({"id":identity,"split":split,"constraints":spec,"families":signature,
                     "author_check":dict(checks,design_seed=2026111500+index,attempts=attempt),
                     "intended_infeasible":want_infeasible})
        graph_signatures.add(graph)
        old_data.add(digest(data))
        old_text.add(text)
    test_signatures = {row["families"] for row in gold if row["split"]=="test"}
    assert len(test_signatures)==16 and not test_signatures & OLD_TEST
    assert all(3<=len(signature)<=6 for signature in test_signatures)
    assert sum(row["intended_infeasible"] for row in gold if row["split"]=="test")==3
    assert all(not row["intended_infeasible"] for row in gold if row["split"]=="dev")
    for split,count in (("dev",8),("test",16)):
        assert len(public[split])==count
        assert sum(row["language"]=="fr" for row in public[split])==count//2
        assert all(sum(row["data"]["n"]==n for row in public[split])==count//4 for n in range(4,8))
    for split in public:
        write_identical(HERE/(split+"_cases.json"),json.dumps(public[split],ensure_ascii=False,indent=2)+"\n")
    write_identical(HERE/"private_gold.author.json",json.dumps(gold,ensure_ascii=False,indent=2)+"\n")
    lines = [
        "# C16 — provenance privée du corpus auteur", "",
        "Création : 2026-11-15. Avant toute inférence C16. Aucun brut du test C15 lu.",
        "Le rôle auteur a lu la conception et les diagnostics agrégés C15; les requêtes publiques",
        "C15 sont lues seulement pour les contrôles de collision. Le code de vérification, les",
        "réponses LLM, les prompts/grammaires C16 et le gold relecteur ne sont pas importés.",
        "Les textes sont des compositions synthétiques déterministes FR/EN, et non 24 textes",
        "rédigés indépendamment ou des observations naturelles. Le filtrage des paramètres",
        "repose exclusivement sur les ensembles faisables exacts avant toute génération.",
        "Le seed de conception et le nombre d'essais sont conservés dans le gold auteur.",
        "",
        "8 dev : 4 FR/4 EN, deux par n=4..7, six familles seules et doubles BI/LM.",
        "16 test : 8 FR/8 EN, quatre par n=4..7; 16 signatures inédites par rapport au",
        "test C15, de 3 à 5 familles (dans l'intervalle demandé 3..6). L'unique signature",
        "à six familles était déjà présente en C15 et n'est donc pas réutilisée.",
        "Les graphes normalisés (n,edges) sont distincts entre les 24 cas et de tous ceux",
        "du corpus C15, de même que les données complètes et les textes. Arêtes : 1..4.",
        "Poids : 17..61; coûts : 13..39. Unités abstraites, bornes inclusives, indices à zéro.",
        "Les implications sont à sens unique. Les familles absentes restent absentes.",
        "",
        "Exactement trois tests sont infaisables. Pour chaque famille présente, même dans",
        "ces cas, supprimer toute cette famille ajoute une affectation faisable. Les",
        "comptes et témoins sont dans author_check.family_drop_checks; les optima sont",
        "des contrôles exacts d'auteur, jamais des performances de LLM. Les exclusions",
        "sont dans edges; aucun encodage matériel/QPU n'est revendiqué.",
        "",
        "Ce fichier, build_corpus.py et private_gold.author.json sont privés pour l'expérience.",
        "Seuls dev_cases.json et test_cases.json sont fournis au LLM et au relecteur aveugle.",
        "Une revue distincte doit extraire les clauses du texte sans importer ce générateur.",
        "Indépendance humaine ou de famille de modèles non établie; quota auteur non rencontré.",
        "",
        "Commande : python3 runs/20261115-c16-quantized-repair/build_corpus.py",
        "Répétition : mêmes fichiers ou erreur avant remplacement d'un artefact différent.",
        "",
        "| ID | Split | Langue | n | Familles | Faisables | Optimum | Essais auteur |",
        "|---|---|---|---:|---|---:|---:|---:|",
    ]
    for row in gold:
        case = next(case for case in public[row["split"]] if case["id"]==row["id"])
        c = row["author_check"]
        lines.append("| {} | {} | {} | {} | {} | {} | {} | {} |".format(
            row["id"],row["split"],case["language"],case["data"]["n"],row["families"],
            c["feasible_count"],c["optimum"],c["attempts"]))
    lines.extend(["","Empreintes avant inférence :",""])
    for name in ("build_corpus.py","dev_cases.json","test_cases.json","private_gold.author.json"):
        lines.append("- "+name+": "+hashlib.sha256((HERE/name).read_bytes()).hexdigest())
    write_identical(HERE/"corpus-provenance.md","\n".join(lines)+"\n")
    print(json.dumps({"dev":8,"test":16,"test_infeasible":3,
                      "test_signatures":sorted(test_signatures),"author_attempts":sum(row["author_check"]["attempts"] for row in gold)}))


if __name__=="__main__": main()
