"""Build candidate-only traces; trusted reference contributes minimal verdict only."""
import json
from pathlib import Path
from quantage.repair_model import verify_model
from quantage.repair_language import parse_proposal
from quantage.repair_trace_feedback import build_feedback
r=Path('runs/20261115-c21-tool-grounded-edits');old=Path('runs/20261115-c19-instruct-repair')
cases=json.loads((r/'probe_cases.json').read_text());gold={x['id']:x for x in json.loads((old/'gold.json').read_text())};initial={x['id']:x for x in [json.loads(s) for s in (old/'test-initial-v2/driver/raw.jsonl').read_text().splitlines()]};payload={}
for c in cases:
 p=parse_proposal(initial[c['id']]['raw_response'],c['data']['n']);report=verify_model(c['data'],gold[c['id']]['constraints'],p);payload[c['id']]=build_feedback(report,p,c['data']['n'])
text=json.dumps(payload,indent=2)+'\n';path=r/'feedback.json'
if path.exists():assert path.read_text()==text,'refuse overwrite different existing trace'
else:path.write_text(text)
print('two candidate-only traces reproduced exactly')
