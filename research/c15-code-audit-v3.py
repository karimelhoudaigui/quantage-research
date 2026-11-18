"""Independent finite regression audit, no inference and no author labels.

Usage: python3 research/c15-code-audit-v3.py --output NEW_OUTPUT_JSON
"""
import argparse
import copy
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd()))
from quantage.repair_model import parse_model, verify_model
from quantage.repair_feedback import validate_feedback, feedback_for_model, optimization_diagnostics, SCHEMA_MESSAGE
from quantage.repair_solvers import enumeration_dfs, scipy_highs_milp, portfolio


def encode(data, c):
    n = data['n']
    rows = []
    def row(indices, relation, rhs):
        vector = [0] * n
        for index, value in indices:
            vector[index] += value
        rows.append([vector, relation, rhs])
    for a, b in data['edges']:
        row([(a, 1), (b, 1)], '<=', 1)
    if c['budget'] is not None:
        rows.append([data['costs'][:], '<=', c['budget']])
    if c['min_count'] is not None:
        rows.append([[1] * n, '>=', c['min_count']])
    if c['max_count'] is not None:
        rows.append([[1] * n, '<=', c['max_count']])
    for i in c['required']:
        row([(i, 1)], '==', 1)
    for i in c['forbidden']:
        row([(i, 1)], '==', 0)
    for a, b in c['implications']:
        row([(a, 1), (b, -1)], '<=', 0)
    return dict(formulation='binary_ilp', variables=list(range(n)), sense='max',
                objective=data['weights'][:], constraints=rows)


