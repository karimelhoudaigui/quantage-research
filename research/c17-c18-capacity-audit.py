"""Read-only reconciliation of actual capacity probes; no new inference."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from quantage.repair_model import verify_model
from quantage.repair_language import parse_proposal
from quantage.repair_thinking_language import parse_proposal as parse_thinking

def read(p): return json.loads(Path(p).read_text())
def rows(p): return [json.loads(s) for s in Path(p).read_text().splitlines()]
run17=Path('runs/20261115-c17-capacity-repair')
run18=Path('runs/20261115-c18-thinking-repair')
cases={r['id']:r for r in read(run17/'probe_cases.json')}
gold={r['id']:r for r in read('runs/20261115-c16-quantized-repair/gold.json')}
c17=rows(run17/'capacity-probe-v2/driver/raw.jsonl')
c18=[read(run18/'recovered-first-response.json')]+rows(run18/'capacity-remaining-v1/driver/raw.jsonl')
assert len(c17)==len(c18)==len(cases)==2
out={}
for name,rs,parser,cap in [('C17',c17,parse_proposal,512),('C18',c18,parse_thinking,1024)]:
 assert {r['id'] for r in rs}==set(cases)
 values=[]
 for r in rs:
  n=cases[r['id']]['data']['n']; parsed=parser(r['raw_response'],n)
  assert parsed==r['parsed']
  assert len(r['generated_token_ids'])==len(r['generated_token_log_probabilities'])==r['output_tokens']<=cap
  report=verify_model(cases[r['id']]['data'],gold[r['id']]['constraints'],parsed)
  values.append({'id':r['id'],'output_tokens':r['output_tokens'],'finish_reason':r['finish_reason'],'schema_valid':parsed['valid'],'verification':report,'wall_seconds':r['wall_seconds'],'client_cpu_seconds':r['cpu_seconds']})
 out[name]={'cases':values,'faithful':sum(x['verification']['faithful'] for x in values),'schema_valid':sum(x['schema_valid'] for x in values),'new_model_calls':0}
assert out['C17']['faithful']==0 and out['C17']['schema_valid']==2
assert out['C18']['faithful']==out['C18']['schema_valid']==0
out['scope']='Integrator self-review on known development only; C18 first response recovered from original HTTP, wall/clientCPU unknown; no model comparison or test result.'
output=Path(sys.argv[1]);output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:{t:v[t] for t in ('faithful','schema_valid')} for k,v in out.items() if k in ('C17','C18')}))
