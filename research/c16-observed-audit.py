"""Bounded independent recheck of conserved C16 evidence; no model/scorer imports.

Stdlib only. Algebra is interpreted at zero and basis vectors, rather than by
the production coefficient compiler. All finite predicates are reimplemented.
This script reads C16 only and never launches inference or a solver.
"""
import argparse
import ast
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import signal

BASE = Path('runs/20261115-c16-quantized-repair')
USED = set()
CHECKS = 0
SELF = 'Review the previous model against every original clause and numerical datum. Correct omissions, wrong coefficients or format. Return the COMPLETE revised JSON model only.'
GUIDED = 'Use this verifier result to correct the previous model. Recheck ALL original clauses, not just the witness. Return COMPLETE revised JSON only.'
SCHEMA = {'kind': 'schema', 'message': 'Invalid JSON or documented model schema. Rebuild a complete binary_ilp object with variables,sense,objective,constraints and explicit integer rows.'}
NO_CE = {'kind': 'no_counterexample', 'message': 'No discrepancy on the finite cube. Preserve all model fields.'}


def check(value, label):
    global CHECKS
    CHECKS += 1
    if not value:
        raise AssertionError(label)


def load(path, lines=False):
    path = Path(path)
    USED.add(str(path))
    text = path.read_text()
    return [json.loads(x) for x in text.splitlines() if x.strip()] if lines else json.loads(text)


def bounded(x):
    if type(x) is not int or x.bit_length() > 512:
        raise ValueError('integer')
    return x


def expr(node, bits, n, depth=0):
    """Return (value, syntactic variable presence), without eval or exec."""
    if depth > 64:
        raise ValueError('depth')
    if isinstance(node, ast.Constant):
        return bounded(node.value), False
    if isinstance(node, ast.Name):
        m = re.fullmatch(r'x_?(0|[1-9][0-9]*)', node.id)
        if not m or int(m[1]) >= n:
            raise ValueError('variable')
        return bits[int(m[1])], True
    if isinstance(node, ast.Subscript):
        s = node.slice
        if hasattr(ast, 'Index') and isinstance(s, ast.Index):
            s = s.value
        if not (isinstance(node.value, ast.Name) and node.value.id == 'x'
                and isinstance(s, ast.Constant) and type(s.value) is int
                and 0 <= s.value < n):
            raise ValueError('index')
        return bits[s.value], True
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        v, p = expr(node.operand, bits, n, depth+1)
        return bounded(-v if isinstance(node.op, ast.USub) else v), p
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
        a, av = expr(node.left, bits, n, depth+1)
        b, bv = expr(node.right, bits, n, depth+1)
        if isinstance(node.op, ast.Mult):
            if av and bv:
                raise ValueError('nonlinear syntax')
            v = a*b
        else:
            v = a-b if isinstance(node.op, ast.Sub) else a+b
        return bounded(v), av or bv
    raise ValueError('syntax')


def compile_row(s, n):
    if not s.strip() or len(s) > 4096 or any(c in s for c in '#;\n\r'):
        raise ValueError('row text')
    s = re.sub(r'(?<![<>=!])=(?!=)', '==', s.replace('≤', '<=').replace('≥', '>=')).strip()
    t = ast.parse(s, mode='eval')
    if sum(1 for _ in ast.walk(t)) > 256:
        raise ValueError('AST size')
    c = t.body
    if not isinstance(c, ast.Compare) or len(c.ops) != 1 or len(c.comparators) != 1:
        raise ValueError('comparison')
    op = {ast.LtE: '<=', ast.GtE: '>=', ast.Eq: '=='}.get(type(c.ops[0]))
    if op is None:
        raise ValueError('relation')
    def difference(x):
        return bounded(expr(c.left, x, n)[0] - expr(c.comparators[0], x, n)[0])
    zero = difference([0]*n)
    a = []
    for i in range(n):
        e = [0]*n
        e[i] = 1
        a.append(bounded(difference(e)-zero))
    return [a, op, bounded(-zero)]


