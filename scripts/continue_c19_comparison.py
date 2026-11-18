"""One bounded infrastructure continuation; never resample an attempted case."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import threading
import time

ROOT=Path(__file__).resolve().parents[1]
RUN=Path('runs/20261115-c19-instruct-repair')
RUNNER='/Users/karimelhoudaigui/.codex/plugins/cache/openai-curated-remote/mathbox/4.0.0/skills/computation-audit/scripts/run_experiment.py'
START=time.monotonic()
STOP=threading.Event()

def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def rows(p):return [json.loads(x) for x in p.read_text().splitlines()]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
 return h.hexdigest()

def tidy():
 """Closed old Git temporary garbage only; refs/valid packs are untouched."""
 count=subprocess.run(['git','count-objects','-vH'],capture_output=True,text=True,check=True,timeout=10)
 candidates=[]
 for name in set(re.findall(r'garbage found: (\.git/objects/pack/tmp_pack_[A-Za-z0-9]+)',count.stderr)):
  p=ROOT/name
  if not p.exists() or p.is_symlink():continue
  s=p.stat()
  if p.is_file() and time.time()-s.st_mtime>=120:candidates.append((s.st_size,p,s))
 candidates=sorted(candidates,reverse=True)[:20]
 before=subprocess.check_output(['git','for-each-ref','--format=%(refname) %(objectname)'],timeout=10)
 removed=[]
 for size,p,s in candidates:
  if STOP.is_set():break
  check=subprocess.run(['lsof','-F','n',str(p)],capture_output=True,text=True,timeout=5)
  if check.returncode!=1 or check.stdout or check.stderr:continue
  t=p.stat()
  if (s.st_ino,s.st_mtime_ns,s.st_size)!=(t.st_ino,t.st_mtime_ns,t.st_size):continue
  p.unlink();removed.append({'path':str(p.relative_to(ROOT)),'bytes':size,'inode':s.st_ino,'mtime_ns':s.st_mtime_ns})
 after=subprocess.check_output(['git','for-each-ref','--format=%(refname) %(objectname)'],timeout=10)
 assert before==after
 with (RUN/'resource-cleanup.jsonl').open('a') as f:f.write(json.dumps({'monotonic_elapsed_seconds':time.monotonic()-START,'removed':removed,'refs_identical':True})+'\n')

def maintain():
 while not STOP.wait(45) and time.monotonic()-START<1700:
  try:tidy()
  except Exception as e:
   with (RUN/'resource-cleanup.jsonl').open('a') as f:f.write(json.dumps({'cleanup_error':type(e).__name__+': '+str(e)})+'\n')

def bounded(name,art,command,results):
 out=RUN/name;cp=RUN/('contract-'+name+'.json')
 assert not out.exists() and not cp.exists()
 art=list(dict.fromkeys(['scripts/continue_c19_comparison.py',str(RUN/'freeze-test-v2.json'),str(RUN/'self-resource-reconciliation.json')]+art))
 c={'claim_id':'C19-FROZEN-CONTINUATION','mathematics':{'assertion_tested':name+'; unchanged frozen inferencer/scorer, only never-attempted cases continued','coefficient_domain':'binary integer ILP, Q4_K_M LLM, float64HiGHS','conventions':'same512/4096/T0.7p0.8k20 per-IDseeds; no resampling or imputation; trusted annotated reference','inputs':art,'bounds':{'parent_total_seconds':1800,'phase_seconds':1650,'call_seconds':180,'n':[4,7]},'non_claims':['No latency-isolation claim; bounded resource cleanup runs concurrently','No population/general-semantic guarantee','No QPU/external inference/spending']},'execution_artifacts':art,'software':[{'name':'Python','version':'3.9.6'},{'name':'llama.cpp','version':'b12359'},{'name':'SciPy','version':'1.13.1'}],'randomness':{'used':'inference' in name,'generator':'same frozen per-ID seed' if 'inference' in name else None,'seed':1 if 'inference' in name else None}}
 dump(cp,c)
 cmd=[sys.executable,RUNNER,'--root',str(ROOT),'--contract',str(cp),'--output',str(out),'--timeout',str(max(1,int(1800-(time.monotonic()-START)))),'--max-threads','4']
 for a in art:cmd+=['--input',a]
 for result in results:cmd+=['--result',str(out/result)]
 subprocess.run(cmd+['--']+command,check=True,cwd=ROOT)


def main():
 freeze=json.loads((RUN/'freeze-test-v2.json').read_text())
 for p,h in freeze['sha256'].items():assert sha(Path(p))==h,p
 cases=json.loads((RUN/'test_cases.json').read_text());public={x['id']:x for x in cases}
 old=RUN/'test-self-v2/driver';completed=rows(old/'raw.jsonl')
 requests=list((old/'http').glob('[0-9][0-9][0-9].request.json'));responses=list((old/'http').glob('[0-9][0-9][0-9].response.json'))
 assert len(completed)==len(requests)==len(responses)==13
 ids={r['id'] for r in completed};remaining=[x for x in cases if x['id'] not in ids]
 assert len(ids)==13 and len(remaining)==7
 dump(RUN/'self_remaining_cases.json',remaining)
 dump(RUN/'self-resource-reconciliation.json',{'completed_self_calls':13,'completion_http_requests':13,'completion_http_responses':13,'next_call_not_attempted':True,'never_attempted_ids':sorted(x['id'] for x in remaining),'old_manifest':str(RUN/'test-self-v2/manifest.json'),'old_manifest_sha256':sha(RUN/'test-self-v2/manifest.json'),'no_model_inputs_changed':True,'resource_management':'bounded1800s background cleanup of old>=120s closed tmp_pack Git garbage, max20files/45s; refs and validobjects preserved; concurrent host load, not a latencybenchmark'})
 tidy();worker=threading.Thread(target=maintain,daemon=True);worker.start()
 try:
  acquisition=json.loads((RUN/'acquisition.json').read_text());rt=Path('research/external/c16-public/runtime')
  model='research/external/c19-public/models/Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf'
  common=['quantage/repair_llama_linear.py','quantage/repair_model.py','quantage/repair_language.py','quantage/repair_feedback.py',str(RUN/'instructions.frozen.txt'),str(RUN/'acquisition.json'),model]+[str(rt/x['path']) for x in acquisition['runtime_extraction']['files']]
  out=RUN/'test-self-remaining-inference-v2'
  cmd=[sys.executable,'-m','quantage.repair_llama_linear','--cases',str(RUN/'self_remaining_cases.json'),'--instructions',str(RUN/'instructions.frozen.txt'),'--phase','self','--initial',str(RUN/'test-initial-v2/driver/raw.jsonl'),'--output',str(out/'driver'),'--server-binary',str(rt/'llama-b12359/llama-server'),'--model',model,'--acquisition',str(RUN/'acquisition.json'),'--execute']
  bounded(out.name,common+[str(RUN/'self_remaining_cases.json'),str(RUN/'test-initial-v2/driver/raw.jsonl')],cmd,['driver/raw.jsonl','driver/generation.json'])
  new=out/'driver';allrows=completed+rows(new/'raw.jsonl');assert len(allrows)==20 and {x['id'] for x in allrows}==set(public)
  union=RUN/'test-self-union-v2/driver';union.mkdir(parents=True)
  (union/'raw.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n' for x in allrows))
  metas=[json.loads((p/'generation.json').read_text()) for p in [old,new]]
  meta={'status':'completed','planned':20,'completed':20,'phase':'self','aggregate_of':[str(old),str(new)],'scope':'actual13+7responses, no retry; two serverloads and interrupted infrastructure phase retained; wallCPU includes original unsuccessful process'}
  for k in ['input_tokens','output_tokens','wall_seconds','cpu_seconds','load_seconds','client_cpu_seconds','server_cpu_seconds']:meta[k]=sum(x[k] for x in metas)
  dump(union/'generation.json',meta)
  subprocess.run([sys.executable,'scripts/run_c19_phase_v2.py','guided','--split','test'],check=True)
  art=['quantage/repair_study_c19.py','quantage/repair_model.py','quantage/repair_language.py','quantage/repair_feedback.py','quantage/repair_solvers.py',str(RUN/'test_cases.json'),str(RUN/'gold.json'),str(RUN/'test-feedback-v2/reports.jsonl')]
  cmd=[sys.executable,'-m','quantage.repair_study_c19','score','--cases',str(RUN/'test_cases.json'),'--gold',str(RUN/'gold.json'),'--output',str(RUN/'test-score-v2'),'--feedback-reports',str(RUN/'test-feedback-v2/reports.jsonl')]
  for phase in ['initial','direct','self','guided']:
   trace=union/'raw.jsonl' if phase=='self' else RUN/('test-'+phase+'-v2/driver/raw.jsonl');art+=[str(trace),str(trace.with_name('generation.json'))];cmd+=['--'+phase,str(trace)]
  bounded('test-score-v2',art,cmd,['raw.jsonl','metrics.json'])
 finally:
  STOP.set();worker.join(timeout=10)

if __name__=='__main__':main()
