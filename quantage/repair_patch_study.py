"""C20 development-only scoring, explicitly replaying literal authored edits."""
import argparse,hashlib,json,math,time
from pathlib import Path
from .repair_model import verify_model
from .repair_language import parse_proposal
from .repair_patch_language import parse_patch
from .repair_feedback import feedback_for_model
from .repair_solvers import portfolio

def read(p):return json.loads(p.read_text())
def rows(p):return [json.loads(x) for x in p.read_text().splitlines()]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 r=Path('runs/20261115-c20-grounded-edits');old=Path('runs/20261115-c19-instruct-repair')
 cases=read(r/'probe_cases.json');public={x['id']:x for x in cases}
 gold={x['id']:x for x in read(old/'gold.json')}
 initial_rows=rows(old/'test-initial-v2/driver/raw.jsonl');initial={x['id']:x for x in initial_rows}
 new=rows(r/'probe-guided-v1/driver/raw.jsonl');assert len(new)==len(cases)==2 and {x['id'] for x in new}==set(public)
 assert len(initial)==len(initial_rows) and len({x['id'] for x in new})==2
 system=(r/'instructions.txt').read_text();records=[]
 for row in new:
  case=public[row['id']];first=initial[row['id']];n=case['data']['n'];spec=gold[row['id']]['constraints']
  assert row['phase']=='guided' and row['seed']==(int(hashlib.sha256(row['id'].encode()).hexdigest()[:8],16)+1)%2**32
  assert row['messages'][0]=={'role':'system','content':system}
  assert json.loads(row['messages'][1]['content'])=={'intention':case['intention'],'data':case['data']}
  assert row['messages'][2]=={'role':'assistant','content':first['raw_response']}
  assert len(row['generated_token_ids'])==len(row['generated_token_log_probabilities'])==row['output_tokens']<=512
  assert type(row['input_tokens']) is int and 0<row['input_tokens']<=3583
  assert all(type(x) in (int,float) and math.isfinite(x) for x in row['generated_token_log_probabilities'])
  assert math.isfinite(row['mean_generated_log_probability']) and abs(sum(row['generated_token_log_probabilities'])/row['output_tokens']-row['mean_generated_log_probability'])<1e-12
  started=time.perf_counter();parsed=parse_patch(row['raw_response'],n,first['raw_response']);materialization=time.perf_counter()-started
  assert parsed==row['parsed']
  started=time.perf_counter();before=verify_model(case['data'],spec,parse_proposal(first['raw_response'],n));after=verify_model(case['data'],spec,parsed);verification=time.perf_counter()-started
  assert json.loads(row['messages'][3]['content'])['verifier_feedback']==feedback_for_model(before,n)
  solved=portfolio(parsed['model']) if parsed['valid'] else None
  cost={k:first[k]+row[k] for k in ['input_tokens','output_tokens','wall_seconds','cpu_seconds']}
  records.append({'id':row['id'],'diagnosis':parsed.get('diagnosis'),'authored_patch':parsed.get('authored_patch'),'patch_valid':parsed['valid'],'materialized_authored_model':parsed.get('authored_model'),'before':before,'after':after,'residual_feedback':feedback_for_model(after,n),'portfolio':solved,'usable_for_original':bool(after['faithful'] and solved and solved['concordance']),'materialization_wall_seconds':materialization,'verification_wall_seconds':verification,'attributable_initial_plus_revision_cost':cost})
 a.output.mkdir(parents=True,exist_ok=True)
 assert not (a.output/'raw.jsonl').exists()
 (a.output/'raw.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n' for x in records))
 metadata=read(r/'probe-guided-v1/driver/generation.json')
 metrics={'development_only':True,'cases':2,'new_physical_model_calls':2,'historical_initial_calls_reused':2,'logical_calls_attributable':4,'valid_patches':sum(x['patch_valid'] for x in records),'faithful_initial':sum(x['before']['faithful'] for x in records),'faithful_after_patch':sum(x['after']['faithful'] for x in records),'usable_for_original':sum(x['usable_for_original'] for x in records),'new_generation_cost':{k:sum(x[k] for x in new) for k in ['input_tokens','output_tokens','wall_seconds','cpu_seconds']},'attributable_cost':{k:sum(x['attributable_initial_plus_revision_cost'][k] for x in records) for k in ['input_tokens','output_tokens','wall_seconds','cpu_seconds']},'generation_load_seconds':metadata['load_seconds'],'generation_process_wall_seconds':metadata['wall_seconds'],'server_cpu_seconds':metadata['server_cpu_seconds'],'resource_management':read(r/'resource-management.json'),'materialization_wall_seconds':sum(x['materialization_wall_seconds'] for x in records),'verification_wall_seconds':sum(x['verification_wall_seconds'] for x in records),'portfolio_seconds':sum(x['portfolio']['total_portfolio_seconds'] for x in records if x['portfolio']),'scope':'two posthoc selected previous errors, no heldout/causal/novelty inference; diagnostic unverified; same token caps but new format/prompt; initial costs reused not free; energy and full session unknown'}
 (a.output/'metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2,allow_nan=False)+'\n');print(json.dumps(metrics,ensure_ascii=False))

if __name__=='__main__':main()
