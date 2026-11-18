"""Prospective C23 v2: three calls/arm, literal two-repair state lineage.

No model is executed here. Initial/direct channels contain full formulations;
self/guided channels contain actual patches. Every patch is replayed against
its correct raw base, never parsed as a full model or selected using the gold.
H23 +3/final regressions<=1 is a proposal to freeze before held-out scoring.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import time

from .repair_language import parse_proposal
from .repair_model import verify_model, no_duplicates
from .repair_patch_tool_language import parse_patch
from .repair_iterative_state import initial_context, round_two_context, public_state_payload, apply_current_patch
from .repair_iterative_patch_inference import (
    SELF_INSTRUCTION, GUIDED_INSTRUCTION, SELF_ROUND2_INSTRUCTION, GUIDED_ROUND2_INSTRUCTION)
from .repair_trace_feedback import build_feedback, validate_feedback
from .repair_feedback import optimization_diagnostics
from .repair_study_c19 import dataset

CHANNELS = ("direct1","direct2","self1","self2","guided1","guided2")
COST_FIELDS = ("input_tokens","output_tokens","wall_seconds","cpu_seconds")


def strict_json(text):
    def reject(_):
        raise ValueError("nonfinite input JSON")
    return json.loads(text, object_pairs_hook=no_duplicates, parse_constant=reject)


def rows(path):
    return [strict_json(line) for line in Path(path).read_text().splitlines()]


def dump(path, value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n")


def channel_parts(channel):
    if channel=="initial":
        return "initial",0
    if channel not in CHANNELS:
        raise ValueError("unknown iterative channel")
    return channel[:-1],int(channel[-1])


def trace_from_follow(follow,n):
    return validate_feedback({"verdict":follow["verifier_feedback"],
                              "candidate_evaluations":follow["candidate_evaluation_tool"],
                              "gloss":follow["gloss"]},n)


def indexed(path, public, channel, initial=None, previous=None, replay_times=None):
    phase,round_index=channel_parts(channel)
    patch_phase=phase in ("self","guided")
    if patch_phase and (initial is None or (round_index==2 and previous is None)):
        raise ValueError("literal patch replay requires actual initial/previous observations")
    observed=rows(path)
    result={row["id"]:row for row in observed}
    if len(result)!=len(observed) or set(result)!=set(public):
        raise ValueError("complete unique channel matrix required; no imputation")
    for identity,row in result.items():
        if row["phase"]!=phase or type(row.get("round")) is not int or row["round"]!=round_index:
            raise ValueError("wrong explicit phase/round")
        count=row["output_tokens"];ids=row["generated_token_ids"];logs=row["generated_token_log_probabilities"]
        if (type(count) is not int or not 0<count<=1024 or type(ids) is not list or type(logs) is not list
                or len(ids)!=count or len(logs)!=count or any(type(t) is not int or t<0 for t in ids)):
            raise ValueError("generated token accounting mismatch")
        mean=row["mean_generated_log_probability"]
        if (any(type(v) not in (int,float) or not math.isfinite(v) or v>0 for v in logs)
                or type(mean) not in (int,float) or not math.isfinite(mean)
                or abs(sum(logs)/count-mean)>1e-12):
            raise ValueError("processed token score mismatch")
        inputs=row["input_tokens"];prompt_ids=row["input_token_ids"]
        if (type(inputs) is not int or not 0<inputs<=5119 or type(prompt_ids) is not list
                or len(prompt_ids)!=inputs or any(type(t) is not int or t<0 for t in prompt_ids)):
            raise ValueError("6144 context reserve/input accounting mismatch")
        if row["finish_reason"] not in ("eos","token_limit") or (row["finish_reason"]=="token_limit" and count!=1024):
            raise ValueError("unexplained stop")
        seed=(int(hashlib.sha256(identity.encode()).hexdigest()[:8],16)+round_index)%2**32
        if type(row["seed"]) is not int or row["seed"]!=seed or seed==2**32-1:
            raise ValueError("wrong explicit round seed")
        for field in ("wall_seconds","cpu_seconds"):
            if type(row[field]) not in (int,float) or not math.isfinite(row[field]) or row[field]<0:
                raise ValueError("invalid client cost")
        messages=row["messages"];expected_count=4 if patch_phase else 2
        if (type(messages) is not list or len(messages)!=expected_count
                or any(type(m) is not dict or set(m)!={"role","content"} or type(m["content"]) is not str for m in messages)
                or messages[0]["role"]!="system" or messages[1]["role"]!="user"):
            raise ValueError("unexpected message roles/fields")
        case=public[identity];n=case["data"]["n"]
        if strict_json(messages[1]["content"])!={"intention":case["intention"],"data":case["data"]}:
            raise ValueError("public request differs")
        started=time.perf_counter()
        if patch_phase:
            first=initial[identity]
            context=(initial_context(first["raw_response"],n) if round_index==1 else
                     round_two_context(first["raw_response"],previous[identity]["raw_response"],n))
            assistant=first["raw_response"] if round_index==1 else previous[identity]["raw_response"]
            if messages[2]!={"role":"assistant","content":assistant} or messages[3]["role"]!="user":
                raise ValueError("assistant must be the actual initial/previous raw patch")
            if row.get("initial_response_sha256")!=context["initial_raw_sha256"]:
                raise ValueError("initial lineage mismatch")
            if (row.get("base_kind")!=context["base_kind"] or row.get("materialized_base_model")!=context["state"]
                    or row.get("previous_patch_sha256")!=context["previous_patch_sha256"]
                    or row.get("state_provenance")!=public_state_payload(context)["state_provenance"]):
                raise ValueError("literal materialized state lineage mismatch")
            if round_index==1 and phase=="self":
                if messages[3]["content"]!=SELF_INSTRUCTION:
                    raise ValueError("round1 self patch received extra feedback")
            else:
                follow=strict_json(messages[3]["content"])
                tool_fields={"verifier_feedback","candidate_evaluation_tool","gloss"}
                state_fields={"current_model_state","state_provenance"} if round_index==2 else set()
                fields={"instruction"}|state_fields|(tool_fields if phase=="guided" else set())
                instruction=(GUIDED_INSTRUCTION if round_index==1 else
                             SELF_ROUND2_INSTRUCTION if phase=="self" else GUIDED_ROUND2_INSTRUCTION)
                if type(follow) is not dict or set(follow)!=fields or follow["instruction"]!=instruction:
                    raise ValueError("closed phase-specific patch instruction required")
                if round_index==2 and any(follow[key]!=value for key,value in public_state_payload(context).items()):
                    raise ValueError("prompt materialized state does not equal literal replay")
                if phase=="guided":
                    trace_from_follow(follow,n)
            parsed=apply_current_patch(row["raw_response"],n,context)
        else:
            parsed=parse_proposal(row["raw_response"],n)
        if replay_times is not None:
            replay_times[identity]=time.perf_counter()-started
        if parsed!=row["parsed"]:
            raise ValueError("saved parser result differs from literal replay")
    return result


def best_direct(candidates):
    index=max(range(len(candidates)),key=lambda i:(int(candidates[i]["parsed"]["valid"]),
              candidates[i]["mean_generated_log_probability"],-i))
    return candidates[index],index


def latest_valid(candidates):
    valid=[i for i,row in enumerate(candidates) if row["parsed"]["valid"]]
    index=valid[-1] if valid else len(candidates)-1
    return candidates[index],index


def feedback(cases_path,gold_path,initial_path,output,round_index=0,previous_path=None,phase="guided"):
    if type(round_index) is not int or round_index not in (0,1) or phase not in ("self","guided"):
        raise ValueError("feedback round must be 0 (initial) or 1 (after first patch)")
    if (round_index==1)!=(previous_path is not None):
        raise ValueError("round1 feedback requires the actual first patch")
    cases,public,gold=dataset(Path(cases_path),Path(gold_path))
    initial=indexed(initial_path,public,"initial")
    previous=indexed(previous_path,public,phase+"1",initial=initial) if previous_path is not None else {}
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    if (output/"minimal.json").exists():
        raise ValueError("feedback output already exists")
    minimal={};reports=[]
    for case in cases:
        identity=case["id"];n=case["data"]["n"];started=time.perf_counter()
        context=(initial_context(initial[identity]["raw_response"],n) if round_index==0 else
                 round_two_context(initial[identity]["raw_response"],previous[identity]["raw_response"],n))
        report=verify_model(case["data"],gold[identity]["constraints"],context["parsed"])
        message=build_feedback(report,context["parsed"],n)
        minimal[identity]=message
        reports.append({"id":identity,"after_round":round_index,"verification":report,
                        "state_provenance":public_state_payload(context)["state_provenance"],
                        "feedback_wall_seconds":time.perf_counter()-started})
    dump(output/"minimal.json",minimal)
    (output/"reports.jsonl").write_text("".join(json.dumps(r,ensure_ascii=False,allow_nan=False)+"\n" for r in reports))
    return reports


def count_template():
    return {"observed":0,"schema_valid":0,"faithful":0,"portfolio_concordant":0,
            "usable_for_original_problem":0,"repairs_from_initial":0,"regressions_from_initial":0}


def evaluate(case,spec,selected,index):
    from .repair_solvers import portfolio
    parsed=selected["parsed"]
    started=time.perf_counter();verification=verify_model(case["data"],spec,parsed)
    verification_seconds=time.perf_counter()-started
    solved=portfolio(parsed["model"]) if parsed["valid"] else None
    return {"selected_candidate_index":index,"selected_phase":selected["phase"],"selected_round":selected["round"],
            "model":parsed.get("model"),"materialized_authored_model":parsed.get("authored_model",parsed.get("model")),
            "verification":verification,"verification_wall_seconds":verification_seconds,
            "optimization_diagnostics":optimization_diagnostics(case["data"],spec,parsed),"portfolio":solved,
            "usable_for_original_problem":bool(verification["faithful"] and solved and solved["concordance"])}


def execution_metadata(path):
    path=Path(path);meta_path=path.parent/"generation.json";manifest_path=path.parent/"manifest.json"
    if not manifest_path.exists() and path.parent.name=="driver":
        manifest_path=path.parent.parent/"manifest.json"
    meta=strict_json(meta_path.read_text()) if meta_path.exists() else {}
    manifest=strict_json(manifest_path.read_text()) if manifest_path.exists() else {}
    return {"load_seconds":meta.get("load_seconds"),"process_wall_seconds":meta.get("wall_seconds"),
            "wrapper_wall_seconds":manifest.get("run",{}).get("runtime_seconds"),
            "client_cpu_seconds":meta.get("client_cpu_seconds"),"server_cpu_seconds":meta.get("server_cpu_seconds"),
            "server_cpu_scope":meta.get("server_cpu_scope"),"aggregate_of":meta.get("aggregate_of")}


def score(cases_path,gold_path,initial_path,output,channel_paths=None,feedback_reports=None):
    cases,public,gold=dataset(Path(cases_path),Path(gold_path))
    initial=indexed(initial_path,public,"initial")
    channel_paths=channel_paths or {}
    if channel_paths and (set(channel_paths)!=set(CHANNELS) or any(v is None for v in channel_paths.values())):
        raise ValueError("all six second/third channels are required; no imputation")
    phases={};timings={}
    for name in CHANNELS:
        if not channel_paths:break
        previous=phases.get(name[:-1]+"1") if name.endswith("2") and name.startswith(("self","guided")) else None
        phases[name]=indexed(channel_paths[name],public,name,initial=initial,previous=previous,replay_times=timings.setdefault(name,{}))
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    if (output/"raw.jsonl").exists():raise ValueError("scores already recorded")
    totals={stage:{arm:count_template() for arm in ("direct","self","guided")} for stage in ("round1","final")}
    second_regressions={arm:0 for arm in ("direct","self","guided")}
    records=[]
    for case in cases:
        identity=case["id"];spec=gold[identity]["constraints"];first=initial[identity];n=case["data"]["n"]
        base=evaluate(case,spec,first,0);results={"initial":base}
        attempts={}
        if phases:
            if any(phases[name][identity]["messages"]!=first["messages"] for name in ("direct1","direct2")):
                raise ValueError("independent direct draws must use the exact initial prompt")
            if len({phases[name][identity]["messages"][0]["content"] for name in ("self1","self2","guided1","guided2")})!=1:
                raise ValueError("all patch phases must share the frozen patch system instruction")
            for round_index in (1,2):
                guided=phases["guided"+str(round_index)][identity]
                context=(initial_context(first["raw_response"],n) if round_index==1 else
                         round_two_context(first["raw_response"],phases["guided1"][identity]["raw_response"],n))
                expected=build_feedback(verify_model(case["data"],spec,context["parsed"]),context["parsed"],n)
                if trace_from_follow(strict_json(guided["messages"][3]["content"]),n)!=expected:
                    raise ValueError("guided feedback is not the exact current-state verdict and OWN-row trace")
            for arm in ("direct","self","guided"):
                candidates=[first,phases[arm+"1"][identity],phases[arm+"2"][identity]]
                choose=best_direct if arm=="direct" else latest_valid
                stage_results={}
                for stage,subset in (("round1",candidates[:2]),("final",candidates)):
                    selected,index=choose(subset);value=evaluate(case,spec,selected,index)
                    stage_results[stage]=value
                    counter=totals[stage][arm];faithful=value["verification"]["faithful"]
                    counter["observed"]+=1;counter["schema_valid"]+=int(selected["parsed"]["valid"])
                    counter["faithful"]+=int(faithful);counter["portfolio_concordant"]+=int(value["portfolio"] is not None and value["portfolio"]["concordance"])
                    counter["usable_for_original_problem"]+=int(value["usable_for_original_problem"])
                    counter["repairs_from_initial"]+=int(not base["verification"]["faithful"] and faithful)
                    counter["regressions_from_initial"]+=int(base["verification"]["faithful"] and not faithful)
                second_regressions[arm]+=int(stage_results["round1"]["verification"]["faithful"] and not stage_results["final"]["verification"]["faithful"])
                results[arm]=stage_results
            for name in ("self1","self2","guided1","guided2"):
                row=phases[name][identity];parsed=row["parsed"]
                attempts[name]={"raw_patch":row["raw_response"],"authored_patch":parsed.get("authored_patch"),
                    "diagnosis":parsed.get("diagnosis"),"diagnosis_scope":"unverified text; never a semantic edit",
                    "valid":parsed["valid"],"materialized_authored_model":parsed.get("authored_model"),
                    "materialized_dense_model":parsed.get("model"),"state_provenance":row["state_provenance"],
                    "base_kind":row["base_kind"],"replay_wall_seconds":timings[name][identity]}
        records.append({"id":identity,"language":case["language"],"families":gold[identity]["families"],
                        "results":results,"patch_attempts":attempts})
    (output/"raw.jsonl").write_text("".join(json.dumps(r,ensure_ascii=False,allow_nan=False)+"\n" for r in records))
    physical=list(initial.values())+[row for mapping in phases.values() for row in mapping.values()]
    attributable={arm:{field:sum(initial[i][field]+phases[arm+"1"][i][field]+phases[arm+"2"][i][field] for i in public)
                       for field in COST_FIELDS} for arm in ("direct","self","guided")} if phases else {}
    h={"status":"development_only"}
    if phases:
        gain=totals["final"]["guided"]["faithful"]-totals["final"]["self"]["faithful"]
        regressions=totals["final"]["guided"]["regressions_from_initial"]
        h={"status":"supported_in_finite_test" if gain>=3 and regressions<=1 else "not_supported_in_finite_test",
           "guided_minus_self_final_faithful":gain,"required_gain":3,"guided_final_regressions":regressions,"maximum_final_regressions":1}
    paths={"initial":initial_path,**channel_paths}
    portfolio_seconds=0.;verification_seconds=0.
    for record in records:
        values=[record["results"]["initial"]]+[v for arm in ("direct","self","guided") if arm in record["results"] for v in record["results"][arm].values()]
        portfolio_seconds+=sum(v["portfolio"]["total_portfolio_seconds"] for v in values if v["portfolio"] is not None)
        verification_seconds+=sum(v["verification_wall_seconds"] for v in values)
    feedback_cost=sum(row["feedback_wall_seconds"] for path in (feedback_reports or []) for row in rows(path)) if feedback_reports else None
    metrics={"cases":len(cases),"round1":totals["round1"],"final":totals["final"],"round2_regressions_from_round1":second_regressions,
             "H23":h,"primary_comparison":"guided_tool_patch_final versus self_patch_final",
             "physical_generation_calls":len(physical),"attributable_generation_calls":9*len(cases) if phases else len(initial),
             "physical_generation_cost":{f:sum(row[f] for row in physical) for f in COST_FIELDS},
             "attributable_cost_per_arm":attributable,"generation_executions":{name:execution_metadata(path) for name,path in paths.items()},
             "feedback_computation_seconds":feedback_cost,"verification_wall_seconds":verification_seconds,
             "posthoc_replay_wall_seconds":{name:sum(values.values()) for name,values in timings.items()},
             "scored_portfolio_seconds_total":portfolio_seconds,
             "planned_call_accounting":{"physical":7*len(cases),"attributable":9*len(cases)} if phases else None,
             "budget":"three calls/arm/case, max3072 output tokens, context6144 with input<=5119; shared initial counted once physically",
             "selection":{"direct":"best of initial/direct1/direct2 by validity then API score, earliest tie",
                          "self_guided":"latest syntactically valid state, never semantic selection"},
             "cost_scope":"row costs are client/completion; server/load/wrapper separate; own-state materialization and feedback/replay/verification/portfolio recorded; GPU energy and full session unknown",
             "scope":"finite annotated oracle, literal state lineage, no population or novelty guarantee; direct full generation secondary; portfolio ex-post"}
    dump(output/"metrics.json",metrics)
    return metrics


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode",choices=("feedback","score"))
    for flag in ("cases","gold","initial","output"):parser.add_argument("--"+flag,type=Path,required=True)
    for channel in CHANNELS:parser.add_argument("--"+channel,type=Path)
    parser.add_argument("--round",dest="round_index",type=int,choices=(0,1),default=0)
    parser.add_argument("--previous",type=Path);parser.add_argument("--phase",choices=("self","guided"),default="guided")
    parser.add_argument("--feedback-reports",type=Path,nargs="*")
    args=parser.parse_args()
    if args.mode=="feedback":
        result=feedback(args.cases,args.gold,args.initial,args.output,args.round_index,args.previous,args.phase)
        print(json.dumps({"feedback_cases":len(result),"after_round":args.round_index}))
    else:
        paths={channel:getattr(args,channel) for channel in CHANNELS}
        paths={} if all(value is None for value in paths.values()) else paths
        result=score(args.cases,args.gold,args.initial,args.output,paths,args.feedback_reports)
        print(json.dumps({"cases":result["cases"],"physical_generation_calls":result["physical_generation_calls"],"H23":result["H23"]}))


if __name__=="__main__":main()
