"""Bounded development fix: unresolved direction overrides positive keywords."""
import re
import unicodedata
from .compact_agent import TASKS
from .compact_v2 import execute_v2
from .compact_v3 import semantic_veto_v3


def semantic_veto_v4(request,task):
    result=semantic_veto_v3(request,task)
    text=''.join(c for c in unicodedata.normalize('NFD',request['intent'].casefold()) if unicodedata.category(c)!='Mn')
    if task==TASKS['mis']:
        patterns=[r'(?:not decided|undecided|undetermined|unresolved|not specified)[^.;\n]{0,65}(?:goal|objective|direction|choice)',
                  r'(?:goal|objective|direction|choice)[^.;\n]{0,100}(?:unresolved|unknown|undecided)',
                  r'(?:pas decide|non precise|indetermine)[^.;\n]{0,65}(?:objectif|direction|choix)']
        if any(re.search(p,text) for p in patterns):
            result['reasons'].append('objective direction explicitly unresolved')
            result['passed']=False
    result['scope']='bounded development veto v4, not universal semantic certification'
    return result


def execute_v4(request,parsed,guard=True):
    if guard and parsed['valid'] and parsed['proposal']['action']=='propose':
        assessment=semantic_veto_v4(request,parsed['proposal']['task'])
        if not assessment['passed']:return {'status':'abstain','stage':'semantic_veto','assessment':assessment}
    result=execute_v2(request,parsed,False)
    result['schema']='compact-v4-development'
    if guard:result['semantic_guard']='bounded development veto v4 applied'
    return result
