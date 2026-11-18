"""Offline evaluation of immutable recorded proposals against separate labels.

Missing responses have no performance score. This module never generates model
outputs and never exposes gold annotations to agent_pipeline.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
from .agent_pipeline import process_proposal
from .core import pipeline
from .transferstudy import keyword_pipeline
from .contracts import verify_external


def load_json(path):
    return json.loads(path.read_text(),parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON '+x)))


def index_rows(rows, ids, label):
    if type(rows) is not list:
        raise ValueError(label+' must be a JSON list')
    index={}
    for row in rows:
        if type(row) is not dict or type(row.get('id')) is not str or row['id'] in index:
            raise ValueError(label+' duplicate or absent id')
        index[row['id']]=row
    if set(index)!=set(ids):
        raise ValueError(label+' IDs differ from assigned public cases')
    return index


def run(public_path, gold_path, arms_path, output):
    public=load_json(public_path)
    ids=[r['id'] for r in public]
    if len(set(ids))!=len(ids):raise ValueError('duplicate public IDs')
    gold=index_rows(load_json(gold_path),ids,'gold')
    arms=load_json(arms_path)
    output.mkdir(parents=True,exist_ok=True)
    methods={'strict':lambda c:pipeline(c['request']),'keywords':lambda c:keyword_pipeline(c['request'])}
    availability={}
    for arm in arms:
        name=arm['name'];paths=[Path(p) for p in arm['files']]
        if not paths or any(not p.is_file() for p in paths):
            availability[name]={'status':'not_evaluated','reason':arm.get('reason','recorded proposal files unavailable'),'cases':0}
            continue
        rows=[]
        for path in paths:rows.extend(load_json(path))
        proposals=index_rows(rows,ids,name)
        availability[name]={'status':'observed_trace','cases':len(rows),
            'source_files':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
            'provenance':arm.get('provenance',{})}
        for numerical in (False,True):
            key=name+('_verified' if numerical else '_schema')
            methods[key]=(lambda c, p=proposals, numeric=numerical:process_proposal(c['request'],p[c['id']],numerical=numeric))
    metrics={name:{'supported':0,'unsupported':0,'accepted_supported':0,'false_accept':0,
                   'false_abstention':0,'correct_abstention':0,'accepted_numeric_invalid':0,
                   'per_family':{}} for name in methods}
    started=time.perf_counter()
    with (output/'raw.jsonl').open('w') as raw:
        for case in public:
            label=gold[case['id']]
            if label['expected_action'] not in ('propose','abstain'):raise ValueError('invalid gold action')
            supported=label['expected_action']=='propose';results={}
            for name,method in methods.items():
                result=method(case)
                accepted=result['status'] in ('accepted','solved')
                group=metrics[name]
                family=group['per_family'].setdefault(label['family'],{'cases':0,'supported':0,'accepted_supported':0,'false_accept':0,'false_abstention':0})
                group['supported' if supported else 'unsupported']+=1
                metric=('accepted_supported' if supported else 'false_accept') if accepted else ('false_abstention' if supported else 'correct_abstention')
                group[metric]+=1;family['cases']+=1;family['supported']+=int(supported)
                if metric in family:family[metric]+=1
                numeric=None
                if accepted:
                    numeric=verify_external(result['problem'],result['formulation'])
                    group['accepted_numeric_invalid']+=int(not numeric['valid'])
                results[name]={'result':result,'offline_numeric_assessment':numeric}
            raw.write(json.dumps({'case':case,'gold':label,'results':results},sort_keys=True,allow_nan=False)+'\n')
    for value in metrics.values():
        accepted=value['accepted_supported']+value['false_accept']
        value['coverage']=value['accepted_supported']/value['supported'] if value['supported'] else None
        value['semantic_risk_among_accepts']=value['false_accept']/accepted if accepted else None
    data={'cases':len(public),'methods':metrics,'agent_arms':availability,
          'agent_cases_evaluated':sum(x['cases'] for x in availability.values()),
          'native_comparison_status':'complete' if availability and all(x['status']=='observed_trace' for x in availability.values()) else 'blocked',
          'elapsed_seconds':time.perf_counter()-started,
          'limits':['Descriptive finite corpus; labels separate from execution','Recorded traces are not automatically blind prospective tests','No model calls performed by scorer']}
    (output/'metrics.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--public',type=Path,required=True)
    parser.add_argument('--gold',type=Path,required=True)
    parser.add_argument('--arms',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run(args.public,args.gold,args.arms,args.output)
