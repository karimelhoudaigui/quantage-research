"""Nonredundant semantic task proposal and bounded text veto, no gold access."""
import json
import re
import unicodedata
from .compact_agent import TASKS,execute_compact


def parse_v2(raw):
    text=raw.strip();match=re.fullmatch(r'```(?:json)?\s*\n([\s\S]*?)\n```',text)
    if match:text=match.group(1)
    try:
        p=json.loads(text,parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
        if type(p) is not dict or set(p)!={'action','task','reason'} or type(p['reason']) is not str:
            raise ValueError('exact v2 fields required')
        if p['action'] not in ('propose','abstain'):raise ValueError('unknown action')
        if p['action']=='abstain' and p['task'] is not None:raise ValueError('abstention task must be null')
        if p['action']=='propose' and p['task'] not in TASKS.values():raise ValueError('unknown task')
        return {'valid':True,'proposal':p,'single_code_fence_removed':bool(match)}
    except (TypeError,ValueError,KeyError) as exc:return {'valid':False,'reason':str(exc)}


def semantic_veto(request,task):
    text=''.join(c for c in unicodedata.normalize('NFD',request['intent'].casefold()) if unicodedata.category(c)!='Mn')
    reasons=[]
    if task==TASKS['mis']:
        requirements=[(r'maxim|\bmaximum\b','maximum direction'),(r'\bweights?\b|\bpoids\b','weight objective'),
                      (r'independ|conflict|incompatib|adjacen|extremit|endpoint','independence constraints')]
        for pattern,name in requirements:
            if not re.search(pattern,text):reasons.append('not recognized: '+name)
        forbidden=[r'\bminimi|\bminimum\b',r'\bcount\b|\bcompter\b|\bcomptage\b',r'cardinal',
                   r'\bexactly\b|\bexactement\b',r'\bmaximal independent set\b|\bensemble independant maximal\b',
                   r'\b(?:must|required|mandatory)\b[^.;\n]{0,35}\b(?:include|vertex|node)\b',
                   r'\b(?:vertex|node)\s*\d[^.;\n]{0,35}\b(?:must|always|mandatory)\b',
                   r'\binclu[^.;\n]{0,30}\bsommet\b|\bimpos|\bobligatoir']
    else:
        requirements=[(r'probabil','probability observable'),(r'ideal|coheren|lossless|sans perte','ideal/coherent scope'),
                      (r'\bmode\s*0\b|\bport\s*0\b','input mode zero')]
        for pattern,name in requirements:
            if not re.search(pattern,text):reasons.append('not recognized: '+name)
        forbidden=[r'amplitud',r'degree|degre|°',r'post.?select|conditionn',r'\bphase\b[^.;\n]{0,35}\bmode\s*0\b']
    if any(re.search(p,text) for p in forbidden):reasons.append('recognized unsupported or conflicting clause')
    return {'passed':not reasons,'reasons':reasons,'scope':'bounded lexical veto, not universal semantic certification'}


def execute_v2(request,parsed,guard=False):
    if not parsed['valid']:return {'status':'abstain','stage':'format','reason':parsed['reason']}
    p=parsed['proposal']
    if p['action']=='abstain':return {'status':'abstain','stage':'model_abstention','reason':p['reason']}
    if guard:
        assessment=semantic_veto(request,p['task'])
        if not assessment['passed']:return {'status':'abstain','stage':'semantic_veto','assessment':assessment}
    family=next(f for f,t in TASKS.items() if t==p['task'])
    expanded={'valid':True,'proposal':dict(p,family=family),'single_code_fence_removed':parsed['single_code_fence_removed']}
    result=execute_compact(request,expanded)
    result['schema']='compact-v2'
    if guard:result['semantic_guard']='bounded lexical veto applied'
    return result
