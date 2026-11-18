"""Replay audit data as data. Never execute the artifact's replay_source."""
import argparse
import copy
import json
import math
from pathlib import Path
import time
from .core import formulate, pipeline, understand
from .verification import verify
from .contracts import verify_external


def decode(value):
    if isinstance(value, dict):
        if set(value) == {'$float'}:
            return {'nan':float('nan'),'inf':float('inf'),'-inf':-float('inf')}[value['$float']]
        return {k:decode(v) for k,v in value.items()}
    if isinstance(value, list):
        return [decode(v) for v in value]
    return value


def encode(value):
    if type(value) is float and not math.isfinite(value):
        return {'$float':'nan' if math.isnan(value) else ('inf' if value>0 else '-inf')}
    if isinstance(value, dict):return {k:encode(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)):return [encode(v) for v in value]
    return value


def run(audit_path, labels_path, output):
    cases=json.loads(audit_path.read_text())['cases']
    labels=json.loads(labels_path.read_text())
    if set(labels) != {c['id'] for c in cases}:raise ValueError('labels must cover every audit case')
    output.mkdir(parents=True,exist_ok=True)
    stats={'cases':len(cases),'proposal_cases':0,'pipeline_boundaries':0,
           'legacy':{'false_accept':0,'false_reject':0,'exceptions':0},
           'external':{'false_accept':0,'false_reject':0,'exceptions':0}}
    t0=time.perf_counter()
    with (output/'raw.jsonl').open('w') as raw:
        for original in cases:
            c=decode(original);row={'case':original,'expected_valid':labels[c['id']]}
            if c['mode']=='pipeline':
                row['pipeline']=encode(pipeline(c['request']))
                stats['pipeline_boundaries']+=1
                if row['pipeline']['status'] != 'abstain':raise AssertionError('unsafe historical input boundary')
            else:
                p=understand(c['request']);m=formulate(p)
                p.update(c.get('problem_updates',{}));m.update(c.get('model_updates',{}))
                row.update(problem=encode(p),proposal=encode(m))
                for name,fn in (('legacy',verify),('external',verify_external)):
                    try:
                        result=fn(copy.deepcopy(p),copy.deepcopy(m),c.get('tolerance',1e-12))
                        accepted=result['valid']
                    except Exception as exc:
                        result={'valid':False,'exception':type(exc).__name__+': '+str(exc)}
                        stats[name]['exceptions']+=1;accepted=False
                    stats[name]['false_accept']+=int(accepted and not labels[c['id']])
                    stats[name]['false_reject']+=int(not accepted and labels[c['id']])
                    row[name]=encode(result)
                stats['proposal_cases']+=1
            raw.write(json.dumps(row,sort_keys=True,allow_nan=False)+'\n')
    stats['elapsed_seconds']=time.perf_counter()-t0
    (output/'metrics.json').write_text(json.dumps(stats,indent=2)+'\n')
    print(json.dumps(stats))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--audit',type=Path,required=True)
    parser.add_argument('--labels',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run(args.audit,args.labels,args.output)
