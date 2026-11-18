"""Development fix after C09; never relabel this as a new held-out test."""
import re
import unicodedata
from .compact_agent import TASKS
from .compact_v2 import execute_v2


def semantic_veto_v3(request,task):
    text=''.join(c for c in unicodedata.normalize('NFD',request['intent'].casefold()) if unicodedata.category(c)!='Mn')
    reasons=[]
    if task==TASKS['mis']:
        requirements=[(r'maxim|\bmaximum\b|\bgreatest\b|\blargest\b','maximum direction'),
                      (r'\bweights?\b|\bpoids\b','weight objective'),
                      (r'independ|conflict|incompatib|adjacen|extremit|endpoint','independence constraints')]
        forbidden=[r'\bminimi|\bminimum\b',r'\bcount\b|\bcompter\b|\bcomptage\b',r'cardinal',
                   r'\bexactly\b|\bexactement\b',r'\bmaximal independent set\b|\bensemble independant maximal\b',
                   r'\b(?:must|required|mandatory)\b[^.;\n]{0,35}\b(?:include|vertex|node)\b',
                   r'\b(?:vertex|node)\s*\d[^.;\n]{0,35}\b(?:must|always|mandatory)\b',
                   r'\binclu[^.;\n]{0,30}\bsommet\b|\bimpos|\bobligatoir']
    else:
        requirements=[(r'probabil|\bdistribution\b','probability observable'),
                      (r'ideal|coheren|lossless|sans perte','ideal/coherent scope'),
                      (r'\bmode\s*0\b|\bport\s*0\b','input mode zero')]
        forbidden=[r'amplitud',r'degree|degre|°',r'post.?select|conditionn',r'\bphase\b[^.;\n]{0,35}\bmode\s*0\b',
                   r'\binput(?: mode| port)?\b[^.;\n]{0,45}(?:\bnot\b|unknown|unspecified|unresolved|missing)',
                   r'(?:mode d.entree|\bentree\b)[^.;\n]{0,40}(?:\bnon\b|\bpas\b|inconnu|indetermine)',
                   r'(?:may be|either|soit)[^.;\n]{0,15}mode\s*0[^.;\n]{0,15}(?:\bor\b|\bou\b)[^.;\n]{0,10}mode\s*1']
    for pattern,name in requirements:
        if not re.search(pattern,text):reasons.append('not recognized: '+name)
    if any(re.search(pattern,text) for pattern in forbidden):reasons.append('unsupported, conflicting or unresolved clause')
    return {'passed':not reasons,'reasons':reasons,'scope':'bounded development veto, not universal semantic certification'}


def execute_v3(request,parsed,guard=True):
    if guard and parsed['valid'] and parsed['proposal']['action']=='propose':
        assessment=semantic_veto_v3(request,parsed['proposal']['task'])
        if not assessment['passed']:return {'status':'abstain','stage':'semantic_veto','assessment':assessment}
    result=execute_v2(request,parsed,False)
    result['schema']='compact-v3-development'
    if guard:result['semantic_guard']='bounded development veto applied'
    return result