def unique(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError('duplicate')
        d[k] = v
    return d


def parse(raw, n):
    try:
        s = raw.strip()
        lines = s.split('\n')
        if len(lines) >= 3 and lines[0] in ('```', '```json') and lines[-1] == '```':
            s = '\n'.join(lines[1:-1])
        d = json.loads(s, object_pairs_hook=unique,
                       parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite')))
        if type(d) is not dict or set(d) != {'formulation','variables','sense','objective','constraints'}:
            raise ValueError('fields')
        if d['formulation'] != 'binary_ilp' or d['sense'] != 'max':
            raise ValueError('formulation')
        if type(d['variables']) is not list or d['variables'] != list(range(n)) or any(type(x) is not int for x in d['variables']):
            raise ValueError('variables')
        def ints(v):
            return type(v) is list and len(v) == n and all(type(x) is int and abs(x) <= 10000 for x in v)
        if not ints(d['objective']) or type(d['constraints']) is not list or len(d['constraints']) > 32:
            raise ValueError('shape')
        rows = [compile_row(r,n) if type(r) is str else r for r in d['constraints']]
        for r in rows:
            if (type(r) is not list or len(r) != 3 or not ints(r[0]) or type(r[1]) is not str
                    or r[1] not in ('<=','>=','==') or type(r[2]) is not int or abs(r[2]) > 10000):
                raise ValueError('dense row')
        return dict(d, constraints=rows)
    except (ValueError, TypeError, KeyError, SyntaxError, RecursionError):
        return None


def reference(data, c, x):
    picked = {i for i, v in enumerate(x) if v}
    return (not any({a,b} <= picked for a,b in data['edges'])
            and (c['budget'] is None or sum(data['costs'][i] for i in picked) <= c['budget'])
            and (c['min_count'] is None or len(picked) >= c['min_count'])
            and (c['max_count'] is None or len(picked) <= c['max_count'])
            and set(c['required']) <= picked and not set(c['forbidden']) & picked
            and all(a not in picked or b in picked for a,b in c['implications']))


def feasible(model, x):
    for a, op, rhs in model['constraints']:
        v = sum(a[i] for i in range(len(x)) if x[i])
        if not {'<=': v <= rhs, '>=': v >= rhs, '==': v == rhs}[op]:
            return False
    return True


def value(coefficients, x):
    return sum(coefficients[i] for i in range(len(x)) if x[i])


def mask(x):
    return sum(v << i for i,v in enumerate(x))


def optimum(domain, obj):
    if not domain:
        return None, []
    best = max(value(obj,x) for x in domain)
    return best, [x for x in domain if value(obj,x) == best]


def assess(data, c, model):
    n = data['n']
    cube = list(itertools.product((0,1), repeat=n))
    ref = [x for x in cube if reference(data,c,x)]
    if model is None:
        return {'faithful':False,'stage':'schema','assignments':0,
                'feasibility_mismatches':None,'objective_mismatches':None,
                'feedback':SCHEMA,'reference_feasible_count':len(ref),
                'proposed_feasible_count':None,'optimizer_set_equal':False,
                'finite_optimization_equivalent':False,'candidate_best':None,
                'candidate_optima':[]}
    proposed = [x for x in cube if feasible(model,x)]
    witnesses = []
    wf = wv = 0
    for x in cube:
        a,b = x in ref, x in proposed
        va,vb = value(data['weights'],x),value(model['objective'],x)
        wf += a != b
        wv += va != vb
        if len(witnesses) < 3:
            if a != b:
                witnesses.append({'kind':'feasibility','x':list(x),'expected_feasible':a,'proposed_feasible':b})
            elif va != vb:
                witnesses.append({'kind':'objective','x':list(x),'expected_value':va,'proposed_value':vb})
    rb,ro = optimum(ref,data['weights'])
    pb,po = optimum(proposed,model['objective'])
    same = set(ro) == set(po)
    return {'faithful':wf == wv == 0,'stage':'finite_cube','assignments':2**n,
            'feasibility_mismatches':wf,'objective_mismatches':wv,
            'reference_feasible_count':len(ref),'proposed_feasible_count':len(proposed),
            'feedback':NO_CE if wf == wv == 0 else {'kind':'counterexamples','witnesses':witnesses},
            'optimizer_set_equal':same,'finite_optimization_equivalent':wf == 0 and same,
            'candidate_best':pb,'candidate_optima':[list(x) for x in po]}


def cost(rows):
    return {'responses':len(rows), **{k:sum(r[k] for r in rows) for k in
            ('input_tokens','output_tokens','wall_seconds','cpu_seconds')}}


def audit(output):
    cases = {x['id']:x for x in load(BASE/'test_cases.json')}
    labels = {x['id']:x['constraints'] for x in load(BASE/'private_gold.review.json')['cases'] if x['split']=='test'}
    oracle = {x['id']:x for x in load('research/c16-annotation-oracle/raw.json')['cases'] if x['split']=='test'}
    check(set(cases)==set(labels)==set(oracle), 'test labels')
    domains = {}
    for i,c in cases.items():
        data=c['data'];xs=[x for x in itertools.product((0,1),repeat=data['n']) if reference(data,labels[i],x)]
        best,opts=optimum(xs,data['weights'])
        domains[i]={'feasible_masks':sorted(mask(x) for x in xs),'feasible_count':len(xs),'max_weight':best,'optimal_masks':sorted(mask(x) for x in opts)}
        for k,v in domains[i].items():check(v==oracle[i][k], 'reviewer oracle '+i+' '+k)
    feedback=load(BASE/'test-feedback-v1/minimal.json')
    instructions=(BASE/'instructions.frozen.txt').read_text();USED.add(str(BASE/'instructions.frozen.txt'))
    traces={};phase_metadata=[];row_assessments={};allrows=[];http_count=0
    for name,phase,count in [('initial','initial',16),('direct','direct',16),('self','self',16),('guided','guided',5),('guided-continuation','guided',10)]:
        folder=BASE/('test-'+name+'-v1')/'driver';rows=load(folder/'raw.jsonl',True)
        check(len(rows)==count, 'trace count '+name)
        target=traces.setdefault(phase,{})
        for r in rows:
            i=r['id'];check(i in cases and i not in target,'unique trace '+phase+' '+i);target[i]=r;allrows.append(r)
            check(r['phase']==phase,'phase');model=parse(r['raw_response'],cases[i]['data']['n'])
            check((model is not None)==r['parsed']['valid'],'parse validity '+phase+' '+i)
            if model is not None:check(model==r['parsed']['model'],'compiled model '+phase+' '+i)
            row_assessments[(phase,i)]=(model,assess(cases[i]['data'],labels[i],model))
            expectedseed=(int(hashlib.sha256(i.encode()).hexdigest()[:8],16)+(phase!='initial'))%(2**32)
            check(r['seed']==expectedseed,'seed')
            messages=r['messages'];check(messages[0]=={'role':'system','content':instructions},'system instructions')
            check(json.loads(messages[1]['content'])=={'intention':cases[i]['intention'],'data':cases[i]['data']},'public input')
            if phase in ('initial','direct'):check(len(messages)==2,'direct messages')
            else:
                check(len(messages)==4 and messages[2]=={'role':'assistant','content':traces['initial'][i]['raw_response']},'initial history')
                check(messages[3]['role']=='user','repair user')
                if phase=='self':check(messages[3]['content']==SELF,'self instruction')
                else:check(json.loads(messages[3]['content'])=={'verifier_feedback':feedback[i],'instruction':GUIDED},'guided feedback payload')
            prompt=''.join('<|im_start|>'+m['role']+'\n'+m['content']+'<|im_end|>\n' for m in messages)+'<|im_start|>assistant\n'
            check(hashlib.sha256(prompt.encode()).hexdigest()==r['prompt_sha256'],'prompt hash')
            check(len(r['input_token_ids'])==r['input_tokens']<=1663,'input count')
            check(len(r['generated_token_ids'])==len(r['generated_token_log_probabilities'])==r['output_tokens']<=384,'output count')
            responsepath=folder/r['http_response'];response=load(responsepath);request=load(responsepath.with_name(responsepath.name.replace('.response.','.request.')));http_count+=1
            check(response['content']==r['raw_response'] and response['tokens']==r['generated_token_ids'],'HTTP content/tokens')
            check(response['tokens_evaluated']==r['input_tokens'] and response['tokens_predicted']==r['output_tokens'],'HTTP counts')
            check(request['prompt']==r['input_token_ids'],'HTTP input IDs')
            for k,v in {'temperature':.2,'top_k':50,'top_p':1.,'n_predict':384,'post_sampling_probs':True,'return_tokens':True,'n_probs':1,'samplers':['top_k','top_p','temperature'],'seed':expectedseed}.items():check(request[k]==v,'sampling request '+k)
            check(response['prompt']==prompt,'HTTP prompt text')
            probs=response['completion_probabilities'];check(len(probs)==r['output_tokens'],'chosen probs count')
            lps=[]
            for token,p,lp in zip(r['generated_token_ids'],probs,r['generated_token_log_probabilities']):
                check(p['id']==token and 0<p['prob']<=1,'chosen-token probability')
                check(math.isclose(math.log(p['prob']),lp,abs_tol=1e-12),'token logprob');lps.append(lp)
            check(math.isclose(sum(lps)/len(lps),r['mean_generated_log_probability'],abs_tol=1e-12),'mean score')
            check(r['finish_reason']=={'eos':'eos','limit':'token_limit'}[response['stop_type']],'finish reason')
            check(r['wall_seconds']>=0 and r['cpu_seconds']>=0,'nonnegative row times')
        mp=folder/'generation.json'
        if mp.exists():
            m=load(mp)
            check(m['status']=='completed' and m['completed']==m['planned']==count,'phase status')
            for k in ('input_tokens','output_tokens'):check(m[k]==sum(r[k] for r in rows),'phase tokens '+k)
            check(m['context']==2048 and m['threads']==4 and m['max_new_tokens']==384,'phase limits')
            phase_metadata.append({'trace':name, **{k:m[k] for k in ('status','completed','input_tokens','output_tokens','wall_seconds','load_seconds','client_cpu_seconds','server_cpu_seconds','cpu_seconds','backend_requested','backend_observed','runtime_tag','runtime_commit','revision')}})
    missing=sorted(set(cases)-set(traces['guided']));check(missing==['54969ba6bb41'],'one missing')
    incident=load(BASE/'disk-incident-guided.json');check(incident['interrupted_attempt_id']==missing[0] and incident['observed_responses']==5,'incident inventory')
    check(set(incident['never_attempted_ids'])==set(r['id'] for r in load(BASE/'test-guided-continuation-v1/driver/raw.jsonl',True)),'continuation only unattempted')
    missing_request=load(BASE/'test-guided-v1/driver/http/005.request.json')
    check(not (BASE/'test-guided-v1/driver/http/005.response.json').exists(),'lost response remains absent')
    check(missing_request['seed']==(int(hashlib.sha256(missing[0].encode()).hexdigest()[:8],16)+1)%(2**32),'lost request ID via seed')
    reports={r['id']:r for r in load(BASE/'test-feedback-v1/reports.jsonl',True)}
    for i in cases:
        a=row_assessments[('initial',i)][1];check(a['feedback']==feedback[i],'feedback minimal '+i)
        for k,v in reports[i]['verification'].items():
            if k in a and k!='feedback':check(v==a[k],'feedback report '+i+' '+k)
        check(reports[i]['feedback_wall_seconds']>=0,'feedback time')
    selected={};summaries={};case_results=[]
    for method in ('initial','direct','self','guided'):
        selected[method]={}
        for i in cases:
            if method=='guided' and i in missing:continue
            initial=traces['initial'][i]
            if method=='initial':index=0
            elif method=='direct':
                choices=[initial,traces['direct'][i]]
                index=max(range(2),key=lambda k:(row_assessments[(choices[k]['phase'],i)][0] is not None,choices[k]['mean_generated_log_probability'],-k))
            else:
                second=row_assessments[(method,i)][0]
                index=1 if second is not None else (0 if row_assessments[('initial',i)][0] is not None else 1)
            phase='initial' if index==0 else method
            model,a=row_assessments[(phase,i)]
            selected[method][i]={'index':index,'phase':phase,'model':model,'assessment':a}
        ss=selected[method]
        def stats(ids):
            return {'observed':len(ids),'schema_valid':sum(ss[i]['model'] is not None for i in ids),'faithful':sum(ss[i]['assessment']['faithful'] for i in ids),'finite_optimization_equivalent':sum(ss[i]['assessment']['finite_optimization_equivalent'] for i in ids),'optimizer_set_equal':sum(ss[i]['assessment']['optimizer_set_equal'] for i in ids)}
        summaries[method]={'all':stats(list(ss)),'feasible':stats([i for i in ss if domains[i]['feasible_count']]),'infeasible':stats([i for i in ss if not domains[i]['feasible_count']]),'fr':stats([i for i in ss if cases[i]['language']=='fr']),'en':stats([i for i in ss if cases[i]['language']=='en']),'faithful_ids':[i for i in ss if ss[i]['assessment']['faithful']]}
        summaries[method]['repairs_from_initial']=sum(not row_assessments[('initial',i)][1]['faithful'] and ss[i]['assessment']['faithful'] for i in ss)
        summaries[method]['regressions_from_initial']=sum(row_assessments[('initial',i)][1]['faithful'] and not ss[i]['assessment']['faithful'] for i in ss)
    paired=load(BASE/'partial-score/paired-results/raw.jsonl',True)
    check({p['id'] for p in paired}==set(cases)-set(missing) and len(paired)==15,'paired set')
    portfolios=solverchecks=0;solver_seconds=0.;selected_seconds=0.
    for p in paired:
        i=p['id'];check(p['initial_feedback']==feedback[i],'paired feedback')
        for method,r in p['results'].items():
            s=selected[method][i];a=s['assessment'];check(r['selected_candidate_index']==s['index'] and r['selected_phase']==s['phase'],'selection '+i+' '+method)
            check(r['model']==s['model'],'selected model')
            for k,v in r['verification'].items():
                if k in a and k!='feedback':check(v==a[k],'verification '+i+' '+method+' '+k)
            if a['stage']!='schema':check(r['verification']['feedback']==a['feedback'],'verification witnesses')
            for k,v in r['optimization_diagnostics'].items():check(v==a[k],'optimization diagnostic')
            pf=r['portfolio']
            if s['model'] is None:
                check(pf is None,'invalid proposal no portfolio');continue
            portfolios+=1;opts={tuple(x) for x in a['candidate_optima']};best=a['candidate_best'];status='optimal' if opts else 'infeasible'
            check(pf['concordance'] and pf['comparison_error'] is None,'portfolio concordance')
            check(pf['objective']==best and (tuple(pf['solution']) in opts if opts else pf['solution'] is None),'portfolio optimum')
            solvermap={z['solver']:z for z in pf['solvers']};check(set(solvermap)=={'enumeration_dfs','scipy_highs_milp'},'two actual solvers')
            for name,z in solvermap.items():
                solverchecks+=1;check(z['status']==status and z['objective']==best,'solver status/objective')
                check(tuple(z['solution']) in opts if opts else z['solution'] is None,'solver solution')
                check(z['seconds']>=0,'solver time')
                if name=='enumeration_dfs':
                    check(z['visited_leaves']==2**cases[i]['data']['n'],'DFS leaves')
                    check({tuple(x) for x in z['all_optima']}==opts,'DFS all optima')
                else:
                    check(z['raw_status']==(0 if opts else 2),'HiGHS status')
                    check(math.isclose(z['raw_min_objective'],-best,abs_tol=1e-7) if opts else z['raw_min_objective'] is None,'HiGHS raw objective')
            fastest=min(pf['solvers'],key=lambda z:z['seconds'])
            check(pf['selected_solver']==fastest['solver'] and pf['selected_solver_seconds']==fastest['seconds'],'ex-post fastest selection')
            total=sum(z['seconds'] for z in pf['solvers'])
            check(pf['total_portfolio_seconds']+1e-9>=total,'both solver costs charged')
            check(r['usable_for_original_problem']==a['faithful'],'usable requires fidelity')
            solver_seconds+=pf['total_portfolio_seconds'];selected_seconds+=pf['selected_solver_seconds']
    for i,c in cases.items():
        case_results.append({'id':i,'language':c['language'],'n':c['data']['n'],'reference':domains[i],
                             'methods':{m:{k:v for k,v in ss[i].items() if k!='model'} for m,ss in selected.items() if i in ss},'guided_unknown':i in missing})
    author=load(BASE/'partial-score/metrics.json')
    for m in summaries:check(author['full_methods'][m]=={k:summaries[m]['all'][k] for k in ('observed','faithful')},'existing aggregate '+m)
    physical=cost(allrows)
    for k in ('input_tokens','output_tokens','wall_seconds','cpu_seconds'):check(math.isclose(physical[k],author['observed_physical_cost'][k],abs_tol=1e-8),'existing cost '+k)
    guided=summaries['guided']['all']['faithful'];selfn=summaries['self']['all']['faithful']
    known_arm={m:cost(list(traces['initial'].values())+list(traces[m].values())) for m in ('direct','self','guided')}
    paired_cost={m:cost([traces['initial'][i] for i in cases if i not in missing]+[traces[m][i] for i in cases if i not in missing]) for m in ('direct','self','guided')}
    complete_phase_cpu=sum(m['cpu_seconds'] for m in phase_metadata)
    result={'audit_status':'completed','computation':'independent stdlib interpretation and exact finite enumeration; no production scorer/parser/verifier/solver imported',
            'bounds':{'cases':16,'max_n':7,'max_cube':128,'timeout_seconds':60},'checks_passed':CHECKS,
            'inventory':{'attempted_calls':63+len(missing),'conserved_responses':len(allrows),'http_pairs_checked':http_count,'paired_cases':len(paired),'unknown_guided_ids':missing,'unknown_output_never_imputed':True,'unknown_request_input_tokens':len(missing_request['prompt'])},
            'methods':summaries,'guided_faithful_bounds':[guided,guided+len(missing)],'guided_minus_self_bounds':[guided-selfn,guided+len(missing)-selfn],
            'H16_gain_at_least_3_possible':guided+len(missing)-selfn>=3,
            'physical_observed_cost':physical,'known_response_cost_per_arm_with_shared_initial':known_arm,'paired_15_cost_per_arm':paired_cost,
            'feedback_wall_seconds':sum(r['feedback_wall_seconds'] for r in reports.values()),
            'solver_evidence':{'recorded_portfolios_checked':portfolios,'recorded_solver_runs_checked':solverchecks,'total_portfolio_seconds':solver_seconds,'selected_solver_seconds':selected_seconds,'new_solver_runs':0},
            'complete_phase_metadata':phase_metadata,'complete_phase_process_cpu_seconds_lower_bound':complete_phase_cpu,
            'limits':['One attempted guided response lost after ENOSPC; its outcome, generated tokens and process cost are unknown.',
                      'Client row CPU excludes server CPU; only four phase process records survive. No energy or monetary estimate.',
                      'Strict fidelity compares all cube objective values, including infeasible assignments; both-empty feasible domains can be extensionally equal.',
                      'All recorded solver answers checked against exact candidate optima; no fresh HiGHS execution or original timing reproduction.',
                      'Token probabilities are pinned API scores after sampling; grammar branch affects normalization. Direct selection is heuristic.',
                      'This role did not author the C16 scoring module or reviewer labels, but authored early C16 inference infrastructure and other corpora. Role independence is limited; no human/model-family blindness claim.',
                      'No C19 response read; no population guarantee, quantum run, causal model/quantization claim or novelty claim.'],
            'cases':case_results}
    result['input_sha256']={s:hashlib.sha256(Path(s).read_bytes()).hexdigest() for s in sorted(USED)}
    Path(output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'checks':CHECKS,'responses':len(allrows),'methods':{m:summaries[m]['all'] for m in summaries},'guided_minus_self_bounds':result['guided_minus_self_bounds'],'solver_runs_checked':solverchecks},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    def expired(_s,_f):raise TimeoutError('60-second independent audit deadline')
    signal.signal(signal.SIGALRM,expired);signal.alarm(60)
    audit(args.output)