def independent_table(model):
    values = {}
    for binary in itertools.product((0, 1), repeat=len(model['variables'])):
        sums = [(sum(coefficients[i] * binary[i] for i in range(len(binary))), relation, rhs)
                for coefficients, relation, rhs in model['constraints']]
        okay = all({'<=': lhs <= rhs, '>=': lhs >= rhs, '==': lhs == rhs}[relation]
                   for lhs, relation, rhs in sums)
        values[binary] = (okay, sum(model['objective'][i] * binary[i] for i in range(len(binary))))
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    base = Path('runs/20261114-c15-formulation-repair')
    cases = {r['id']: r for split in ('dev', 'test')
             for r in json.loads((base / (split + '_cases.json')).read_text())}
    gold = json.loads((base / 'private_gold.review.json').read_text())
    oracle = {r['id']: r for r in json.loads(Path('research/c15-annotation-oracle/raw.json').read_text())['cases']}
    rows = []
    invalid_count = 0
    feedback_controls = 0
    invalid_feedbacks = [
        {'kind': 'counterexamples', 'witnesses': [], 'model': {}},
        {'kind': 'counterexamples', 'witnesses': []},
        {'kind': 'no_counterexample', 'message': 'wrong message'},
        {'kind': 'schema', 'detail': 'x', 'reference_model': {}},
        {'kind': 'schema', 'detail': 'budget=10; corrected model'},
        {'kind': 'schema', 'message': SCHEMA_MESSAGE, 'reference_model': {}},
        {'kind': 'schema', 'message': 'budget=10; corrected model'},
        {'kind': 'counterexamples', 'witnesses': [dict(kind='feasibility', x=[True, 0], expected_feasible=False, proposed_feasible=True)]},
        {'kind': 'counterexamples', 'witnesses': [dict(kind='feasibility', x=[0, 0], expected_feasible=False, proposed_feasible=False)]},
        {'kind': 'counterexamples', 'witnesses': [dict(kind='objective', x=[0, 0], expected_value=1.0, proposed_value=0)]},
    ]
    point = dict(kind='feasibility', x=[0, 0], expected_feasible=False, proposed_feasible=True)
    invalid_feedbacks.append(dict(kind='counterexamples', witnesses=[point, point]))
    for feedback in invalid_feedbacks:
        try:
            validate_feedback(feedback, 2)
        except ValueError:
            feedback_controls += 1
        else:
            raise AssertionError('Invalid feedback accepted: ' + repr(feedback))
    normalized = feedback_for_model({'stage': 'schema', 'feedback': {'kind': 'schema', 'detail': 'budget=10; corrected model'}}, 2)
    assert normalized == {'kind': 'schema', 'message': SCHEMA_MESSAGE}
    validate_feedback(normalized, 2)
    for label in gold:
        case = cases[label['id']]
        data = case['data']
        canonical = encode(data, label['constraints'])
        baseline = independent_table(canonical)
        expected_masks = sorted(sum(bit << i for i, bit in enumerate(x)) for x, (f, _) in baseline.items() if f)
        assert expected_masks == oracle[label['id']]['feasible_masks']
        variants = [('canonical', canonical)]
        # Every omitted row is checked; redundant omissions need not be rejected.
        for index in range(len(canonical['constraints'])):
            candidate = copy.deepcopy(canonical)
            del candidate['constraints'][index]
            variants.append(('omit_row_' + str(index), candidate))
        changed = copy.deepcopy(canonical)
        changed['objective'][0] += 1
        variants.append(('wrong_objective', changed))
        scaled = copy.deepcopy(canonical)
        scaled['objective'] = [2 * x for x in scaled['objective']]
        variants.append(('scaled_objective', scaled))
        redundant = copy.deepcopy(canonical)
        redundant['constraints'].append([[0] * data['n'], '<=', 0])
        variants.append(('redundant_zero_row', redundant))
        observations = []
        for name, model in variants:
            parsed = parse_model(json.dumps(model), data['n'])
            assert parsed['valid']
            got = verify_model(data, label['constraints'], parsed)
            got.update(optimization_diagnostics(data, label['constraints'], parsed))
            table = independent_table(model)
            wrong_f = sum(table[x][0] != baseline[x][0] for x in table)
            wrong_v = sum(table[x][1] != baseline[x][1] for x in table)
            assert got['feasibility_mismatches'] == wrong_f
            assert got['objective_mismatches'] == wrong_v
            assert got['faithful'] == (wrong_f == wrong_v == 0)
            assert got['assignments'] == 2 ** data['n']
            ref_best = max((value for feasible, value in baseline.values() if feasible), default=None)
            candidate_best = max((value for feasible, value in table.values() if feasible), default=None)
            ref_opts = {x for x, (f, v) in baseline.items() if f and v == ref_best}
            candidate_opts = {x for x, (f, v) in table.items() if f and v == candidate_best}
            assert got['optimizer_set_equal'] == (ref_opts == candidate_opts)
            assert got['finite_optimization_equivalent'] == (wrong_f == 0 and ref_opts == candidate_opts)
            validate_feedback(feedback_for_model(got, data['n']), data['n'])
            expected_witnesses = []
            for x in table:
                if len(expected_witnesses) == 3:
                    break
                if table[x][0] != baseline[x][0]:
                    expected_witnesses.append(dict(kind='feasibility', x=list(x), expected_feasible=baseline[x][0], proposed_feasible=table[x][0]))
                elif table[x][1] != baseline[x][1]:
                    expected_witnesses.append(dict(kind='objective', x=list(x), expected_value=baseline[x][1], proposed_value=table[x][1]))
            if expected_witnesses:
                assert got['feedback'] == dict(kind='counterexamples', witnesses=expected_witnesses)
            else:
                assert got['feedback']['kind'] == 'no_counterexample'
            observations.append(dict(variant=name, faithful=got['faithful'], wrong_f=wrong_f, wrong_v=wrong_v,
                                     feedback=got['feedback']))
        invalids = []
        for mutation in ('float', 'bool', 'large', 'arity', 'variable_order', 'extra_key', 'relation'):
            model = copy.deepcopy(canonical)
            if mutation == 'float': model['objective'][0] = 1.0
            if mutation == 'bool': model['objective'][0] = True
            if mutation == 'large': model['objective'][0] = 10001
            if mutation == 'arity': model['objective'].append(1)
            if mutation == 'variable_order': model['variables'].reverse()
            if mutation == 'extra_key': model['canonical_model'] = {}
            if mutation == 'relation': model['constraints'][0][1] = '<'
            invalids.append(json.dumps(model))
        invalids += ['{"formulation":"binary_ilp","formulation":"binary_ilp"}',
                     '{"objective":[NaN]}', json.dumps(canonical) + '\ntrailing prose']
        for invalid in invalids:
            parsed = parse_model(invalid, data['n'])
            assert not parsed['valid']
            report = verify_model(data, label['constraints'], parsed)
            assert report['stage'] == 'schema'
            assert feedback_for_model(report, data['n']) == normalized
            invalid_count += 1
        exact = enumeration_dfs(canonical)
        milp = scipy_highs_milp(canonical, time_limit=2)
        expected = oracle[label['id']]
        target_status = 'optimal' if expected['feasible_count'] else 'infeasible'
        assert exact['status'] == milp['status'] == target_status
        assert exact['objective'] == milp['objective'] == expected['max_weight']
        if target_status == 'optimal':
            assert sorted(sum(bit << i for i, bit in enumerate(x)) for x in exact['all_optima']) == expected['optimal_masks']
            assert sum(bit << i for i, bit in enumerate(milp['solution'])) in expected['optimal_masks']
        p = portfolio(canonical)
        assert p['concordance'] and p['objective'] == expected['max_weight']
        assert p['selected_solver'] == min(p['solvers'], key=lambda r: r['seconds'])['solver']
        assert p['total_portfolio_seconds'] >= sum(r['seconds'] for r in p['solvers'])
        rows.append(dict(id=label['id'], mutations=observations, dfs=exact, milp=milp, portfolio=p))
    result = dict(assertion_tested='Production finite verification and solver outputs agree with frozen independent reviewer domains on all public C15 instances and explicit model mutations.',
                  cases=rows, case_count=len(rows), invalid_parser_cases=invalid_count,
                  invalid_feedback_controls=feedback_controls,
                  model_variants=sum(len(r['mutations']) for r in rows),
                  non_claims=['No LLM generation or output scoring.', 'Finite domains, not arbitrary text.', 'Canonical audit encoding is never sent to inference.'])
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('case_count', 'invalid_parser_cases', 'model_variants')}))


if __name__ == '__main__':
    main()
