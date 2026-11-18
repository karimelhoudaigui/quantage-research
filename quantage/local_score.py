"""Score completed local-model records only; no generation and no imputations."""
import argparse
import json
from pathlib import Path
from .compact_agent import parse_compact,execute_compact
from .core import pipeline
from .transferstudy import keyword_pipeline


def new_counts():
    return {'observed':0,'supported_observed':0,'unsupported_observed':0,'accepted_supported':0,
            'false_accept':0,'false_abstention':0,'correct_abstention':0,'format_invalid':0,
            'model_abstentions':0,'model_proposes':0,'model_proposes_outside_contract':0,
            'controller_refusals':0,'blocked_wrong_proposals':0,'semantic_errors_with_numeric_certificate':0,
            'input_tokens':0,'output_tokens':0,'wall_seconds':0.,'cpu_seconds':0.}


def accumulate(counts,supported,accepted,raw=None,parsed=None,result=None):
    counts['observed']+=1;counts['supported_observed' if supported else 'unsupported_observed']+=1
    key=('accepted_supported' if supported else 'false_accept') if accepted else ('false_abstention' if supported else 'correct_abstention')
    counts[key]+=1
    if raw is not None:
        for field in ('input_tokens','output_tokens','wall_seconds','cpu_seconds'):counts[field]+=raw[field]
        if not parsed['valid']:counts['format_invalid']+=1
        else:
            proposed=parsed['proposal']['action']=='propose'
            counts['model_proposes' if proposed else 'model_abstentions']+=1
            counts['model_proposes_outside_contract']+=int(proposed and not supported)
            counts['blocked_wrong_proposals']+=int(proposed and not supported and not accepted)
        counts['controller_refusals']+=int(result['stage'] in ('format','data_contract','numeric'))
    if accepted and not supported and result and result.get('verification',{}).get('valid'):
        counts['semantic_errors_with_numeric_certificate']+=1


def ratios(c):
    c['coverage_on_observed_supported']=c['accepted_supported']/c['supported_observed'] if c['supported_observed'] else None
    n=c['accepted_supported']+c['false_accept']
    c['risk_among_accepts']=c['false_accept']/n if n else None
    return c


def score(cases_path,gold_path,responses_path,output):
    cases=json.loads(cases_path.read_text());gold={x['id']:x for x in json.loads(gold_path.read_text())}
    public={x['id']:x for x in cases}
    if len(public)!=len(cases) or set(public)!=set(gold):raise ValueError('cases/gold mismatch')
    responses=[json.loads(s) for s in responses_path.read_text().splitlines()]
    indexed={}
    for row in responses:
        key=(row['id'],row['arm'])
        if key in indexed or row['id'] not in public or row['arm'] not in ('alone','documented'):
            raise ValueError('duplicate or unknown observed response')
        indexed[key]=row
    output.mkdir(parents=True,exist_ok=True)
    if (output/'raw.jsonl').exists():raise ValueError('refuse to overwrite scoring')
    totals={k:new_counts() for k in ('strict','keywords','alone','documented')}
    families={k:{f:new_counts() for f in ('mis','photon')} for k in totals}
    decisions={};rows=[]
    for case in cases:
        label=gold[case['id']];supported=label['expected_action']=='propose';family=label['family']
        for name,fn in (('strict',pipeline),('keywords',keyword_pipeline)):
            result=fn(case['request']);accepted=result['status']=='solved'
            accumulate(totals[name],supported,accepted,result=result);accumulate(families[name][family],supported,accepted,result=result)
            rows.append({'id':case['id'],'method':name,'gold':label,'result':result})
        for arm in ('alone','documented'):
            raw=indexed.get((case['id'],arm))
            if raw is None:continue
            parsed=parse_compact(raw['raw_response'])
            if parsed!=raw['parsed']:raise ValueError('generation/scoring parser mismatch')
            result=execute_compact(case['request'],parsed);accepted=result['status']=='accepted'
            for target in (totals[arm],families[arm][family]):accumulate(target,supported,accepted,raw,parsed,result)
            decisions[(case['id'],arm)]=accepted
            rows.append({'id':case['id'],'method':arm,'gold':label,'parsed':parsed,'result':result,
                         'finish_reason':raw['finish_reason']})
    with (output/'raw.jsonl').open('x') as raw:
        for row in rows:raw.write(json.dumps(row,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n')
    pair_ids=[i for i in public if all((i,a) in decisions for a in ('alone','documented'))]
    pairs={'both_observed':len(pair_ids),'alone_only_correct_accept':0,'documented_only_correct_accept':0,
           'alone_only_false_accept':0,'documented_only_false_accept':0,'changed_acceptance_ids':[]}
    for i in pair_ids:
        a,b=decisions[(i,'alone')],decisions[(i,'documented')]
        if a!=b:
            pairs['changed_acceptance_ids'].append(i)
            name=('alone_only_' if a else 'documented_only_')+('correct_accept' if gold[i]['expected_action']=='propose' else 'false_accept')
            pairs[name]+=1
    result={'cases_selected':len(cases),'generation_records_observed':len(responses),
            'missing_generation_records':2*len(cases)-len(responses),
            'methods':{k:ratios(v) for k,v in totals.items()},
            'per_family':{k:{f:ratios(v) for f,v in byfamily.items()} for k,byfamily in families.items()},
            'paired':pairs,'interpretation':'Hybrid semantic LLM + deterministic formulation; finite descriptive paired pilot, not population inference.'}
    (output/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--cases',type=Path,required=True);parser.add_argument('--gold',type=Path,required=True)
    parser.add_argument('--responses',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args();score(a.cases,a.gold,a.responses,a.output)
