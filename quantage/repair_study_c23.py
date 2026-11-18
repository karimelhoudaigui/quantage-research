"""C23 prospective full-vs-literal-patch comparison; no model execution.

Primary comparison is guided tool patch versus self patch. Direct full-model
generation is secondary. H23 gain>=3/regressions<=1 is a proposal to freeze
before any held-out observations, not a data-derived result.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import time
from .repair_model import verify_model, model_feasible, objective_value
from .repair_language import parse_proposal as parse_model
from .repair_feedback import optimization_diagnostics
from .repair_patch_tool_language import parse_patch
from .repair_trace_feedback import build_feedback, validate_feedback
from .repair_patch_scale_inference import SELF_INSTRUCTION, GUIDED_INSTRUCTION
from .repair_model import no_duplicates


def strict_json(text):
    def reject(_):
        raise ValueError('nonfinite input JSON')
    return json.loads(text, object_pairs_hook=no_duplicates, parse_constant=reject)


def rows(path):
    return [strict_json(s) for s in path.read_text().splitlines()]


def trace_from_message(row, n):
    follow = strict_json(row['messages'][3]['content'])
    fields = {'verifier_feedback','candidate_evaluation_tool','gloss','instruction'}
    if type(follow) is not dict or set(follow) != fields or follow['instruction'] != GUIDED_INSTRUCTION:
        raise ValueError('closed guided tool message required')
    return validate_feedback({'verdict':follow['verifier_feedback'],
                              'candidate_evaluations':follow['candidate_evaluation_tool'],
                              'gloss':follow['gloss']}, n)


def indexed(path, public, expected_phase, initial=None, replay_times=None):
    if expected_phase not in ('initial','direct','self','guided'):
        raise ValueError('unknown C23 phase')
    patch_phase = expected_phase in ('self','guided')
    if patch_phase and initial is None:
        raise ValueError('patch replay requires the actual initial raw responses')
    records = rows(path)
    result = {r['id']:r for r in records}
    if len(result) != len(records) or set(result) != set(public):
        raise ValueError('complete unique generation matrix required, no imputation')
    for i, row in result.items():
        if row['phase'] != expected_phase or type(row['output_tokens']) is not int or not 0 < row['output_tokens'] <= 1024:
            raise ValueError('wrong phase or output budget')
        ids=row['generated_token_ids']; logps=row['generated_token_log_probabilities']
        if len(ids) != row['output_tokens'] or len(logps) != len(ids) or not all(type(t) is int and t>=0 for t in ids):
            raise ValueError('token count mismatch')
        if not all(type(x) in (int,float) and math.isfinite(x) and x<=0 for x in logps):
            raise ValueError('nonfinite token log probability')
        if (type(row['mean_generated_log_probability']) not in (int,float) or not math.isfinite(row['mean_generated_log_probability']) or abs(sum(logps)/len(logps)-row['mean_generated_log_probability']) > 1e-12):
            raise ValueError('mean token log probability mismatch')
        if type(row['input_tokens']) is not int or not 0 < row['input_tokens'] <= 3071 or row['finish_reason'] not in ('eos','token_limit'):
            raise ValueError('input budget or unexplained finish')
        if row['finish_reason']=='token_limit' and row['output_tokens'] != 1024:
            raise ValueError('unexplained early stop')
        prompt_ids=row.get('input_token_ids')
        if type(prompt_ids) is not list or len(prompt_ids)!=row['input_tokens'] or any(type(t) is not int or t<0 for t in prompt_ids):
            raise ValueError('input token count mismatch')
        messages=row['messages']
        count=4 if patch_phase else 2
        if (type(messages) is not list or len(messages)!=count
                or any(type(m) is not dict or set(m)!={'role','content'} or type(m['content']) is not str for m in messages)
                or messages[0]['role']!='system' or messages[1]['role']!='user'):
            raise ValueError('unexpected recorded message structure')
        user=strict_json(messages[1]['content'])
        if user != {'intention':public[i]['intention'],'data':public[i]['data']}:
            raise ValueError('model input differs')
        expected_seed=(int(hashlib.sha256(i.encode()).hexdigest()[:8],16)+(0 if expected_phase=='initial' else 1))%2**32
        if type(row['seed']) is not int or row['seed']!=expected_seed or expected_seed==2**32-1:
            raise ValueError('wrong deterministic seed')
        n=public[i]['data']['n']
        started=time.perf_counter()
        if patch_phase:
            base=initial[i]['raw_response']
            if messages[2]!={'role':'assistant','content':base} or messages[3]['role']!='user':
                raise ValueError('patch history does not echo the exact initial raw response')
            if row.get('initial_response_sha256')!=hashlib.sha256(base.encode()).hexdigest():
                raise ValueError('patch initial response hash mismatch')
            if expected_phase=='self' and messages[3]['content']!=SELF_INSTRUCTION:
                raise ValueError('self patch received non-generic feedback')
            if expected_phase=='guided':
                trace_from_message(row,n)
            parsed=parse_patch(row['raw_response'],n,base)
        else:
            parsed=parse_model(row['raw_response'],n)
        if replay_times is not None:
            replay_times[i]=time.perf_counter()-started
        if parsed != row['parsed']:
            raise ValueError('saved parse differs')
    return result


def dataset(cases_path, gold_path):
    cases = json.loads(cases_path.read_text())
    public = {r['id']:r for r in cases}
    label_rows=json.loads(gold_path.read_text())
    labels = {r['id']:r for r in label_rows}
    if len(public) != len(cases) or len(labels) != len(label_rows) or not set(public) <= set(labels):
        raise ValueError('public/label ID mismatch')
    for case in cases:
        data = case['data']; spec = labels[case['id']]['constraints']; n=data['n']
        if type(n) is not int or not 1 <= n <= 8:
            raise ValueError('domain cap')
        if set(data) != {'n','weights','costs','edges'} or any(len(data[k]) != n for k in ('weights','costs')):
            raise ValueError('data shape')
        if any(type(x) is not int or not 0 < x <= 10000 for k in ('weights','costs') for x in data[k]):
            raise ValueError('data coefficient domain')
        if set(spec) != {'budget','min_count','max_count','required','forbidden','implications'}:
            raise ValueError('reference schema')
        for k in ('budget','min_count','max_count'):
            if spec[k] is not None and (type(spec[k]) is not int or spec[k] < 0):
                raise ValueError('invalid reference bound')
        for pair in data['edges'] + spec['implications']:
            if len(pair) != 2 or any(type(x) is not int or not 0 <= x < n for x in pair):
                raise ValueError('invalid reference pair')
        for k in ('required','forbidden'):
            if any(type(x) is not int or not 0 <= x < n for x in spec[k]):
                raise ValueError('invalid reference index')
        families=[f for f,k in [('B','budget'),('L','min_count'),('U','max_count')] if spec[k] is not None]
        families += [f for f,k in [('M','required'),('F','forbidden'),('I','implications')] if spec[k]]
        if 'families' in labels[case['id']] and set(labels[case['id']]['families']) != set(families):
            raise ValueError('family metadata disagrees with reference')
        labels[case['id']]['families']=sorted(families)
    return cases,public,labels


def feedback(cases_path,gold_path,initial_path,output):
    cases,public,gold = dataset(cases_path,gold_path)
    initial = indexed(initial_path,public,'initial')
    output.mkdir(parents=True,exist_ok=True)
    if (output/'minimal.json').exists():
        raise ValueError('feedback already recorded')
    minimal={};reports=[]
    for case in cases:
        started=time.perf_counter()
        report=verify_model(case['data'],gold[case['id']]['constraints'],initial[case['id']]['parsed'])
        message=build_feedback(report,initial[case['id']]['parsed'],case['data']['n'])
        validate_feedback(message,case['data']['n'])
        minimal[case['id']]=message
        reports.append({'id':case['id'],'verification':report,'feedback_wall_seconds':time.perf_counter()-started})
    (output/'minimal.json').write_text(json.dumps(minimal,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    (output/'reports.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n' for r in reports))
    print(json.dumps({'feedback_cases':len(cases),'faithful_initial':sum(r['verification']['faithful'] for r in reports),
                      'schema_errors':sum(r['verification']['stage']=='schema' for r in reports)}))


def choose_direct(first,second):
    options=[first,second]
    index=max(range(2),key=lambda i:(int(options[i]['parsed']['valid']),
                                   options[i]['mean_generated_log_probability'],-i))
    return options[index],index


def choose_revision(first,second):
    if second['parsed']['valid']:
        return second,1
    return (first,0) if first['parsed']['valid'] else (second,1)


def count_template():
    return {'observed':0,'schema_valid':0,'faithful':0,'optimization_equivalent':0,
            'feasibility_mismatches':0,'objective_mismatches':0,'assignments_compared':0,
            'portfolio_concordant':0,'usable_for_original_problem':0,
            'format_repairs_to_faithful':0,'mathematical_repairs_to_faithful':0,
            'regressions_from_faithful':0,'initial_errors':0,'repairs_to_faithful':0}


def score(cases_path,gold_path,initial_path,direct_path,self_path,guided_path,output,feedback_reports=None):
    from .repair_solvers import portfolio
    cases,public,gold=dataset(cases_path,gold_path)
    initial=indexed(initial_path,public,'initial')
    paths={'direct':direct_path,'self':self_path,'guided':guided_path}
    if any(path is None for path in paths.values()) and not all(path is None for path in paths.values()):
        raise ValueError('all three second phases or development initial-only')
    replay_times={}
    phases={k:indexed(p,public,k,initial=initial,replay_times=replay_times.setdefault(k,{}))
            for k,p in paths.items() if p is not None}
    output.mkdir(parents=True,exist_ok=True)
    if (output/'raw.jsonl').exists():
        raise ValueError('scores already exist')
    totals={};strata={};records=[]
    for case in cases:
        i=case['id'];data=case['data'];spec=gold[i]['constraints'];first=initial[i]
        initial_report=verify_model(data,spec,first['parsed'])
        choices={'initial':(first,0)}
        if phases:
            if phases['direct'][i]['messages']!=first['messages']:
                raise ValueError('direct must use the same independent full-model prompt as initial')
            if phases['self'][i]['messages'][0]!=phases['guided'][i]['messages'][0]:
                raise ValueError('self and guided patches must share their patch system instruction')
            expected_feedback=build_feedback(initial_report,first['parsed'],data['n'])
            if trace_from_message(phases['guided'][i],data['n'])!=expected_feedback:
                raise ValueError('guided tool trace differs from the exact initial verification/candidate rows')
            choices['direct']=choose_direct(first,phases['direct'][i])
            choices['self']=choose_revision(first,phases['self'][i])
            choices['guided']=choose_revision(first,phases['guided'][i])
        results={}
        for name,(selected,choice) in choices.items():
            parsed=selected['parsed']; report=verify_model(data,spec,parsed)
            diagnosis=optimization_diagnostics(data,spec,parsed)
            solved=portfolio(parsed['model']) if parsed['valid'] else None
            usable=report['faithful'] and solved is not None and solved['concordance']
            result={'selected_candidate_index':choice,'selected_phase':selected['phase'],
                    'model':parsed.get('model'),'verification':report,'optimization_diagnostics':diagnosis,
                    'portfolio':solved,'usable_for_original_problem':usable}
            if phases and name in ('self','guided'):
                attempted=phases[name][i]
                patch=attempted['parsed']
                result.update(raw_patch=attempted['raw_response'],
                              authored_patch=patch.get('authored_patch'),
                              diagnosis=patch.get('diagnosis'),
                              diagnosis_scope='unverified text; never a semantic edit',
                              patch_valid=patch['valid'],
                              patch_materialized_authored_model=patch.get('authored_model'),
                              patch_materialized_dense_model=patch.get('model'),
                              initial_raw_sha256=patch.get('initial_raw_sha256'),
                              patch_replay_wall_seconds=replay_times[name][i])
            for axis,value in [('all','all'),('language',case['language']),
                               ('reference_feasibility','infeasible' if initial_report.get('reference_feasible_count')==0 else 'feasible')]:
                # Reference feasibility must also be known when initial schema fails.
                if axis=='reference_feasibility' and initial_report['stage']=='schema':
                    from itertools import product
                    from .repair_model import reference_feasible
                    value='feasible' if any(reference_feasible(data,spec,x) for x in product((0,1),repeat=data['n'])) else 'infeasible'
                bucket=totals if axis=='all' else strata.setdefault(axis,{}).setdefault(value,{})
                c=bucket.setdefault(name,count_template())
                c['observed']+=1;c['schema_valid']+=int(parsed['valid']);c['faithful']+=int(report['faithful'])
                c['optimization_equivalent']+=int(diagnosis['finite_optimization_equivalent'])
                c['feasibility_mismatches']+=report['feasibility_mismatches'] or 0
                c['objective_mismatches']+=report['objective_mismatches'] or 0
                c['assignments_compared']+=report['assignments']
                c['portfolio_concordant']+=int(solved is not None and solved['concordance'])
                c['usable_for_original_problem']+=int(usable)
                if name!='initial':
                    c['initial_errors']+=int(not initial_report['faithful'])
                    repaired=not initial_report['faithful'] and report['faithful']
                    c['repairs_to_faithful']+=int(repaired)
                    c['format_repairs_to_faithful']+=int(repaired and not first['parsed']['valid'])
                    c['mathematical_repairs_to_faithful']+=int(repaired and first['parsed']['valid'])
                    c['regressions_from_faithful']+=int(initial_report['faithful'] and not report['faithful'])
            results[name]=result
        records.append({'id':i,'language':case['language'],'families':gold[i]['families'],
                        'initial_feedback':build_feedback(initial_report,first['parsed'],data['n']),'results':results})
    with (output/'raw.jsonl').open('x') as handle:
        for r in records:handle.write(json.dumps(r,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n')
    physical=[*initial.values()]+[r for mapping in phases.values() for r in mapping.values()]
    fields=('input_tokens','output_tokens','wall_seconds','cpu_seconds')
    attributable={name:{k:sum(initial[i][k]+mapping[i][k] for i in public) for k in fields} for name,mapping in phases.items()}
    h={'status':'development_only'}
    if phases:
        gain=totals['guided']['faithful']-totals['self']['faithful']
        h={'status':'supported_in_finite_test' if gain>=3 and totals['guided']['regressions_from_faithful']<=1 else 'not_supported_in_finite_test',
           'guided_minus_self_faithful':gain,'required_gain':3,'guided_regressions':totals['guided']['regressions_from_faithful'],
           'maximum_regressions':1}
    sources={'initial':initial_path,**{k:p for k,p in paths.items() if p is not None}}
    executions={}
    for name,path in sources.items():
        meta_path=path.parent/'generation.json';manifest_path=path.parent/'manifest.json'
        if not manifest_path.exists() and path.parent.name=='driver':
            manifest_path=path.parent.parent/'manifest.json'
        meta=json.loads(meta_path.read_text()) if meta_path.exists() else {}
        manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
        executions[name]={'load_seconds':meta.get('load_seconds'),'process_wall_seconds':meta.get('wall_seconds'),
                          'wrapper_wall_seconds':manifest.get('run',{}).get('runtime_seconds'),
                          'client_cpu_seconds':meta.get('client_cpu_seconds'),
                          'server_cpu_seconds':meta.get('server_cpu_seconds'),
                          'server_cpu_scope':meta.get('server_cpu_scope'),
                          'aggregate_of':meta.get('aggregate_of')}
    feedback_seconds=sum(r['feedback_wall_seconds'] for r in rows(feedback_reports)) if feedback_reports else None
    portfolio_seconds=sum(v['portfolio']['total_portfolio_seconds'] for r in records for v in r['results'].values() if v['portfolio'] is not None)
    metrics={'cases':len(cases),'methods':totals,'strata':strata,'H23':h,
             'physical_generation_calls':len(physical),'physical_generation_cost':{k:sum(r[k] for r in physical) for k in fields},
             'attributable_cost_per_arm':attributable,
             'generation_executions':executions,'feedback_computation_seconds':feedback_seconds,
             'scored_portfolio_seconds_total':portfolio_seconds,
             'patch_replay_wall_seconds':{name:sum(values.values()) for name,values in replay_times.items() if name in ('self','guided')},
             'attempted_valid_patches':{name:sum(row['parsed']['valid'] for row in phases[name].values()) for name in ('self','guided')} if phases else {},
             'planned_call_accounting':{'physical':4*len(cases),'attributable_across_three_arms':6*len(cases)} if phases else None,
             'cost_scope':'row wall times include server request/postprocessing, not imports/load; row CPU is Python HTTP client only; server CPU is phase-level separately; process/wrapper timings reported; GPU energy and annotation/development/session cost unknown',
             'budget':'two calls and max2048 outputtokens per arm/case; shared initial counted once physically',
             'selection':{'direct':'schema validity then mean processed-token logprob, tie first','self_guided':'second if schema-valid, else initial if schema-valid'},
              'primary_comparison':'guided_tool_patch versus self_patch',
             'response_formats':{'initial_direct':'complete authored binary ILP','self_guided':'diagnosis plus literal edits applied to exact initial raw response'},
             'scope':'finite annotated reference, no population CI; patch materialization is literal and atomic; direct full generation is secondary; portfolio is ex-post profiling' }
    (output/'metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'cases':len(cases),'methods':totals,'H23':h},ensure_ascii=False))


def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('feedback','score'))
    p.add_argument('--cases',type=Path,required=True);p.add_argument('--gold',type=Path,required=True)
    p.add_argument('--initial',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--direct',type=Path);p.add_argument('--self',dest='self_path',type=Path)
    p.add_argument('--guided',type=Path)
    p.add_argument('--feedback-reports',type=Path)
    a=p.parse_args()
    if a.mode=='feedback':feedback(a.cases,a.gold,a.initial,a.output)
    else:score(a.cases,a.gold,a.initial,a.direct,a.self_path,a.guided,a.output,a.feedback_reports)


if __name__=='__main__':
    main()
