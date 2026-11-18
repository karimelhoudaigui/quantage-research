"""Bounded synthetic C19 source checks: no model, socket, gold or test corpus."""
import argparse
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quantage import repair_llama_linear as driver
from quantage import repair_study_c19 as study
from quantage.repair_feedback import SCHEMA_MESSAGE, validate_feedback
from quantage.repair_language import parse_proposal
from quantage.repair_model import model_feasible


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT/"research/c19-preflight-review.json")
    args = parser.parse_args()
    started = time.perf_counter()
    checks = {}
    n = 7
    expressions = [
        ("exclusion", "x0+x1<=1", lambda x: x[0]+x[1] <= 1),
        ("budget", "17*x0+23*x1+31*x2+13*x3+19*x4+29*x5+37*x6<=83",
         lambda x: sum(a*b for a,b in zip([17,23,31,13,19,29,37],x)) <= 83),
        ("minimum", "x0+x1+x2+x3+x4+x5+x6>=3", lambda x: sum(x) >= 3),
        ("maximum", "x0+x1+x2+x3+x4+x5+x6<=4", lambda x: sum(x) <= 4),
        ("required", "x3==1", lambda x: x[3] == 1),
        ("forbidden", "x5==0", lambda x: x[5] == 0),
        ("implication", "x2-x6<=0", lambda x: not x[2] or x[6]),
    ]
    for name, expression, expected in expressions:
        candidate = {"formulation":"binary_ilp","variables":list(range(n)),
                     "sense":"max","objective":[11,13,17,19,23,29,31],"constraints":[expression]}
        parsed = parse_proposal(json.dumps(candidate), n)
        assert parsed["valid"], parsed
        assert parsed["authored_model"] == candidate
        assert len(parsed["model"]["constraints"]) == 1
        assert all(model_feasible(parsed["model"], x) == bool(expected(x))
                   for x in itertools.product((0,1), repeat=n))
        checks["primitive_" + name] = {"passed":True,"assignments":2**n}
    candidate = {"formulation":"binary_ilp","variables":[0,1],"sense":"max",
                 "objective":[3,2],"constraints":["x0+x1<=1"]}
    case = {"id":"software-fixture","intention":"synthetic public request only",
            "data":{"n":2,"weights":[3,2],"costs":[2,1],"edges":[[0,1]]}}
    row = {"id":case["id"],"phase":"initial","output_tokens":3,
           "generated_token_ids":[11,12,151645],
           "generated_token_log_probabilities":[-.5,-.25,-.125],
           "mean_generated_log_probability":(-.5-.25-.125)/3,
           "input_tokens":10,"finish_reason":"eos",
           "messages":[{"role":"system","content":"fixture"},
                       {"role":"user","content":json.dumps({"intention":case["intention"],"data":case["data"]})}],
           "raw_response":json.dumps(candidate),"parsed":parse_proposal(json.dumps(candidate),2)}
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary)/"fixture.jsonl"
        path.write_text(json.dumps(row)+"\n")
        assert study.indexed(path,{case["id"]:case},"initial")
        for name, key, value in [
            ("nan_mean_rejected","mean_generated_log_probability",float("nan")),
            ("infinite_mean_rejected","mean_generated_log_probability",float("inf")),
            ("input_reserve_rejected","input_tokens",3584),
            ("boolean_input_rejected","input_tokens",True),
        ]:
            altered = copy.deepcopy(row); altered[key] = value
            path.write_text(json.dumps(altered)+"\n")
            try:
                study.indexed(path,{case["id"]:case},"initial")
            except ValueError:
                checks[name] = {"passed":True}
            else:
                raise AssertionError(name)
    first = copy.deepcopy(row); second = copy.deepcopy(row)
    assert study.choose_direct(first,second)[1] == 0
    second["mean_generated_log_probability"] = -.01
    assert study.choose_direct(first,second)[1] == 1
    second["parsed"] = {"valid":False,"error":"fixture"}
    assert study.choose_direct(first,second)[1] == 0
    assert study.choose_revision(first,second)[1] == 0
    second["parsed"] = first["parsed"]
    assert study.choose_revision(first,second)[1] == 1
    checks["arm_selection_without_reference"] = {"passed":True}
    request = driver.completion_request([1,2,3], 1234)
    assert request["n_predict"] == 512 and request["grammar"] == driver.FORM_GRAMMAR
    response = {"content":json.dumps(candidate),"tokens":[11,12,151645],
                "completion_probabilities":[{"id":11,"prob":.5},{"id":12,"prob":.25},{"id":151645,"prob":1.0}],
                "tokens_predicted":3,"tokens_evaluated":3,"truncated":False,"stop_type":"eos",
                "generation_settings":{**{key:request[key] for key in
                    ("post_sampling_probs","samplers","seed","top_k","temperature","top_p","min_p","n_predict")},
                    "speculative.types":"none","backend_sampling":False}}
    response["generation_settings"]["top_p"] = 0.800000011920929
    ids, logs, reason = driver.decode_completion(response,3,1234,512)
    assert ids == [11,12,151645] and logs == [math.log(.5),math.log(.25),0] and reason == "eos"
    checks["chosen_probabilities_string_speculation_float32_and_eos"] = {"passed":True}
    bad = copy.deepcopy(response); bad["completion_probabilities"][0]["id"] = 999
    try:
        driver.decode_completion(bad,3,1234,512)
    except ValueError:
        checks["chosen_probability_id_mismatch_rejected"] = {"passed":True}
    else:
        raise AssertionError("chosen probability mismatch")
    try:
        validate_feedback({"kind":"schema","message":SCHEMA_MESSAGE,"correct_model":candidate},2)
    except ValueError:
        checks["feedback_cannot_add_reference_model"] = {"passed":True}
    else:
        raise AssertionError("feedback model injection")
    sources = ("quantage/repair_llama_linear.py","quantage/repair_language.py",
               "quantage/repair_feedback.py","quantage/repair_study_c19.py",
               "scripts/audit_c19_preflight.py")
    report = {"status":"passed_bounded_software_checks","python":platform.python_version(),
              "source_sha256":{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sources},
              "checks":checks,"elapsed_seconds":time.perf_counter()-started,
              "model_executions":0,"network_requests":0,"test_C19_records_read":0,
              "grammar_validation_scope":"manual derivations plus exact parser truth tables; no native GBNF validator invoked",
              "review_independence":"driver/scorer reviewer distinct; reviewer originally authored repair_language.py and repair_solvers.py",
              "limitations":["historical schema feedback wording mentions integer rows",
                             "API scores are heuristics, not grammar-conditioned likelihood",
                             "runtime/native template, Metal and model quality not exercised"]}
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":report["status"],"checks":len(checks),
                      "model_executions":0,"test_C19_records_read":0}))


if __name__=="__main__": main()
