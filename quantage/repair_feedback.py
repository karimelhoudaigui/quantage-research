"""Closed verifier feedback and optional finite optimization diagnostics."""
import itertools
from .repair_model import need, model_feasible, objective_value, reference_feasible

SCHEMA_MESSAGE = 'Invalid JSON or documented model schema. Rebuild a complete binary_ilp object with variables,sense,objective,constraints and explicit integer rows.'

def validate_feedback(feedback, n):
    need(type(feedback) is dict and type(feedback.get('kind')) is str, 'invalid feedback object')
    kind = feedback['kind']
    if kind == 'schema':
        need(set(feedback) == {'kind', 'message'} and feedback['message'] == SCHEMA_MESSAGE, 'invalid schema feedback')
    elif kind == 'no_counterexample':
        need(set(feedback) == {'kind', 'message'} and feedback['message'] ==
             'No discrepancy on the finite cube. Preserve all model fields.', 'invalid success feedback')
    elif kind == 'counterexamples':
        need(set(feedback) == {'kind', 'witnesses'} and type(feedback['witnesses']) is list
             and 1 <= len(feedback['witnesses']) <= 3, 'invalid witness feedback')
        seen = set()
        for witness in feedback['witnesses']:
            need(type(witness) is dict and type(witness.get('x')) is list
                 and len(witness['x']) == n and all(type(x) is int and x in (0, 1) for x in witness['x']),
                 'invalid binary witness')
            point = tuple(witness['x'])
            need(point not in seen, 'duplicate witness')
            seen.add(point)
            if witness.get('kind') == 'feasibility':
                need(set(witness) == {'kind','x','expected_feasible','proposed_feasible'}
                     and type(witness['expected_feasible']) is bool and type(witness['proposed_feasible']) is bool
                     and witness['expected_feasible'] != witness['proposed_feasible'], 'invalid feasibility witness')
            elif witness.get('kind') == 'objective':
                need(set(witness) == {'kind','x','expected_value','proposed_value'}
                     and all(type(witness[k]) is int and abs(witness[k]) <= 80000 for k in ('expected_value','proposed_value'))
                     and witness['expected_value'] != witness['proposed_value'], 'invalid objective witness')
            else:
                raise ValueError('unknown witness type')
    else:
        raise ValueError('unknown feedback kind')
    return feedback


def feedback_for_model(report, n):
    if report['stage'] == 'schema':
        return {'kind':'schema','message':SCHEMA_MESSAGE}
    return validate_feedback(report['feedback'],n)


def optimization_diagnostics(data, reference, parsed):
    if not parsed['valid']:
        return {'optimizer_set_equal':False,'finite_optimization_equivalent':False}
    target=[];candidate=[]
    same_domain=True
    for bits in itertools.product((0,1),repeat=data['n']):
        a=reference_feasible(data,reference,bits)
        b=model_feasible(parsed['model'],bits)
        same_domain &= a==b
        if a:target.append((sum(w*x for w,x in zip(data['weights'],bits)),bits))
        if b:candidate.append((objective_value(parsed['model'],bits),bits))
    def optima(values):
        if not values:return set()
        best=max(v for v,x in values)
        return {x for v,x in values if v==best}
    same_optima=optima(target)==optima(candidate)
    return {'optimizer_set_equal':same_optima,'finite_optimization_equivalent':bool(same_domain and same_optima)}
