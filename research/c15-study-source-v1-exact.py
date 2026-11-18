"""Minimal oracle feedback and offline comparison of real repair trajectories."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from .repair_model import parse_model, verify_model, model_feasible, objective_value
from .repair_feedback import feedback_for_model, optimization_diagnostics, validate_feedback


def rows(path):
    return [json.loads(s) for s in path.read_text().splitlines()]


def indexed(path, public):
    records = rows(path)
    result = {r['id']:r for r in records}
    if len(result) != len(records) or set(result) != set(public):
        raise ValueError('complete unique generation matrix required, no imputation')
    for i, row in result.items():
        if parse_model(row['raw_response'], public[i]['data']['n']) != row['parsed']:
            raise ValueError('saved parse differs')
    return result


def dataset(cases_path, gold_path):
    cases = json.loads(cases_path.read_text())
    public = {r['id']:r for r in cases}
    labels = {r['id']:r for r in json.loads(gold_path.read_text())}
    if len(public) != len(cases) or not set(public) <= set(labels):
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
    return cases,public,labels


def feedback(cases_path,gold_path,initial_path,output):
    cases,public,gold = dataset(cases_path,gold_path)
    initial = indexed(initial_path,public)
    output.mkdir(parents=True,exist_ok=True)
    if (output/'minimal.json').exists():
        raise ValueError('feedback already recorded')
    minimal={};reports=[]
    for case in cases:
        started=time.perf_counter()
        report=verify_model(case['data'],gold[case['id']]['constraints'],initial[case['id']]['parsed'])
        message=feedback_for_model(report,case['data']['n'])
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


def score(cases_path,gold_path,initial_path,direct_path,self_path,guided_path,output):
    from .repair_solvers import portfolio
    cases,public,gold=dataset(cases_path,gold_path)
    initial=indexed(initial_path,public)
    paths={'direct':direct_path,'self':self_path,'guided':guided_path}
    if any(path is None for path in paths.values()) and not all(path is None for path in paths.values()):
        raise ValueError('all three second phases or development initial-only')
    phases={k:indexed(p,public) for k,p in paths.items() if p is not None}
    output.mkdir(parents=True,exist_ok=True)
    if (output/'raw.jsonl').exists():
        raise ValueError('scores already exist')
    totals={};strata={};records=[]
    for case in cases:
        i=case['id'];data=case['data'];spec=gold[i]['constraints'];first=initial[i]
        initial_report=verify_model(data,spec,first['parsed'])
        choices={'initial':(first,0)}
        if phases:
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
                        'initial_feedback':feedback_for_model(initial_report,data['n']),'results':results})
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
    metrics={'cases':len(cases),'methods':totals,'strata':strata,'H15':h,
             'physical_generation_calls':len(physical),'physical_generation_cost':{k:sum(r[k] for r in physical) for k in fields},
             'attributable_cost_per_arm':attributable,
             'budget':'two calls and max768 outputtokens per arm/case; shared initial counted once physically',
             'selection':{'direct':'schema validity then mean processed-token logprob, tie first','self_guided':'second if schema-valid, else initial if schema-valid'},
             'scope':'finite annotated reference, no population CI, full explicit ILP emitted by LLM; portfolio is ex-post profiling'}
    (output/'metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'cases':len(cases),'methods':totals,'H15':h},ensure_ascii=False))


def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('feedback','score'))
    p.add_argument('--cases',type=Path,required=True);p.add_argument('--gold',type=Path,required=True)
    p.add_argument('--initial',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--direct',type=Path);p.add_argument('--self',dest='self_path',type=Path)
    p.add_argument('--guided',type=Path)
    a=p.parse_args()
    if a.mode=='feedback':feedback(a.cases,a.gold,a.initial,a.output)
    else:score(a.cases,a.gold,a.initial,a.direct,a.self_path,a.guided,a.output)


if __name__=='__main__':
    main()
