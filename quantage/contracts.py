"""Explicit boundary for externally proposed finite models.

The historical core and its manifests remain immutable. This module validates
before delegating to its finite output oracle; it does not certify language
understanding, circuits for every input, or physical hardware compatibility.
"""
import math
from .core import MIS_INTENT, PHOTO_INTENT, Unsupported, understand
from .verification import verify


class ContractError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise ContractError(message)


def keys(value, required, optional=()):
    need(type(value) is dict, 'object required')
    need(set(required) <= set(value) <= set(required) | set(optional), 'missing or unknown fields')


def integer(value):
    return type(value) is int


def finite_real(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except (OverflowError, ValueError):
        return False


def normalize_problem(problem):
    need(type(problem) is dict, 'problem must be object')
    family = problem.get('family')
    if family == 'mis':
        keys(problem, ('family','n','edges','weights','objective','domain','constraints'))
        need(problem['objective'] == 'maximize_weight' and problem['domain'] == 'binary'
             and problem['constraints'] == 'independent', 'unsupported MIS task')
        request = {'intent':MIS_INTENT, 'data':{k:problem[k] for k in ('n','edges','weights')}}
    elif family == 'photon':
        keys(problem, ('family','a','b','phi','input','modes','loss','observable'))
        need(type(problem['input']) is list and len(problem['input']) == 2
             and all(integer(x) for x in problem['input']) and problem['input'] == [1,0], 'unsupported optical input')
        need(problem['observable'] == 'probabilities', 'unsupported observable')
        request = {'intent':PHOTO_INTENT, 'data':{k:problem[k] for k in ('a','b','phi','modes','loss')}}
        request['data']['photons'] = 1
    else:
        raise ContractError('unknown family')
    try:
        return understand(request)
    except (Unsupported, TypeError, ValueError, OverflowError) as exc:
        raise ContractError(str(exc))


def validate_model(problem, model):
    p = normalize_problem(problem)
    if p['family'] == 'mis':
        keys(model, ('kind','linear','quadratic','constant','sense'), ('penalty',))
        need(model['kind'] == 'qubo', 'expected qubo')
        need(model['sense'] in ('minimize','maximize'), 'unknown objective sense')
        need(type(model['linear']) is list and len(model['linear']) == p['n']
             and all(integer(x) for x in model['linear']), 'exact integer linear coefficients required')
        need(integer(model['constant']), 'exact integer constant required')
        need(type(model['quadratic']) is list, 'quadratic terms must be list')
        seen = set()
        for term in model['quadratic']:
            need(type(term) is list and len(term) == 3, 'term must be [i,j,coefficient]')
            i, j, value = term
            need(integer(i) and integer(j) and 0 <= i < j < p['n'], 'indices must satisfy 0<=i<j<n')
            need(integer(value), 'exact integer quadratic coefficients required')
            need((i,j) not in seen, 'duplicate quadratic term')
            seen.add((i,j))
        if 'penalty' in model:
            need(integer(model['penalty']), 'exact integer penalty metadata required')
            need(all(value == model['penalty'] for i,j,value in model['quadratic']), 'penalty metadata contradicts coefficients')
    else:
        keys(model, ('kind','a','b','phi','phase_mode','input_mode','order','global_phase','coherent','output'))
        need(model['kind'] == 'linear_optics', 'expected linear_optics')
        need(all(finite_real(model[k]) for k in ('a','b','phi','global_phase')), 'finite real angles required')
        need(integer(model['input_mode']) and model['input_mode'] in (0,1), 'input mode must be 0 or 1')
        need(integer(model['phase_mode']) and model['phase_mode'] in (0,1), 'phase mode must be 0 or 1')
        need(model['order'] in ('R_b P R_a','R_a P R_b'), 'unknown component order')
        need(type(model['coherent']) is bool, 'coherent must be boolean')
        need(model['output'] == 'probabilities', 'probability output required')
    return p


def verify_external(problem, model, tolerance=1e-12):
    try:
        need(finite_real(tolerance) and 0 < tolerance <= 1e-6, 'invalid or unsupported tolerance')
        normalized = validate_model(problem, model)
    except (ContractError, KeyError, TypeError, ValueError, OverflowError) as exc:
        return {'valid':False, 'stage':'schema', 'reason':str(exc)}
    result = verify(normalized, model, tolerance)
    return dict(result, stage='finite_output', scope='this normalized instance only')
