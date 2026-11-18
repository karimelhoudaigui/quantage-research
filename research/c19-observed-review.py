"""Post-test C19 audit: stdlib, exact cubes, no production scorer imports.

Reuses the separately written C16 audit's algebra interpreter and reference
predicates. This role authored C19 corpus; that limitation is explicit.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import signal

SPEC = importlib.util.spec_from_file_location('independent_c16_audit', 'research/c16-observed-audit.py')
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)
B = Path('runs/20261115-c19-instruct-repair')
USED = A.USED
load, check = A.load, A.check


def controls():
    model={'formulation':'binary_ilp','variables':[0,1,2,3],'sense':'max',
           'objective':[1,2,3,4],'constraints':['2*x0 + x1 <= 3', 'x2-x3=0']}
    p=A.parse(json.dumps(model),4)
    check(p['constraints']==[[[2,1,0,0],'<=',3],[[0,0,1,-1],'==',0]],'hand algebra')
    for bad in ['x0*x1<=1','x4<=1','x[1+1]<=1','x0;__import__("os")<=1']:
        check(A.parse(json.dumps(dict(model,constraints=[bad])),4) is None,'hand reject '+bad)
    d={'n':4,'weights':[2,3,5,7],'costs':[1,2,3,4],'edges':[[0,3]]}
    c={'budget':3,'min_count':2,'max_count':2,'required':[0],'forbidden':[3],'implications':[[0,1]]}
    xs=[x for x in itertools.product((0,1),repeat=4) if A.reference(d,c,x)]
    check(xs==[(1,1,0,0)],'hand reference singleton')
    check(A.optimum(xs,d['weights'])==(5,[(1,1,0,0)]),'hand optimum')
    c=dict(c,budget=2)
    check(not any(A.reference(d,c,x) for x in itertools.product((0,1),repeat=4)),'hand empty domain')
    return 8


def audit(output):
    check((B/'test-score-v2/metrics.json').exists(),'complete score prerequisite')
    hand=controls()
    cases={x['id']:x for x in load(B/'test_cases.json')}
    labels={x['id']:x['constraints'] for x in load(B/'private_gold.review.json')['cases']}
    oracle={x['id']:x for x in load('research/c19-annotation-oracle/raw.json')['cases']}
    check(len(cases)==20 and set(cases)==set(labels)==set(oracle),'case inventory')
    domains={}
    for i,c in cases.items():
        d=c['data'];xs=[x for x in itertools.product((0,1),repeat=d['n']) if A.reference(d,labels[i],x)]
        best,opts=A.optimum(xs,d['weights'])
        domains[i]={'feasible_masks':sorted(A.mask(x) for x in xs),'feasible_count':len(xs),'max_weight':best,'optimal_masks':sorted(A.mask(x) for x in opts)}
        for k,v in domains[i].items():check(v==oracle[i][k],'oracle '+i+' '+k)
    check(sum(not d['feasible_count'] for d in domains.values())==3,'three infeasible')
    feedback=load(B/'test-feedback-v2/minimal.json')
    reports={r['id']:r for r in load(B/'test-feedback-v2/reports.jsonl',True)}
    instructions=(B/'instructions.frozen.txt').read_text();USED.add(str(B/'instructions.frozen.txt'))
    physical=[('initial','initial','test-initial-v2',20),('direct','direct','test-direct-v2',20),
              ('self-original','self','test-self-v2',13),('self-continuation','self','test-self-remaining-inference-v2',7),
              ('guided','guided','test-guided-v2',20)]
    traces={};assessed={};allrows=[];metas=[];allhttp=0
    for name,phase,dirname,count in physical:
        folder=B/dirname/'driver';rows=load(folder/'raw.jsonl',True)
        check(len(rows)==count,'phase count '+name);target=traces.setdefault(phase,{})
        requests=list((folder/'http').glob('[0-9][0-9][0-9].request.json'))
        responses=list((folder/'http').glob('[0-9][0-9][0-9].response.json'))
        check(len(requests)==len(responses)==count,'HTTP physical attempts '+name)
        for r in rows:
            i=r['id'];check(i in cases and i not in target,'unique physical call '+phase+' '+i)
            target[i]=r;allrows.append(r);check(r['phase']==phase,'row phase')
            model=A.parse(r['raw_response'],cases[i]['data']['n'])
            check((model is not None)==r['parsed']['valid'],'parse validity '+phase+' '+i)
            if model is not None:check(model==r['parsed']['model'],'normalized model '+phase+' '+i)
            assessed[(phase,i)]=(model,A.assess(cases[i]['data'],labels[i],model))
            seed=(int(hashlib.sha256(i.encode()).hexdigest()[:8],16)+(phase!='initial'))%(2**32)
            check(r['seed']==seed,'seed');messages=r['messages']
            check(messages[0]=={'role':'system','content':instructions},'system')
            check(messages[1]['role']=='user' and json.loads(messages[1]['content'])=={'intention':cases[i]['intention'],'data':cases[i]['data']},'public user')
            if phase in ('initial','direct'):check(len(messages)==2,'two-message initial/direct')
            else:
                check(len(messages)==4 and messages[2]=={'role':'assistant','content':traces['initial'][i]['raw_response']} and messages[3]['role']=='user','repair history')
                if phase=='self':check(messages[3]['content']==A.SELF,'self instruction')
                else:check(json.loads(messages[3]['content'])=={'verifier_feedback':feedback[i],'instruction':A.GUIDED},'guided payload')
            responsepath=folder/r['http_response'];response=load(responsepath)
            stem=str(responsepath).removesuffix('.response.json') if hasattr(str,'removesuffix') else str(responsepath)[:-len('.response.json')]
            request=load(stem+'.request.json');template_request=load(stem+'.template.request.json');template=load(stem+'.template.response.json')
            prompt=template['prompt'];check(template_request=={'messages':messages},'template request')
            check(not prompt.rstrip().endswith('<think>'),'no open reasoning')
            check(hashlib.sha256(prompt.encode()).hexdigest()==r['prompt_sha256'] and response['prompt']==prompt,'rendered prompt SHA')
            promptfile=Path(stem+'.prompt.txt');USED.add(str(promptfile));check(promptfile.read_text()==prompt,'prompt file')
            check(len(r['input_token_ids'])==r['input_tokens']<=3583 and request['prompt']==r['input_token_ids'],'input tokens')
            check(len(r['generated_token_ids'])==len(r['generated_token_log_probabilities'])==r['output_tokens']<=512,'output tokens')
            check(response['content']==r['raw_response'] and response['tokens']==r['generated_token_ids'],'HTTP response')
            check(response['tokens_evaluated']==r['input_tokens'] and response['tokens_predicted']==r['output_tokens'],'HTTP counts')
            for k,v in {'temperature':.7,'top_k':20,'top_p':.8,'n_predict':512,'post_sampling_probs':True,'return_tokens':True,'n_probs':1,'samplers':['top_k','top_p','temperature'],'seed':seed}.items():check(request[k]==v,'request '+k)
            probs=response['completion_probabilities'];check(len(probs)==r['output_tokens'],'prob count')
            logs=[]
            for token,p,lp in zip(r['generated_token_ids'],probs,r['generated_token_log_probabilities']):
                check(p['id']==token and 0<p['prob']<=1,'chosen probability')
                check(math.isclose(math.log(p['prob']),lp,abs_tol=1e-12),'log probability');logs.append(lp)
            check(math.isclose(sum(logs)/len(logs),r['mean_generated_log_probability'],abs_tol=1e-12),'selection score')
            check(r['finish_reason']=={'eos':'eos','limit':'token_limit'}[response['stop_type']],'finish')
            check(r['wall_seconds']>=r['generation_wall_seconds']>=0 and r['cpu_seconds']>=0,'times');allhttp+=1
        m=load(folder/'generation.json')
        check(m['completed']==count and m['planned']==(20 if name=='self-original' else count),'metadata counts')
        check(m['status']==('partial_error' if name=='self-original' else 'completed'),'metadata status')
        if name=='self-original':check('disk reserve below 1GiB' in m['error'],'pre-call disk stop')
        for k in ('input_tokens','output_tokens'):check(m[k]==sum(r[k] for r in rows),'metadata '+k)
        check(m['context']==4096 and m['max_new_tokens']==512 and m['threads']==4,'runtime limits')
        metas.append({'trace':name,**{k:m[k] for k in ('status','completed','planned','input_tokens','output_tokens','wall_seconds','load_seconds','client_cpu_seconds','server_cpu_seconds','cpu_seconds','backend_requested','backend_observed','runtime_tag','runtime_commit','revision')}})
    for phase,rows in traces.items():check(set(rows)==set(cases),'complete '+phase)
    union=load(B/'test-self-union-v2/driver/raw.jsonl',True)
    check(len(union)==20 and {r['id']:r for r in union}==traces['self'],'union exact physical rows')
    unionmeta=load(B/'test-self-union-v2/driver/generation.json')
    for k in ('input_tokens','output_tokens','wall_seconds','load_seconds','client_cpu_seconds','server_cpu_seconds','cpu_seconds'):
        check(math.isclose(unionmeta[k],sum(m[k] for m in metas if m['trace'].startswith('self-')),abs_tol=1e-8),'union both loads '+k)
    incident=load(B/'self-resource-reconciliation.json')
    oldids={r['id'] for r in load(B/'test-self-v2/driver/raw.jsonl',True)}
    check(incident['next_call_not_attempted'] and set(incident['never_attempted_ids'])==set(cases)-oldids,'no repeated attempted call')
    for i in cases:
        a=assessed[('initial',i)][1];check(a['feedback']==feedback[i],'minimal feedback '+i)
        for k,v in reports[i]['verification'].items():
            if k in a and k!='feedback':check(v==a[k],'initial verification '+i+' '+k)
    selected={};methods={}
    for method in ('initial','direct','self','guided'):
        selected[method]={}
        for i in cases:
            if method=='initial':index=0
            elif method=='direct':
                options=[traces['initial'][i],traces['direct'][i]]
                index=max(range(2),key=lambda k:(assessed[(options[k]['phase'],i)][0] is not None,options[k]['mean_generated_log_probability'],-k))
            else:index=1 if assessed[(method,i)][0] is not None else (0 if assessed[('initial',i)][0] is not None else 1)
            phase='initial' if index==0 else method;model,a=assessed[(phase,i)]
            selected[method][i]={'index':index,'phase':phase,'model':model,'assessment':a}
        s=selected[method]
        def stats(ids):
            return {'observed':len(ids),'schema_valid':sum(s[i]['model'] is not None for i in ids),'faithful':sum(s[i]['assessment']['faithful'] for i in ids),'finite_optimization_equivalent':sum(s[i]['assessment']['finite_optimization_equivalent'] for i in ids),'optimizer_set_equal':sum(s[i]['assessment']['optimizer_set_equal'] for i in ids)}
        methods[method]={'all':stats(list(s)),'feasible':stats([i for i in s if domains[i]['feasible_count']]),'infeasible':stats([i for i in s if not domains[i]['feasible_count']]),'fr':stats([i for i in s if cases[i]['language']=='fr']),'en':stats([i for i in s if cases[i]['language']=='en']),
                         'faithful_ids':[i for i in s if s[i]['assessment']['faithful']],
                         'repairs_from_initial':[i for i in s if not assessed[('initial',i)][1]['faithful'] and s[i]['assessment']['faithful']],
                         'regressions_from_initial':[i for i in s if assessed[('initial',i)][1]['faithful'] and not s[i]['assessment']['faithful']],
                         'schema_repairs_from_initial':[i for i in s if assessed[('initial',i)][0] is None and s[i]['model'] is not None],
                         'math_repairs_from_initial':[i for i in s if assessed[('initial',i)][0] is not None and not assessed[('initial',i)][1]['faithful'] and s[i]['assessment']['faithful']]}
    scored=load(B/'test-score-v2/raw.jsonl',True)
    check(len(scored)==20 and {r['id'] for r in scored}==set(cases),'scored rows')
    portfolios=solverchecks=0;portfolio_seconds=selected_seconds=0.
    feasible_original_solution={m:0 for m in selected};optimal_original_solution={m:0 for m in selected}
    for p in scored:
        i=p['id'];check(p['initial_feedback']==feedback[i],'scored initial feedback')
        for method,r in p['results'].items():
            s=selected[method][i];a=s['assessment'];check(r['selected_candidate_index']==s['index'] and r['selected_phase']==s['phase'] and r['model']==s['model'],'scored selection')
            for k,v in r['verification'].items():
                if k in a and k!='feedback':check(v==a[k],'scored verification '+i+' '+method+' '+k)
            if a['stage']!='schema':check(r['verification']['feedback']==a['feedback'],'scored witnesses')
            for k,v in r['optimization_diagnostics'].items():check(v==a[k],'scored optimum sets')
            pf=r['portfolio']
            if s['model'] is None:check(pf is None,'invalid no solver');continue
            portfolios+=1;opts={tuple(x) for x in a['candidate_optima']};best=a['candidate_best']
            check(pf['concordance'] and pf['comparison_error'] is None,'concordance')
            check(pf['objective']==best and (tuple(pf['solution']) in opts if opts else pf['solution'] is None),'portfolio answer')
            if pf['solution'] is not None:
                original_ok=A.reference(cases[i]['data'],labels[i],pf['solution'])
                feasible_original_solution[method]+=original_ok
                optimal_original_solution[method]+=original_ok and A.value(cases[i]['data']['weights'],pf['solution'])==domains[i]['max_weight']
            solvermap={z['solver']:z for z in pf['solvers']};check(set(solvermap)=={'enumeration_dfs','scipy_highs_milp'},'solver pair')
            for name,z in solvermap.items():
                solverchecks+=1;check(z['status']==('optimal' if opts else 'infeasible') and z['objective']==best,'solver optimum')
                check(tuple(z['solution']) in opts if opts else z['solution'] is None,'solver witness')
                check(z['seconds']>=0,'solver time')
                if name=='enumeration_dfs':
                    check(z['visited_leaves']==2**cases[i]['data']['n'] and {tuple(x) for x in z['all_optima']}==opts,'DFS all optima')
                else:
                    check(z['raw_status']==(0 if opts else 2),'HiGHS status')
                    check(math.isclose(z['raw_min_objective'],-best,abs_tol=1e-7) if opts else z['raw_min_objective'] is None,'HiGHS objective')
            fastest=min(pf['solvers'],key=lambda z:z['seconds'])
            check(pf['selected_solver']==fastest['solver'] and pf['selected_solver_seconds']==fastest['seconds'],'solver selection')
            check(pf['total_portfolio_seconds']+1e-9>=sum(z['seconds'] for z in pf['solvers']),'full portfolio charge')
            check(r['usable_for_original_problem']==a['faithful'],'usable')
            portfolio_seconds+=pf['total_portfolio_seconds'];selected_seconds+=pf['selected_solver_seconds']
    for m in methods:
        methods[m]['returned_solution_feasible_for_original']=feasible_original_solution[m]
        methods[m]['returned_solution_optimal_for_original']=optimal_original_solution[m]
    # Consult author aggregates only after the reconstruction above.
    author=load(B/'test-score-v2/metrics.json')
    for method,s in selected.items():
        def aggregate(ids):
            return {'observed':len(ids),'schema_valid':sum(s[i]['model'] is not None for i in ids),
                    'faithful':sum(s[i]['assessment']['faithful'] for i in ids),
                    'optimization_equivalent':sum(s[i]['assessment']['finite_optimization_equivalent'] for i in ids),
                    'feasibility_mismatches':sum(s[i]['assessment']['feasibility_mismatches'] or 0 for i in ids),
                    'objective_mismatches':sum(s[i]['assessment']['objective_mismatches'] or 0 for i in ids),
                    'assignments_compared':sum(s[i]['assessment']['assignments'] for i in ids),
                    'regressions_from_faithful':sum(assessed[('initial',i)][1]['faithful'] and not s[i]['assessment']['faithful'] for i in ids),
                    'repairs_to_faithful':sum(not assessed[('initial',i)][1]['faithful'] and s[i]['assessment']['faithful'] for i in ids)}
        for k,v in aggregate(list(cases)).items():check(author['methods'][method][k]==v,'author aggregate '+method+' '+k)
        for axis,groups in [('language',{'fr':[i for i in cases if cases[i]['language']=='fr'],'en':[i for i in cases if cases[i]['language']=='en']}),
                            ('reference_feasibility',{'feasible':[i for i in cases if domains[i]['feasible_count']],'infeasible':[i for i in cases if not domains[i]['feasible_count']]})]:
            for group,ids in groups.items():
                for k,v in aggregate(ids).items():check(author['strata'][axis][group][method][k]==v,'author stratum '+method+' '+group+' '+k)
    physical_cost=A.cost(allrows)
    check(author['physical_generation_calls']==len(allrows),'author physical calls')
    for k,v in author['physical_generation_cost'].items():check(math.isclose(physical_cost[k],v,abs_tol=1e-8),'author physical cost '+k)
    for method in ('direct','self','guided'):
        arm=A.cost(list(traces['initial'].values())+list(traces[method].values()))
        for k,v in author['attributable_cost_per_arm'][method].items():check(math.isclose(arm[k],v,abs_tol=1e-8),'author arm cost '+method+' '+k)
    frozen=load(B/'freeze-test-v2.json');freeze_small={};freeze_large=[]
    for p,h in frozen['sha256'].items():
        path=Path(p)
        if path.exists() and path.stat().st_size<=64*1024*1024:
            USED.add(p);got=hashlib.sha256(path.read_bytes()).hexdigest();check(got==h,'frozen input '+p);freeze_small[p]=h
        else:freeze_large.append(p)
    gain=methods['guided']['all']['faithful']-methods['self']['all']['faithful'];reg=len(methods['guided']['regressions_from_initial'])
    check(author['H19']['guided_minus_self_faithful']==gain and author['H19']['guided_regressions']==reg,'author H19')
    check(math.isclose(author['scored_portfolio_seconds_total'],portfolio_seconds,abs_tol=1e-8),'author portfolio cost')
    result={'audit_status':'completed','independence':'Independent scorer implementation, but auditor authored C19 corpus; not a blind or author-independent corpus review. Reviewer labels and oracle were independently prepared.',
            'checks_passed':A.CHECKS,'hand_controls_passed':hand,'inventory':{'cases':20,'physical_calls':len(allrows),'http_pairs':allhttp,'unknown_responses':0,'self_original':13,'self_never_attempted_continuation':7},
            'methods':methods,'H19':{'guided_minus_self':gain,'guided_regressions_from_initial':reg,'gain_at_least_four':gain>=4,'regressions_at_most_one':reg<=1,'supported':gain>=4 and reg<=1},
            'physical_cost':physical_cost,'attributable_arm_cost_shared_initial':{m:A.cost(list(traces['initial'].values())+list(traces[m].values())) for m in ('direct','self','guided')},
            'phase_process_metadata':metas,'total_process_wall_seconds':sum(m['wall_seconds'] for m in metas),'total_process_cpu_seconds':sum(m['cpu_seconds'] for m in metas),'total_load_seconds':sum(m['load_seconds'] for m in metas),
            'feedback_wall_seconds':sum(r['feedback_wall_seconds'] for r in reports.values()),
            'solver_evidence':{'portfolios_checked':portfolios,'solver_results_checked':solverchecks,'total_portfolio_seconds':portfolio_seconds,'selected_solver_seconds':selected_seconds,'new_solver_runs':0},
            'freeze_small_artifacts_verified':freeze_small,'freeze_large_artifacts_not_rehashed':freeze_large,
            'author_metrics_observed_after_reconstruction':author,
            'cases':[{'id':i,'language':c['language'],'n':c['data']['n'],'reference':domains[i],'methods':{m:{k:v for k,v in ss[i].items() if k!='model'} for m,ss in selected.items()}} for i,c in cases.items()],
            'limits':['Corpus author served as score auditor after other agent quota failures; independent reviewer annotations are used but this is not a fully independent final review.',
                      'Hand controls and exact enumeration check the conserved candidate models; no new model generation, tokenizer, GGUF conversion, runtime execution or solver benchmark.',
                      'Token probabilities are processed pinned-API heuristics; not global grammar-conditioned likelihoods.',
                      'Self13+7 continuation has two model loads; recorded client/server phase CPU and wall time counted. Parent housekeeping CPU, host load, energy and complete session cost are not measured; latency is descriptive.',
                      'No population inference from 20 convenience instances, no causal claim comparing C16 to C19, no novelty or QPU claim.']}
    result['input_sha256']={s:hashlib.sha256(Path(s).read_bytes()).hexdigest() for s in sorted(USED)}
    Path(output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'checks':A.CHECKS,'calls':len(allrows),'methods':{m:methods[m]['all'] for m in methods},'H19':result['H19'],'solver_results_checked':solverchecks}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args()
    def expire(_s,_f):raise TimeoutError('60-second C19 audit deadline')
    signal.signal(signal.SIGALRM,expire);signal.alarm(60);audit(args.output)
