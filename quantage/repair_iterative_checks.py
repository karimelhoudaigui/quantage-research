"""Author software checks only: synthetic data, no corpus/gold/model/network."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import tempfile
import time

from . import repair_iterative_full_inference as full
from . import repair_iterative_patch_inference as patch_driver
from . import repair_study_c23_v2 as study
from .repair_iterative_state import initial_context, round_two_context, public_state_payload, apply_current_patch
from .repair_language import parse_proposal
from .repair_patch_tool_language import parse_patch
from .repair_trace_feedback import build_feedback
from .repair_model import verify_model


def run_checks():
    started=time.perf_counter();checks={}
    case={"id":"iterative-software-fixture","language":"en","intention":"SYNTHETIC implication/exclusion check only.",
          "data":{"n":3,"weights":[5,4,3],"costs":[2,1,2],"edges":[[0,1]]}}
    spec={"budget":None,"min_count":None,"max_count":None,"required":[],"forbidden":[],"implications":[[2,1]]}
    bad={"formulation":"binary_ilp","variables":[0,1,2],"sense":"max","objective":[5,4,3],
         "constraints":["x0+x1<=1","x2-x0<=0","x1+x2<=1"]}
    first_raw=json.dumps(bad)
    patch1=json.dumps({"diagnosis":"Correct one implication.",
                      "edits":[{"op":"replace_constraint","index":1,"row":"x2-x1<=0"}]})
    patch2=json.dumps({"diagnosis":"Remove the remaining invented exclusion.",
                      "edits":[{"op":"delete_constraint","index":2}]})
    noop=json.dumps({"diagnosis":"No change.","edits":[]})
    c1=initial_context(first_raw,3);c2=round_two_context(first_raw,patch1,3)
    assert not verify_model(case["data"],spec,c2["parsed"])["faithful"]
    final=parse_patch(patch2,3,c2["base_raw"])
    assert final["valid"] and verify_model(case["data"],spec,final)["faithful"]
    checks["second_literal_repair_removes_residual_error"]=True
    assert c2["base_kind"]=="materialized_state" and not c2["materialization_is_model_generation"]
    assert c2["previous_patch_sha256"]==hashlib.sha256(patch1.encode()).hexdigest()
    fallback=round_two_context(first_raw,"INVALID PATCH",3)
    assert fallback["state"]==bad and fallback["selected_state_source"]=="initial_syntax_fallback"
    absent=round_two_context("INVALID INITIAL","INVALID PATCH",3)
    assert absent["state"] is None and absent["base_raw"]=="INVALID INITIAL" and absent["base_kind"]=="unusable_initial_raw"
    replacement={"formulation":"binary_ilp","variables":[0,1,2],"sense":"max","objective":[5,4,3],
                 "constraints":["x0+x1<=1","x2-x1<=0"]}
    explicit=parse_patch(json.dumps({"diagnosis":"Replace unusable base.",
                       "edits":[{"op":"replace_model","model":replacement}]}),3,absent["base_raw"])
    assert explicit["valid"]
    incomplete={**bad,"objective":[]}
    missing=round_two_context(json.dumps(incomplete),"INVALID PATCH",3)
    local=json.dumps({"diagnosis":"Repair a field.","edits":[{"op":"set_objective","values":[5,4,3]}]})
    assert parse_patch(local,3,missing["base_raw"])["valid"]
    assert not apply_current_patch(local,3,missing)["valid"]
    replacement_patch=json.dumps({"diagnosis":"Explicit replacement.",
                                 "edits":[{"op":"replace_model","model":replacement}]})
    assert apply_current_patch(replacement_patch,3,missing)["valid"]
    checks["syntax_fallback_and_explicit_replacement_only"]=True
    assert full.CONTEXT==patch_driver.CONTEXT==6144 and full.MAX_NEW_TOKENS==patch_driver.MAX_NEW_TOKENS==1024
    assert full.completion_request([1]*5119,123)["n_predict"]==1024
    try:full.completion_request([1]*5120,123)
    except ValueError:pass
    else:raise AssertionError("context reserve")
    for driver in (full,patch_driver):
        try:driver.completion_request([1]*5120,123,max_new_tokens=1)
        except ValueError:pass
        else:raise AssertionError("lower output request bypassed fixed input cap")
    assert full.seed_for(case["id"],"direct",2)==patch_driver.seed_for(case["id"],"guided",2)
    command=full.server_command("/fixture/server","/fixture/model",1234)
    assert command[command.index("--batch-size")+1]==command[command.index("--ubatch-size")+1]=="128"
    checks["6144_1024_round_seeds_and_batch128"]=True

    class CleanupProcess:
        """State fixture only; no process starts and no timing claim is made."""
        def __init__(self, unreapable):
            self.unreapable=unreapable;self.returncode=None;self.waits=[];self.killed=False
        def poll(self):return self.returncode
        def terminate(self):pass
        def kill(self):self.killed=True
        def wait(self,timeout):
            self.waits.append(timeout)
            if timeout==2 or self.unreapable:raise subprocess.TimeoutExpired("fixture",timeout)
            self.returncode=-9;return self.returncode
    for driver in (full,patch_driver):
        command=driver.server_command("/fixture/server","/fixture/model",1234)
        assert driver.GPU_LAYERS==30 and command[command.index("--n-gpu-layers")+1]=="30"
        for unreapable in (False,True):
            server=driver.ServerProcess.__new__(driver.ServerProcess)
            server.process=CleanupProcess(unreapable);server.watchdog=None;server.handles=[];server.stats={}
            server.output=Path("/fixture/absent-output");server.child_cpu_before=resource.getrusage(resource.RUSAGE_CHILDREN)
            try:server.stop()
            except subprocess.TimeoutExpired:
                assert unreapable
            else:assert not unreapable
            assert server.process.killed and server.process.waits==[2,10.0]
            assert server.stats["server_reaped"] is not unreapable
            assert server.stats["backend_observed"]["device"]=="unverified"
    checks["partial30_and_bounded_10s_reap_state_fixture"]=True

    def full_row(phase,round_index):
        logs=[-.25,-.125]
        return {"id":case["id"],"phase":phase,"round":round_index,
                "seed":full.seed_for(case["id"],phase,round_index),"messages":full.messages_for(case,"FULL FIXTURE",phase),
                "raw_response":first_raw,"parsed":parse_proposal(first_raw,3),
                "input_tokens":10,"input_token_ids":list(range(10)),"output_tokens":2,
                "generated_token_ids":[101,151645],"generated_token_log_probabilities":logs,
                "mean_generated_log_probability":sum(logs)/2,"finish_reason":"eos",
                "wall_seconds":.01,"cpu_seconds":.001}
    first=full_row("initial",0)

    def patch_row(phase,round_index,raw,previous=None,feedback=None):
        context=(initial_context(first_raw,3) if round_index==1 else round_two_context(first_raw,previous["raw_response"],3))
        row=full_row("direct",round_index)
        row.update(phase=phase,round=round_index,raw_response=raw,
                   messages=patch_driver.messages_for(case,"PATCH FIXTURE",phase,first,feedback,round_index,context,previous),
                   parsed=apply_current_patch(raw,3,context),
                   initial_response_sha256=context["initial_raw_sha256"],base_kind=context["base_kind"],
                   state_provenance=public_state_payload(context)["state_provenance"],
                   previous_patch_sha256=context["previous_patch_sha256"],materialized_base_model=context["state"])
        return row

    def write_rows(path,values):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text("".join(json.dumps(row,allow_nan=False)+"\n" for row in values))

    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary);cases=root/"cases.json";gold=root/"gold.json"
        cases.write_text(json.dumps([case]));gold.write_text(json.dumps([{"id":case["id"],"constraints":spec,"families":"I"}]))
        paths={name:root/name/"raw.jsonl" for name in ("initial",)+study.CHANNELS}
        write_rows(paths["initial"],[first])
        study.feedback(cases,gold,paths["initial"],root/"feedback0")
        feedback0=json.loads((root/"feedback0/minimal.json").read_text())[case["id"]]
        s1=patch_row("self",1,noop);g1=patch_row("guided",1,patch1,feedback=feedback0)
        for name,row in (("direct1",full_row("direct",1)),("direct2",full_row("direct",2)),("self1",s1),("guided1",g1)):
            write_rows(paths[name],[row])
        study.feedback(cases,gold,paths["initial"],root/"feedback1",1,paths["guided1"],"guided")
        feedback1=json.loads((root/"feedback1/minimal.json").read_text())[case["id"]]
        s2=patch_row("self",2,noop,previous=s1)
        g2=patch_row("guided",2,patch2,previous=g1,feedback=feedback1)
        assert g2["messages"][2]=={"role":"assistant","content":g1["raw_response"]}
        follow=json.loads(g2["messages"][3]["content"])
        assert follow["current_model_state"]==c2["state"] and follow["current_model_state"]!=replacement
        assert "verifier_feedback" not in json.loads(s2["messages"][3]["content"])
        checks["actual_previous_patch_assistant_and_own_materialized_state"]=True
        write_rows(paths["self2"],[s2]);write_rows(paths["guided2"],[g2])
        metrics=study.score(cases,gold,paths["initial"],root/"scores",
                            {name:paths[name] for name in study.CHANNELS},
                            [root/"feedback0/reports.jsonl",root/"feedback1/reports.jsonl"])
        assert metrics["physical_generation_calls"]==7 and metrics["attributable_generation_calls"]==9
        assert metrics["round1"]["guided"]["faithful"]==0 and metrics["final"]["guided"]["faithful"]==1
        assert metrics["final"]["self"]["faithful"]==0 and metrics["H23"]["required_gain"]==3
        recorded=json.loads((root/"scores/raw.jsonl").read_text())
        assert recorded["patch_attempts"]["guided2"]["raw_patch"]==patch2
        assert recorded["results"]["direct"]["final"]["selected_candidate_index"]==0
        checks["round1_final_metrics_best3_tie_and_7_physical_9_attributable"]=True
        tampered=copy.deepcopy(g2);tampered["materialized_base_model"]=replacement
        write_rows(root/"tampered.jsonl",[tampered])
        try:study.indexed(root/"tampered.jsonl",{case["id"]:case},"guided2",
                          initial={case["id"]:first},previous={case["id"]:g1})
        except ValueError:pass
        else:raise AssertionError("materialized state tampering")
        checks["tampered_state_rejected"]=True
        try:study.indexed(paths["guided2"],{case["id"]:case},"guided2",initial={case["id"]:first})
        except ValueError:pass
        else:raise AssertionError("missing previous actual patch")
        checks["missing_lineage_rejected_without_imputation"]=True
    return {"status":"passed_author_software_checks","checks":checks,
            "model_executions":0,"network_requests":0,"C23_corpus_or_gold_reads":0,
            "fixtures":"synthetic only; classical DFS/HiGHS really execute; not LLM performance",
            "elapsed_seconds":time.perf_counter()-started}


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args();report=run_checks()
    names=("quantage/repair_iterative_state.py","quantage/repair_iterative_full_inference.py",
           "quantage/repair_iterative_patch_inference.py","quantage/repair_study_c23_v2.py",
           "quantage/repair_iterative_checks.py")
    report["source_sha256"]={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in names}
    report["review_provenance"]="implementation author; independent review pending"
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":report["status"],"checks":len(report["checks"]),"model_executions":0}))


if __name__=="__main__":main()
