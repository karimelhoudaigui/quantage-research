"""Synthetic integration of selection, patches, fallback, regression and H23; no LLM."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from quantage import repair_study_c23 as study
from quantage.repair_language import parse_proposal
from quantage.repair_patch_tool_language import parse_patch
from quantage.repair_patch_scale_inference import SELF_INSTRUCTION,GUIDED_INSTRUCTION
from quantage.repair_feedback import SCHEMA_MESSAGE

root=Path(sys.argv[1]);root.mkdir(parents=True,exist_ok=True)
cases=[];gold=[];phase_rows={p:[] for p in ['initial','direct','self','guided']}
def model(objective=[3,5],constraints=['x0+x1<=1']):return {'formulation':'binary_ilp','variables':[0,1],'sense':'max','objective':objective[:],'constraints':constraints[:]}
def text(x):return json.dumps(x,sort_keys=True)
def patch(edits):return text({'diagnosis':'Synthetic fixture, no model call','edits':edits})
for index in range(5):
 identity='fixture-'+str(index);c={'id':identity,'language':'en','intention':'Synthetic budget and exclusion '+str(index),'data':{'n':2,'weights':[3,5],'costs':[1,2],'edges':[[0,1]]}};cases.append(c)
 gold.append({'id':identity,'constraints':{'budget':2,'min_count':None,'max_count':None,'required':[],'forbidden':[],'implications':[]},'families':['B']})
 first_raw=text(model(constraints=[])) if index==0 else '{' if index==2 else text(model(objective=[7,5])) if index==4 else text(model())
 direct_raw='{' if index==3 else text(model(objective=[3,99])) if index==1 else text(model())
 self_raw=patch([]) if index in [0,1,4] else '{' if index==2 else patch([{'op':'set_objective','values':[99,5]}])
 guided_raw=patch([{'op':'add_constraint','row':'1*x0+2*x1<=2'}]) if index==0 else patch([{'op':'set_objective','values':[99,5]}]) if index==1 else patch([{'op':'replace_model','model':model()}]) if index==2 else '{' if index==3 else patch([{'op':'set_objective','values':[3,5]}])
 base=[{'role':'system','content':'FULL_FIXTURE'},{'role':'user','content':json.dumps({'intention':c['intention'],'data':c['data']},ensure_ascii=False)}]
 if index==0:
  verdict={'kind':'counterexamples','witnesses':[{'kind':'feasibility','x':[1,1],'expected_feasible':False,'proposed_feasible':True}]}
  traces=[{'x':[1,1],'rows':[],'candidate_feasible':True,'candidate_objective':8}]
  gloss='Witness 1: the REFERENCE REJECTS this assignment; YOUR CANDIDATE ACCEPTS it. The row evaluations describe YOUR candidate only.'
 elif index==2:verdict={'kind':'schema','message':SCHEMA_MESSAGE};traces=[];gloss='Invalid initial model: provide an explicit complete replace_model edit.'
 elif index==4:
  verdict={'kind':'counterexamples','witnesses':[{'kind':'objective','x':[1,0],'expected_value':3,'proposed_value':7},{'kind':'objective','x':[1,1],'expected_value':8,'proposed_value':12}]}
  traces=[{'x':x,'rows':[{'index':0,'lhs':sum(x),'op':'<=','rhs':1,'satisfied':sum(x)<=1}],'candidate_feasible':sum(x)<=1,'candidate_objective':v} for x,v in [([1,0],7),([1,1],12)]]
  gloss='Witness 1: reference objective 3, candidate objective 7. Witness 2: reference objective 8, candidate objective 12.'
 else:verdict={'kind':'no_counterexample','message':'No discrepancy on the finite cube. Preserve all model fields.'};traces=[];gloss='No counterexample: preserve every correct field.'
 for phase,raw in [('initial',first_raw),('direct',direct_raw),('self',self_raw),('guided',guided_raw)]:
  messages=base if phase in ['initial','direct'] else [{'role':'system','content':'PATCH_FIXTURE'},base[1],{'role':'assistant','content':first_raw},{'role':'user','content':SELF_INSTRUCTION if phase=='self' else json.dumps({'verifier_feedback':verdict,'candidate_evaluation_tool':traces,'gloss':gloss,'instruction':GUIDED_INSTRUCTION},ensure_ascii=False)}]
  lp=-0.5 if phase=='initial' else -0.8 if phase=='direct' and index==1 else -0.2
  r={'id':identity,'phase':phase,'seed':(int(hashlib.sha256(identity.encode()).hexdigest()[:8],16)+(phase!='initial'))%2**32,'messages':messages,'raw_response':raw,'parsed':parse_proposal(raw,2) if phase in ['initial','direct'] else parse_patch(raw,2,first_raw),'input_token_ids':[1],'input_tokens':1,'generated_token_ids':[2],'output_tokens':1,'generated_token_log_probabilities':[lp],'mean_generated_log_probability':lp,'finish_reason':'eos','wall_seconds':0.01,'cpu_seconds':0.001,'source_provenance':'synthetic software fixture; no model sampled'}
  if phase in ['self','guided']:r['initial_response_sha256']=hashlib.sha256(first_raw.encode()).hexdigest()
  phase_rows[phase].append(r)
cp=root/'cases.json';gp=root/'gold.json';cp.write_text(json.dumps(cases));gp.write_text(json.dumps(gold))
paths={}
for phase,rs in phase_rows.items():
 p=root/phase;p.mkdir();paths[phase]=p/'raw.jsonl';paths[phase].write_text(''.join(json.dumps(x)+'\n' for x in rs));(p/'generation.json').write_text(json.dumps({'status':'synthetic_software_fixture','load_seconds':0,'wall_seconds':0.01,'client_cpu_seconds':0.001,'server_cpu_seconds':0,'server_cpu_scope':'no model was run'}))
study.feedback(cp,gp,paths['initial'],root/'feedback')
study.score(cp,gp,paths['initial'],paths['direct'],paths['self'],paths['guided'],root/'scores',root/'feedback/reports.jsonl')
m=json.loads((root/'scores/metrics.json').read_text());counts={k:v['faithful'] for k,v in m['methods'].items()};assert counts=={'initial':2,'direct':5,'self':1,'guided':4},counts
assert m['H23']['status']=='supported_in_finite_test' and m['H23']['guided_minus_self_faithful']==3
assert m['methods']['guided']['regressions_from_faithful']==1
assert m['methods']['guided']['format_repairs_to_faithful']==1 and m['methods']['guided']['mathematical_repairs_to_faithful']==2
assert m['physical_generation_calls']==20
rs=[json.loads(x) for x in (root/'scores/raw.jsonl').read_text().splitlines()];fallback=next(x for x in rs if x['id']=='fixture-3')['results']['guided'];assert fallback['selected_candidate_index']==0
print(json.dumps({'synthetic_counts':counts,'checks_passed':8,'new_model_calls':0,'scope':'software integration only, not agent performance'}))
