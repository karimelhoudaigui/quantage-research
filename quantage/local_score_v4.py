"""Paired no-veto/veto scoring of the same real v2 local proposals."""
import argparse
import json
from pathlib import Path
from .compact_v2 import parse_v2
from .compact_v4 import execute_v4
from .core import pipeline
from .transferstudy import keyword_pipeline
from .local_score import new_counts,accumulate,ratios


def score(cases_path,gold_path,responses_path,output):
    cases=json.loads(cases_path.read_text());public={x['id']:x for x in cases}
    gold={x['id']:x for x in json.loads(gold_path.read_text())}
    records=[json.loads(s) for s in responses_path.read_text().splitlines()]
    observed={}
    for r in records:
        if r['id'] in observed or r['id'] not in public or r['arm']!='nonredundant':raise ValueError('wrong or duplicate response')
        observed[r['id']]=r
    if len(public)!=len(cases) or set(public)!=set(gold):raise ValueError('labels/public mismatch')
    output.mkdir(parents=True,exist_ok=True)
    if (output/'raw.jsonl').exists():raise ValueError('refuse to overwrite scored rows')
    totals={k:dict(new_counts(),semantic_vetoes=0) for k in ('strict','keywords','unprotected','guarded')}
    families={k:{f:dict(new_counts(),semantic_vetoes=0) for f in ('mis','photon')} for k in totals}
    pairs={'observed':len(observed),'vetoed_wrong_acceptance':0,'vetoed_supported_acceptance':0,'added_acceptance':0,'changed_ids':[]}
    with (output/'raw.jsonl').open('x') as raw:
        for c in cases:
            label=gold[c['id']];supported=label['expected_action']=='propose';family=label['family'];results={}
            for name,method in (('strict',pipeline),('keywords',keyword_pipeline)):
                result=method(c['request']);accepted=result['status']=='solved'
                for target in (totals[name],families[name][family]):accumulate(target,supported,accepted,result=result)
                results[name]=result
            r=observed.get(c['id'])
            if r:
                parsed=parse_v2(r['raw_response'])
                if parsed!=r['parsed']:raise ValueError('parser changed since generation')
                for name,guard in (('unprotected',False),('guarded',True)):
                    result=execute_v4(c['request'],parsed,guard);accepted=result['status']=='accepted'
                    for target in (totals[name],families[name][family]):
                        accumulate(target,supported,accepted,r,parsed,result)
                        target['semantic_vetoes']+=int(result['stage']=='semantic_veto')
                        target['controller_refusals']+=int(result['stage']=='semantic_veto')
                    results[name]=result
                a=results['unprotected']['status']=='accepted';b=results['guarded']['status']=='accepted'
                if a!=b:pairs['changed_ids'].append(c['id'])
                pairs['vetoed_wrong_acceptance']+=int(a and not b and not supported)
                pairs['vetoed_supported_acceptance']+=int(a and not b and supported)
                pairs['added_acceptance']+=int(not a and b)
            raw.write(json.dumps({'id':c['id'],'gold':label,'results':results},ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n')
    metrics={'cases_selected':len(cases),'generation_records_observed':len(records),'missing_generation_records':len(cases)-len(records),
             'methods':{k:ratios(v) for k,v in totals.items()},
             'per_family':{k:{f:ratios(v) for f,v in byfamily.items()} for k,byfamily in families.items()},
             'paired':pairs,'scope':'Post-hoc v4 development regression on observed C09 responses; never a new held-out test.'}
    (output/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cases',type=Path,required=True);p.add_argument('--gold',type=Path,required=True)
    p.add_argument('--responses',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();score(a.cases,a.gold,a.responses,a.output)
