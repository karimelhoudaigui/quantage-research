"""LLM compact semantic proposal -> deterministic formulation and local solver."""
import json
import re
from .core import MIS_INTENT,PHOTO_INTENT,understand,formulate,choose_solver,solve_qubo,optical_probabilities
from .contracts import verify_external

TASKS={'mis':'maximum_weight_independent_set','photon':'ideal_single_photon_probabilities'}


def parse_compact(raw):
    text=raw.strip()
    match=re.fullmatch(r'```(?:json)?\s*\n([\s\S]*?)\n```',text)
    if match:text=match.group(1)
    try:
        proposal=json.loads(text,parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
        if type(proposal) is not dict or set(proposal)!={'action','family','task','reason'}:
            raise ValueError('exact compact fields required')
        if proposal['action'] not in ('propose','abstain') or proposal['family'] not in TASKS or type(proposal['reason']) is not str:
            raise ValueError('unknown action, family or reason type')
        if proposal['action']=='abstain' and proposal['task'] is not None:
            raise ValueError('abstention requires task=null')
        if proposal['action']=='propose' and proposal['task']!=TASKS[proposal['family']]:
            raise ValueError('unsupported compact task')
        return {'valid':True,'proposal':proposal,'single_code_fence_removed':bool(match)}
    except (TypeError,ValueError,KeyError) as exc:
        return {'valid':False,'reason':str(exc)}


def execute_compact(request,parsed):
    if not parsed['valid']:return {'status':'abstain','stage':'format','reason':parsed['reason']}
    proposal=parsed['proposal']
    if proposal['action']=='abstain':return {'status':'abstain','stage':'model_abstention','reason':proposal['reason']}
    try:
        intent=MIS_INTENT if proposal['family']=='mis' else PHOTO_INTENT
        problem=understand({'intent':intent,'data':request['data']})
        model=formulate(problem);report=verify_external(problem,model)
        if not report['valid']:return {'status':'abstain','stage':'numeric','verification':report}
        solution=solve_qubo(model) if problem['family']=='mis' else {'probabilities':optical_probabilities(model)}
        return {'status':'accepted','stage':'hybrid_pipeline','problem':problem,'formulation':model,
                'verification':report,'route':choose_solver(problem),'solution':solution,
                'original_intent':request['intent'],'semantic_certificate':False,
                'provenance':'LLM compact contract, deterministic formulation and solver'}
    except (TypeError,ValueError,KeyError,OverflowError) as exc:
        return {'status':'abstain','stage':'data_contract','reason':str(exc)}
