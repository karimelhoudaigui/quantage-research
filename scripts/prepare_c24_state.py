"""Compose only actual authored state; trusted reference contributes feedback only."""
import hashlib,json
from pathlib import Path
from quantage.repair_patch_tool_language import parse_patch
from quantage.repair_model import verify_model
from quantage.repair_trace_feedback import build_feedback
r=Path('runs/20261116-c24-second-repair');old=Path('runs/20261115-c19-instruct-repair');c22=Path('runs/20261115-c22-model-capacity')
cases=json.loads((c22/'remaining_cases.json').read_text());assert len(cases)==1;case=cases[0];i=case['id']
initial={x['id']:x for x in [json.loads(s) for s in (old/'test-initial-v2/driver/raw.jsonl').read_text().splitlines()]}[i]
patches=[json.loads(s) for s in (c22/'probe-remaining-v3/driver/raw.jsonl').read_text().splitlines()];assert len(patches)==1 and patches[0]['id']==i
previous=patches[0];parsed=parse_patch(previous['raw_response'],case['data']['n'],initial['raw_response']);assert parsed==previous['parsed'] and parsed['valid']
current=json.dumps(parsed['authored_model'],ensure_ascii=False,separators=(',',':'),sort_keys=True)
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
state={'id':i,'phase':'materialized_state','record_kind':'literal_recorded_edits','public_request':{'intention':case['intention'],'data':case['data']},'raw_response':current,'previous_patch_raw':previous['raw_response'],'state_instructions_sha256':sha((r/'instructions.txt').read_text()),'lineage':{'original_initial_raw_sha256':sha(initial['raw_response']),'previous_patch_raw_sha256':sha(previous['raw_response']),'original_file':str(old/'test-initial-v2/driver/raw.jsonl'),'previous_file':str(c22/'probe-remaining-v3/driver/raw.jsonl'),'current_state_sha256':sha(current),'new_initial_sampling':False}}
(r/'public_case.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n');(r/'states.json').write_text(json.dumps([state],ensure_ascii=False,indent=2)+'\n')
gold={x['id']:x for x in json.loads((old/'gold.json').read_text())};report=verify_model(case['data'],gold[i]['constraints'],parsed);feedback=build_feedback(report,parsed,case['data']['n'])
(r/'feedback.json').write_text(json.dumps({i:feedback},indent=2)+'\n');(r/'before-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'new_initial_calls':0,'current_state_faithful':report['faithful'],'remaining_disagreements':report['feasibility_mismatches'],'state_phase':state['phase']}))
