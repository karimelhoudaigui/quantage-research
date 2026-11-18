"""Explicit binary ILPs and finite counterexamples, never a canonical repair."""
import itertools
import json

FIELDS = {'formulation', 'variables', 'sense', 'objective', 'constraints'}


def need(value, message):
    if not value:
        raise ValueError(message)


def integer(value):
    return type(value) is int and abs(value) <= 10000


def validate_model(model, n):
    need(type(n) is int and 1 <= n <= 8, 'finite domain requires 1<=n<=8')
    need(type(model) is dict and set(model) == FIELDS, 'exact fields: formulation,variables,sense,objective,constraints')
    need(model['formulation'] == 'binary_ilp' and model['sense'] == 'max', 'binary_ilp and max required')
    need(type(model['variables']) is list and all(type(i) is int for i in model['variables'])
         and model['variables'] == list(range(n)), 'variables must be the ordered item indices 0..n-1')
    need(type(model['objective']) is list and len(model['objective']) == n
         and all(integer(x) for x in model['objective']), 'one integer objective coefficient per variable')
    need(type(model['constraints']) is list and len(model['constraints']) <= 32, 'at most32 explicit linear rows')
    for row in model['constraints']:
        need(type(row) is list and len(row) == 3, 'row is [coefficient_vector,relation,rhs]')
        a, op, b = row
        need(type(a) is list and len(a) == n and all(integer(x) for x in a), 'integer coefficient vector has wrong arity/type')
        need(type(op) is str and op in ('<=', '>=', '==') and integer(b), 'invalid relation or integer rhs')
    return model


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def parse_model(text, n):
    raw = text.strip()
    fence = chr(96) * 3
    lines = raw.split('\n')
    stripped = len(lines) >= 3 and lines[0] in (fence, fence + 'json') and lines[-1] == fence
    if stripped:
        raw = '\n'.join(lines[1:-1])
    try:
        model = json.loads(raw, object_pairs_hook=no_duplicates,
                           parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
        validate_model(model, n)
        return {'valid': True, 'model': model, 'single_fence_removed': stripped}
    except (ValueError, TypeError, KeyError) as exc:
        return {'valid': False, 'error': str(exc)}


def objective_value(model, bits):
    return sum(a * x for a, x in zip(model['objective'], bits))


def model_feasible(model, bits):
    for a, op, b in model['constraints']:
        lhs = sum(c * x for c, x in zip(a, bits))
        if (op == '<=' and lhs > b) or (op == '>=' and lhs < b) or (op == '==' and lhs != b):
            return False
    return True


def reference_feasible(data, constraints, bits):
    """Trusted annotated contract; this code never generates a corrected ILP."""
    if any(bits[i] and bits[j] for i, j in data['edges']):
        return False
    if constraints['budget'] is not None and sum(c*x for c, x in zip(data['costs'], bits)) > constraints['budget']:
        return False
    size = sum(bits)
    if constraints['min_count'] is not None and size < constraints['min_count']:
        return False
    if constraints['max_count'] is not None and size > constraints['max_count']:
        return False
    if any(not bits[i] for i in constraints['required']) or any(bits[i] for i in constraints['forbidden']):
        return False
    if any(bits[i] and not bits[j] for i, j in constraints['implications']):
        return False
    return True


def verify_model(data, constraints, parsed, witness_limit=3):
    if not parsed['valid']:
        return {'faithful': False, 'stage': 'schema', 'feedback': {'kind': 'schema', 'detail': parsed['error']},
                'feasibility_mismatches': None, 'objective_mismatches': None, 'assignments': 0}
    n = data['n']
    model = validate_model(parsed['model'], n)
    witnesses = []
    wrong_f = wrong_v = feasible_ref = feasible_proposed = 0
    for bits in itertools.product((0, 1), repeat=n):
        expected_f = reference_feasible(data, constraints, bits)
        got_f = model_feasible(model, bits)
        expected_v = sum(w*x for w, x in zip(data['weights'], bits))
        got_v = objective_value(model, bits)
        wrong_f += int(expected_f != got_f)
        wrong_v += int(expected_v != got_v)
        feasible_ref += int(expected_f)
        feasible_proposed += int(got_f)
        if len(witnesses) < witness_limit:
            if expected_f != got_f:
                witnesses.append({'kind': 'feasibility', 'x': list(bits),
                                  'expected_feasible': expected_f, 'proposed_feasible': got_f})
            elif expected_v != got_v:
                witnesses.append({'kind': 'objective', 'x': list(bits),
                                  'expected_value': expected_v, 'proposed_value': got_v})
    faithful = wrong_f == wrong_v == 0
    feedback = {'kind': 'no_counterexample', 'message': 'No discrepancy on the finite cube. Preserve all model fields.'} if faithful else {'kind': 'counterexamples', 'witnesses': witnesses}
    return {'faithful': faithful, 'stage': 'finite_cube', 'feedback': feedback,
            'assignments': 2**n, 'feasibility_mismatches': wrong_f, 'objective_mismatches': wrong_v,
            'reference_feasible_count': feasible_ref, 'proposed_feasible_count': feasible_proposed,
            'scope': 'exact finite feasibility and objective values relative to annotated contract, not arbitrary NL certification'}
