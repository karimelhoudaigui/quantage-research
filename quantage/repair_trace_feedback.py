"""Exact evaluations of the candidate's OWN rows, with no target coefficients."""
from .repair_feedback import feedback_for_model,validate_feedback as validate_minimal

FIELDS={'verdict','candidate_evaluations','gloss'}
def compare(lhs,op,rhs):return lhs<=rhs if op=='<=' else lhs>=rhs if op=='>=' else lhs==rhs

def validate_feedback(value,n):
 if type(value) is not dict or set(value)!=FIELDS:raise ValueError('exact trace feedback fields required')
 verdict=validate_minimal(value['verdict'],n)
 if type(value['gloss']) is not str or len(value['gloss'])>8192 or not value['gloss'].isascii():raise ValueError('bounded ASCII gloss')
 traces=value['candidate_evaluations'];expected=verdict.get('witnesses',[])
 if type(traces) is not list or len(traces)!=len(expected):raise ValueError('one candidate trace per witness')
 for t,w in zip(traces,expected):
  if type(t) is not dict or set(t)!={'x','rows','candidate_feasible','candidate_objective'} or t['x']!=w['x']:raise ValueError('trace point mismatch')
  if type(t['rows']) is not list or len(t['rows'])>32:raise ValueError('bounded candidate rows')
  for i,row in enumerate(t['rows']):
   if type(row) is not dict or set(row)!={'index','lhs','op','rhs','satisfied'} or type(row['index']) is not int or row['index']!=i:raise ValueError('candidate row schema')
   if row['op'] not in ('<=','>=','==') or type(row['lhs']) is not int or abs(row['lhs'])>80000 or type(row['rhs']) is not int or abs(row['rhs'])>10000:raise ValueError('candidate arithmetic bounds')
   if type(row['satisfied']) is not bool or row['satisfied']!=compare(row['lhs'],row['op'],row['rhs']):raise ValueError('incorrect candidate row evaluation')
  if type(t['candidate_feasible']) is not bool or t['candidate_feasible']!=all(row['satisfied'] for row in t['rows']):raise ValueError('candidate conjunction')
  if type(t['candidate_objective']) is not int or abs(t['candidate_objective'])>80000:raise ValueError('candidate objective bounds')
  if w['kind']=='feasibility' and t['candidate_feasible']!=w['proposed_feasible']:raise ValueError('trace contradicts candidate verdict')
  if w['kind']=='objective' and t['candidate_objective']!=w['proposed_value']:raise ValueError('trace contradicts objective verdict')
 return value

def build_feedback(report,parsed,n):
 verdict=feedback_for_model(report,n);traces=[];gloss=[]
 for index,w in enumerate(verdict.get('witnesses',[])):
  model=parsed['model'];x=w['x'];values=[]
  for i,(coeff,op,rhs) in enumerate(model['constraints']):
   lhs=sum(a*b for a,b in zip(coeff,x));values.append({'index':i,'lhs':lhs,'op':op,'rhs':rhs,'satisfied':compare(lhs,op,rhs)})
  traces.append({'x':x,'rows':values,'candidate_feasible':all(r['satisfied'] for r in values),'candidate_objective':sum(a*b for a,b in zip(model['objective'],x))})
  if w['kind']=='feasibility':
   gloss.append('Witness '+str(index+1)+': the REFERENCE '+('ACCEPTS' if w['expected_feasible'] else 'REJECTS')+' this assignment; YOUR CANDIDATE '+('ACCEPTS' if w['proposed_feasible'] else 'REJECTS')+' it. The row evaluations describe YOUR candidate only.')
  else:gloss.append('Witness '+str(index+1)+': reference objective '+str(w['expected_value'])+', candidate objective '+str(w['proposed_value'])+'.')
 if not gloss:gloss=['No counterexample: preserve every correct field.' if verdict['kind']=='no_counterexample' else 'Invalid initial model: provide an explicit complete replace_model edit.']
 return validate_feedback({'verdict':verdict,'candidate_evaluations':traces,'gloss':' '.join(gloss)},n)
