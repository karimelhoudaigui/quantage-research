"""Bounded C22 conserved-evidence audit; never import production patch/scorer.

One known completion is replayed, one attempted outcome stays unknown.
No model/runtime/solver execution, missing file synthesis or cache mutation.
"""
import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import platform
import signal
import time

SPEC=importlib.util.spec_from_file_location('separate_finite_audit','research/c16-observed-audit.py')
A=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)
B=Path('runs/20261115-c22-model-capacity')
C=Path('runs/20261115-c19-instruct-repair')
PINS={}


def read(path,lines=False,plain=False):
    path=Path(path);raw=path.read_bytes();PINS[str(path)]=hashlib.sha256(raw).hexdigest();s=raw.decode()
    return s if plain else ([json.loads(x) for x in s.splitlines() if x.strip()] if lines else json.loads(s))


def audit(output):
    started=time.perf_counter()
    cases={c['id']:c for c in read(B/'probe_cases.json')}
    remaining=read(B/'remaining_cases.json')
    A.check(set(cases)=={'29507bb778cc','417127d82203'} and [c['id'] for c in remaining]==['417127d82203'],'case disposition')
    initial={r['id']:r for r in read(C/'test-initial-v2/driver/raw.jsonl',True)}
    labels={r['id']:r['constraints'] for r in read(C/'private_gold.review.json')['cases']}
    oracle={r['id']:r for r in read('research/c19-annotation-oracle/raw.json')['cases']}
    feedback=read(B/'feedback.json');system=read(B/'instructions.txt',plain=True)
    v1meta=read(B/'probe-guided-v1/driver/generation.json');v1manifest=read(B/'probe-guided-v1/manifest.json')
    A.check(v1meta['status']=='partial_error' and v1meta['completed']==0 and 'before model startup' in v1meta['error'],'startup only failure')
    A.check(v1manifest['run']['status']=='failed' and v1manifest['run']['exit_status']==1,'startup runner failed')
    A.check(not list((B/'probe-guided-v1/driver').glob('http/*.request.json')),'startup no completion request')
    reconcile=read(B/'execution-reconciliation-v2.json');process=read(B/'process-reconciliation-v2.json')
    A.check(reconcile['attempted_unknown_ids']==['29507bb778cc'] and reconcile['never_attempted_ids']==['417127d82203'],'unknown vs never attempted')
    A.check(process['owned_repo_llama_processes']==[],'captured process check')
    A.check(read(B/'probe-guided-v2/driver/raw.jsonl',plain=True)=='','unknown raw empty')
    for path in [B/'probe-guided-v2/driver/generation.json',B/'probe-guided-v2/manifest.json',B/'probe-guided-v2/driver/http/000.response.json']:
        A.check(not path.exists(),'unknown artifact absent '+str(path))
    unknown_request=read(B/'probe-guided-v2/driver/http/000.request.json')
    unknown_template=read(B/'probe-guided-v2/driver/http/000.template.response.json')
    unknown_template_request=read(B/'probe-guided-v2/driver/http/000.template.request.json')
    A.check(json.loads(unknown_template_request['messages'][1]['content'])=={'intention':cases['29507bb778cc']['intention'],'data':cases['29507bb778cc']['data']},'unknown request matches public case')
    A.check(unknown_request['seed']==(int(hashlib.sha256(b'29507bb778cc').hexdigest()[:8],16)+1)%2**32,'unknown seed identity')
    suffix='<|im_start|>assistant\n<think>\n\n</think>\n\n'
    A.check(unknown_template['prompt'].endswith(suffix),'unknown closed nonthinking prompt')
    for path,h in reconcile['sha256_observed_after_interruption'].items():
        p=Path(path);got=hashlib.sha256(p.read_bytes()).hexdigest();PINS[path]=got;A.check(got==h,'interrupted evidence unchanged')
    rows=read(B/'probe-remaining-v3/driver/raw.jsonl',True)
    A.check(len(rows)==1 and rows[0]['id']=='417127d82203' and rows[0]['phase']=='guided','only never attempted remaining response')
    row=rows[0];i=row['id'];data=cases[i]['data'];n=data['n']
    patch=json.loads(row['raw_response'],object_pairs_hook=A.unique)
    A.check(set(patch)=={'diagnosis','edits'} and len(patch['diagnosis'])<=768 and all(32<=ord(c)<=126 for c in patch['diagnosis']),'patch shape')
    A.check(len(patch['edits'])==1,'one literal edit')
    base=json.loads(initial[i]['raw_response']);material=copy.deepcopy(base)
    edit=patch['edits'][0]
    A.check(set(edit)=={'op','index','row'} and edit['op']=='replace_constraint' and type(edit['index']) is int and 0<=edit['index']<len(material['constraints']),'observed edit')
    before_row=material['constraints'][edit['index']];material['constraints'][edit['index']]=edit['row']
    bm=A.parse(initial[i]['raw_response'],n);model=A.parse(json.dumps(material),n)
    A.check(model is not None and row['parsed']['valid'] and row['parsed']['authored_patch']==patch and row['parsed']['authored_model']==material and row['parsed']['model']==model,'independent literal materialization')
    before=A.assess(data,labels[i],bm);after=A.assess(data,labels[i],model)
    domain=[x for x in itertools.product((0,1),repeat=n) if A.reference(data,labels[i],x)]
    rb,ro=A.optimum(domain,data['weights'])
    A.check(sorted(A.mask(x) for x in domain)==oracle[i]['feasible_masks'] and rb==oracle[i]['max_weight'] and sorted(A.mask(x) for x in ro)==oracle[i]['optimal_masks'],'reviewer domain/optima')
    A.check(not after['faithful'] and after['feasibility_mismatches']==1 and after['objective_mismatches']==0,'residual one mismatch')
    witness=after['feedback']['witnesses'][0]['x'];evaluation=[]
    for j,(co,op,rhs) in enumerate(model['constraints']):
        lhs=sum(a*b for a,b in zip(co,witness));evaluation.append(dict(index=j,lhs=lhs,op=op,rhs=rhs,satisfied={'<=':lhs<=rhs,'>=':lhs>=rhs,'==':lhs==rhs}[op]))
    A.check([r['index'] for r in evaluation if not r['satisfied']]==[0],'remaining blocker line0')
    proposed_edges={tuple(j for j,v in enumerate(co) if v) for co,op,rhs in model['constraints'] if op=='<=' and rhs==1 and co.count(1)==2 and all(v in (0,1) for v in co)}
    extra_edges=sorted(proposed_edges-{tuple(sorted(e)) for e in data['edges']})
    A.check(extra_edges==[(0,1),(0,2),(0,3)],'three unsupported exclusions retained')
    messages=row['messages'];A.check(len(messages)==4 and messages[0]=={'role':'system','content':system} and messages[2]=={'role':'assistant','content':initial[i]['raw_response']},'history and current system')
    A.check(json.loads(messages[1]['content'])=={'intention':cases[i]['intention'],'data':data},'public request')
    follow=json.loads(messages[3]['content']);f=feedback[i]
    A.check(set(follow)=={'verifier_feedback','candidate_evaluation_tool','gloss','instruction'} and follow['verifier_feedback']==f['verdict']==before['feedback'] and follow['candidate_evaluation_tool']==f['candidate_evaluations'] and follow['gloss']==f['gloss'],'unchanged own-row feedback')
    for ev in f['candidate_evaluations']:
        x=ev['x'];rr=[]
        for j,(co,op,rhs) in enumerate(bm['constraints']):
            lhs=sum(a*b for a,b in zip(co,x));rr.append(dict(index=j,lhs=lhs,op=op,rhs=rhs,satisfied={'<=':lhs<=rhs,'>=':lhs>=rhs,'==':lhs==rhs}[op]))
        A.check(ev==dict(x=x,rows=rr,candidate_feasible=A.feasible(bm,x),candidate_objective=A.value(bm['objective'],x)),'tool is candidate only')
    folder=B/'probe-remaining-v3/driver';response=read(folder/row['http_response']);request=read(folder/'http/000.request.json');template=read(folder/'http/000.template.response.json');tr=read(folder/'http/000.template.request.json')
    A.check(tr=={'messages':messages} and template['prompt'].endswith(suffix) and response['prompt']==template['prompt'],'known hard-nonthinking prefix')
    A.check(hashlib.sha256(template['prompt'].encode()).hexdigest()==row['prompt_sha256'],'prompt hash')
    A.check(request['prompt']==row['input_token_ids'] and len(request['prompt'])==row['input_tokens']<=3071,'input reserve')
    A.check(response['content']==row['raw_response'] and response['tokens']==row['generated_token_ids'] and response['tokens_predicted']==row['output_tokens']==len(row['generated_token_ids'])<=1024 and response['tokens_evaluated']==row['input_tokens'],'HTTP content/counts')
    A.check(response['stop_type']==row['finish_reason']=='eos','known EOS')
    seed=(int(hashlib.sha256(i.encode()).hexdigest()[:8],16)+1)%2**32
    for k,v in {'seed':seed,'temperature':.7,'top_p':.8,'top_k':20,'n_predict':1024,'post_sampling_probs':True,'return_tokens':True,'samplers':['top_k','top_p','temperature']}.items():A.check(request[k]==v,'request '+k)
    A.check(len(response['completion_probabilities'])==len(row['generated_token_log_probabilities'])==row['output_tokens'],'chosen score lengths')
    for token,p,lp in zip(row['generated_token_ids'],response['completion_probabilities'],row['generated_token_log_probabilities']):A.check(token==p['id'] and 0<p['prob']<=1 and math.isclose(math.log(p['prob']),lp,abs_tol=1e-12),'chosen logprob')
    A.check(math.isclose(sum(row['generated_token_log_probabilities'])/row['output_tokens'],row['mean_generated_log_probability'],abs_tol=1e-12),'mean score')
    meta=read(folder/'generation.json');manifest=read(B/'probe-remaining-v3/manifest.json')
    A.check(meta['status']=='completed' and meta['error'] is None and meta['completed']==meta['planned']==1 and meta['server_exit_status']==0,'model process completed')
    A.check(manifest['run']['status']=='result-missing' and manifest['run']['exit_status']==0 and not manifest['run']['invalid_results'],'runner result-missing exit0')
    missing=[str(folder/'http/001.request.json'),str(folder/'http/001.response.json')]
    A.check(manifest['run']['missing_results']==missing and all(not Path(p).exists() for p in missing),'two wrongly declared001 outputs remain absent')
    for output_entry in manifest['outputs']:
        p=Path(output_entry['path']);got=hashlib.sha256(p.read_bytes()).hexdigest();PINS[str(p)]=got;A.check(got==output_entry['sha256'],'existing output hash')
    A.check(len(list((folder/'http').glob('[0-9][0-9][0-9].request.json')))==len(list((folder/'http').glob('[0-9][0-9][0-9].response.json')))==1,'single actual HTTP pair')
    cmd=meta['server_command']
    for flag,value in {'--batch-size':'128','--ubatch-size':'128','--ctx-size':'4096','--threads':'4','--device':'MTL0','--n-gpu-layers':'99'}.items():A.check(cmd[cmd.index(flag)+1]==value,'server config '+flag)
    A.check(json.loads(cmd[cmd.index('--chat-template-kwargs')+1])=={'enable_thinking':False} and meta['nonthinking_prompt_suffix_checked'],'requested hard switch')
    serverlog=read(folder/'server.stderr.txt',plain=True);gpu=meta['backend_observed']
    A.check(gpu['device']=='Metal' and gpu['offloaded_gpu_layers']==gpu['reported_total_layers']==37 and gpu['positive_metal_model_buffer'],'observed37layers')
    A.check(all(line in serverlog for line in gpu['evidence_lines']),'loader evidence lines retained')
    acq=read(B/'acquisition.json');A.check(acq['status']=='completed' and meta['model']['sha256']==acq['model']['sha256_expected'],'acquisition metadata pin')
    resources={name:read(B/name) for name in ['resource-management.json','resource-management-v2.json','resource-management-remaining.json']}
    eviction=read(B/'storage-additional-v2.json');validation=read('research/c19-c21-validation-before-cache-eviction.json')
    A.check(len(validation['manifests'])==17 and all(x['valid'] and not x['errors'] for x in validation['manifests']),'recorded pre-eviction17valid')
    A.check(all(e['restore_url'] and e['sha256_before'] and e['closed_by_lsof'] for e in eviction['evicted']),'cache restore provenance')
    A.check(all(not Path(p).exists() for e in eviction['evicted'] for p in e['paths']),'evicted cache aliases absent')
    for p,h in PINS.items():A.check(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,'audit inputs stable')
    result={'status':'completed_partial_evidence_audit','checked_on':'2026-11-16','python':platform.python_version(),'checks_passed':A.CHECKS,
            'independence':'Reviewer authored C19 corpus and C20 patch implementation. Separate literal replay and finite predicates; no production patch parser/scorer imported. Not blind or author-independent.',
            'inventory':{'planned_completion_cases':2,'attempted_case_ids':['29507bb778cc','417127d82203'],'known_response_records':1,'known_faithful':0,'unknown_ids':['29507bb778cc'],'full_pilot_faithful_bounds':[0,1],'unknown_imputed':False,'new_model_or_solver_executions':0},
            'known_case':{'id':i,'raw_patch':patch,'initial_row':before_row,'replacement_row':edit['row'],'materialized_authored_model':material,'before':before,'after':after,'reference_feasible_masks':sorted(A.mask(x) for x in domain),'reference_optimum':rb,'reference_optimal_masks':sorted(A.mask(x) for x in ro),'unsupported_exclusions':extra_edges,'residual_witness_row_evaluation':evaluation},
            'unknown_case':{'id':'29507bb778cc','request_input_ids_count':len(unknown_request['prompt']),'requested_output_cap':unknown_request['n_predict'],'request_seed':unknown_request['seed'],'output_tokens':None,'output_model':None,'consumed_input_tokens':None,'wall_seconds':None,'cpu_seconds':None,'cause':'unknown; no response, generation metadata or final runner manifest; captured process reconciliation empty'},
            'statuses':{'startup_v1':{'model':v1meta['status'],'runner':v1manifest['run']['status'],'completion_calls':0,'wall_seconds':v1meta['wall_seconds'],'cpu_seconds':v1meta['cpu_seconds']},'unknown_v2':{'runner_manifest':None,'model_generation_metadata':None,'raw_response_records':0},'known_remaining_v3':{'model':meta['status'],'server_exit_status':meta['server_exit_status'],'runner':manifest['run']['status'],'runner_exit_status':manifest['run']['exit_status'],'missing_results':missing,'missing_files_created_by_audit':False}},
            'known_completion_cost':A.cost([row]),'known_case_historical_initial_plus_revision':A.cost([initial[i],row]),'partial_pilot_known_responses_including_two_historical_initials':A.cost([initial[j] for j in cases]+[row]),
            'known_phase_metadata':{k:meta[k] for k in ['wall_seconds','load_seconds','client_cpu_seconds','server_cpu_seconds','cpu_seconds','input_tokens','output_tokens','backend_requested','backend_observed','context','max_new_tokens','diagnosis_character_cap','server_command','nonthinking_prompt_suffix_checked']},
            'acquisition_elapsed_seconds':acq['elapsed_seconds'],'separate_resource_management':resources,
            'cache_eviction':{'pre_eviction_valid_manifest_count':len(validation['manifests']),'record_reused_not_rerun':True,'restore_records':eviction['evicted'],'scope':eviction['scope']},
            'model_metadata':{'repository':meta['model_repository'],'revision':meta['revision'],'filename':meta['quantization_file'],'sha256_declared':meta['model']['sha256'],'runtime_tag':meta['runtime_tag'],'runtime_commit':meta['runtime_commit'],'large_model_bytes_rehashed_by_audit':False},
            'closed_nonthinking_prompt_suffix':suffix,'input_sha256':PINS,'hashes_after_equal_before':True,'audit_wall_seconds':time.perf_counter()-started,
            'limits':['One actual attempted outcome is unknown, never counted as zero tokens, refusal or failure; no full cost or complete2case score.',
                      'Known instruction-direction correction is a local semantic improvement, while full model fidelity remains false.',
                      'Remaining process changed batch/microbatch to128 and used caffeinate; this is not an isolated model-size or latency comparison.',
                      'Loader placement and one completed call do not establish general8GiBfit, GPU-only execution, peak global RAM or future6144context viability.',
                      'Known runtime metadata and cache-eviction records read; no model bytes, installs, process operations, missing-file creation or raw regeneration.',
                      'No C24 generation/output or C23 test outcome read. Two historical posthoc development cases, no novelty/generalization/causal claim.']}
    Path(output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'checks':A.CHECKS,'known_responses':1,'known_faithful':0,'unknown':1,'after_wrong_feasibility':after['feasibility_mismatches'],'known_tokens':[row['input_tokens'],row['output_tokens']],'runner_status':manifest['run']['status']}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    def timeout(_s,_f):raise TimeoutError('60second C22 audit limit')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(60);audit(args.output)
