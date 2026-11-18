"""Run one real guided repair of a previously observed wrong dev formulation."""
import json
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[1];r=Path('runs/20261115-c19-instruct-repair');out=r/'development-loop-v1'
a=json.loads((r/'acquisition.json').read_text());runtime=Path('research/external/c16-public/runtime')
art=['scripts/run_c19_demo.py','quantage/repair_loop_linear.py','quantage/repair_llama_linear.py','quantage/repair_model.py','quantage/repair_language.py','quantage/repair_feedback.py','quantage/repair_solvers.py',str(r/'protocol-development-loop.md'),str(r/'dev_remaining_cases.json'),str(r/'instructions.v1.txt'),str(r/'acquisition.json'),str(r/'development-remaining-v1/driver/raw.jsonl'),'runs/20261115-c16-quantized-repair/gold.json','research/external/c19-public/models/Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf']+[str(runtime/x['path']) for x in a['runtime_extraction']['files']]
c={'claim_id':'C19-DEV-LOOP','mathematics':{'assertion_tested':'One real guided call for lexfirst valid-but-wrong among six known dev records; reused actual initial, no resampling','coefficient_domain':'exact binary integer ILP, Q4_K_M, HiGHS float64','conventions':'trusted annotated reference, finite cube, closed3CE, stop on faithful, two real solvers','inputs':[str(r/'dev_remaining_cases.json')],'bounds':{'selected_id':'b97cb5f56812','new_calls':1,'repairs':1,'completion_tokens':512,'context':4096,'global_seconds':1800},'non_claims':['Not heldout performance','No automatic reference/formulation completion','No independent final review of new controller','No QPU/spending']},'execution_artifacts':art,'software':[{'name':'Python','version':'3.9.6'},{'name':'llama.cpp','version':'b12359'},{'name':'SciPy','version':'1.13.1'}],'randomness':{'used':True,'generator':'same fixed SHAID+1','seed':1}}
p=r/'contract-development-loop-v1.json';assert not p.exists();p.write_text(json.dumps(c,indent=2)+'\n')
cmd=[sys.executable,'/Users/karimelhoudaigui/.codex/plugins/cache/openai-curated-remote/mathbox/4.0.0/skills/computation-audit/scripts/run_experiment.py','--root',str(root),'--contract',str(p),'--output',str(out),'--timeout','1800','--max-threads','4','--result',str(out/'loop/result.json')]
for x in art:cmd+=['--input',x]
cmd+=['--',sys.executable,'-m','quantage.repair_loop_linear','--cases',str(r/'dev_remaining_cases.json'),'--gold','runs/20261115-c16-quantized-repair/gold.json','--id','b97cb5f56812','--instructions',str(r/'instructions.v1.txt'),'--initial-records',str(r/'development-remaining-v1/driver/raw.jsonl'),'--output',str(out/'loop'),'--execute']
raise SystemExit(subprocess.call(cmd))
