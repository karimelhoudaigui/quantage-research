"""Independent exact frontend and controller SOFTWARE audit, no model calls."""
import argparse
import copy
import importlib.util
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd()))
from quantage.repair_language import compile_constraint, parse_proposal
from quantage.repair_model import parse_model, verify_model
from quantage.repair_feedback import validate_feedback
from quantage.repair_loop import run_loop, _validate_record


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def proposal(rows, n=3, objective=None):
    return dict(formulation='binary_ilp', variables=list(range(n)), sense='max',
                objective=objective or [7, 4, 5][:n], constraints=rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output
    probes = []
    truth_checks = 0
    for coefficients in itertools.product(range(-2, 3), repeat=3):
        left = '+'.join('(%s)*x%s' % (value, i) for i, value in enumerate(coefficients)) + '-1'
        right = 'x0-2*x1+4'
        for relation in ('<=', '>=', '=='):
            expression = left + relation + right
            row = compile_constraint(expression, 3)
            assert row == [[coefficients[0]-1, coefficients[1]+2, coefficients[2]], relation, 5]
            for point in itertools.product((-2, 0, 3), repeat=3):
                lhs = sum(a*x for a, x in zip(coefficients, point)) - 1
                rhs = point[0] - 2*point[1] + 4
                expected = {'<=': lhs <= rhs, '>=': lhs >= rhs, '==': lhs == rhs}[relation]
                dense = sum(a*x for a, x in zip(row[0], point))
                got = {'<=': dense <= row[2], '>=': dense >= row[2], '==': dense == row[2]}[relation]
                assert got == expected
                truth_checks += 1
            probes.append(expression)
    handwritten = [
        ('(2+3)*(x0+1)<=9', [[5,0,0], '<=', 4]),
        ('-(x0-2*x2)+1>=-x1-3', [[-1,1,2], '>=', -4]),
        ('7>=3*x0+2*x1', [[-3,-2,0], '>=', -7]),
        ('x0+x_0+x[0]-x1≤2', [[3,-1,0], '<=', 2]),
        ('x[2]≥1', [[0,0,1], '>=', 1]),
        ('x2=1', [[0,0,1], '==', 1]),
        ('2*(3*(x0+1)-x2)<=17', [[6,0,-2], '<=', 11]),
    ]
    for text, expected in handwritten:
        assert compile_constraint(text, 3) == expected
    forbidden = [
        'f(x0)<=1', 'x0.real<=1', '[x0][0]<=1', 'x[1+1]<=1', 'x[-1]<=1',
        'x[True]<=1', 'x[0.0]<=1', 'x0*x1<=1', '(x0-x0)*x1<=1', '0*x0*x1<=1',
        'x0**2<=1', 'x0/2<=1', 'x0//2<=1', 'x0%2<=1', 'x0<<1<=1', '~x0<=1',
        'x0<=True', 'x0<=1.0', 'x0<=1j', 'x0<1', 'x0!=1', '0<=x0<=1',
        'x0<=1 and x1<=1', 'x0<=1; x1<=1', 'x0<=1 #hidden', 'x0<=1\nx1<=1',
        '(lambda: x0)()<=1', '(x0:=1)<=1', '(x for x in [0])==0', 'x01<=1',
        'y0<=1', 'x3<=1', 'x0+...<=1', 'x0<=None', 'x0<=b"1"',
        'x0' + '+1'*200 + '<=1', '9'*300 + '*x0<=1', 'x0<=1' + ' '*4096,
    ]
    for text in forbidden:
        try:
            compile_constraint(text, 3)
        except ValueError:
            pass
        else:
            raise AssertionError('Forbidden expression accepted: ' + text)
    # Final frozen bounds are a parse constraint, after exact cancellation.
    assert parse_proposal(json.dumps(proposal(['10001*x0-x0<=10000'])), 3)['valid']
    assert not parse_proposal(json.dumps(proposal(['10001*x0<=1'])), 3)['valid']
    assert not parse_proposal(json.dumps(proposal(['x0<=10001'])), 3)['valid']
    mixed = proposal(['x0+x1<=1', [[0,0,1], '>=', 1]])
    parsed = parse_proposal(json.dumps(mixed), 3)
    assert parsed['valid'] and parsed['authored_model'] == mixed
    assert parsed['model']['objective'] == mixed['objective']
    assert parsed['model']['constraints'][1] == mixed['constraints'][1]
    assert len(parsed['model']['constraints']) == len(mixed['constraints'])
    legacy = [json.dumps(proposal([[[1,1,0], '<=', 1]])), 'not JSON',
              json.dumps(proposal([[[1,1], '<=', 1]])), '{"variables":[],"variables":[]}']
    for raw in legacy:
        assert parse_proposal(raw, 3) == parse_model(raw, 3)
    # Reuse the independent reviewer translation only as an audit input.
    spec = importlib.util.spec_from_file_location('independent_dense_audit', 'research/c15-code-audit.py')
    independent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(independent)
    base = Path('runs/20261114-c15-formulation-repair')
    cases = {r['id']:r for split in ('dev','test') for r in json.loads((base/(split+'_cases.json')).read_text())}
    labels = json.loads((base/'private_gold.review.json').read_text())
    expected_domains = {r['id']:r for r in json.loads(Path('research/c15-annotation-oracle/raw.json').read_text())['cases']}
    canonical_checks = []
    for label in labels:
        data = cases[label['id']]['data']
        dense = independent.encode(data, label['constraints'])
        authored = copy.deepcopy(dense)
        authored['constraints'] = ['+'.join('(%s)*x%s' % (a,i) for i,a in enumerate(coeffs)) + op + str(rhs)
                                  for coeffs,op,rhs in dense['constraints']]
        parsed = parse_proposal(json.dumps(authored), data['n'])
        assert parsed['valid'] and parsed['model'] == dense and parsed['authored_model'] == authored
        table = independent.independent_table(parsed['model'])
        masks = sorted(sum(bit<<i for i,bit in enumerate(x)) for x,(f,_) in table.items() if f)
        assert masks == expected_domains[label['id']]['feasible_masks']
        assert verify_model(data, label['constraints'], parsed)['faithful']
        canonical_checks.append(dict(id=label['id'], feasible_count=len(masks), authored_rows=len(authored['constraints'])))
    # A real controller with an injected response function, labelled software only.
    fixture = output/'loop-fixture'
    fixture.mkdir()
    case = dict(id='loop-software', intention='At least one selected, edge exclusion, budget two.',
                data=dict(n=2,weights=[3,2],costs=[2,1],edges=[[0,1]]))
    contract = dict(budget=2,min_count=1,max_count=None,required=[],forbidden=[],implications=[])
    write(fixture/'cases.json', [dict(case, private_incidental='must be stripped')])
    write(fixture/'labels.json', [dict(id=case['id'],constraints=contract,private_gold_marker='must not pass')])
    instructions='Software fixture instructions.'
    (fixture/'instructions.txt').write_text(instructions)
    good=proposal(['x0+x1<=1','2*x0+x1<=2','x0+x1>=1'],n=2,objective=[3,2])
    bad=proposal([],n=2,objective=[3,2])
    calls=[]
    def generate(**call):
        calls.append(call['phase'])
        assert call['case'] == case and 'gold_path' not in call
        assert json.loads(call['cases_path'].read_text()) == [case]
        if len(calls)>1:
            minimal=json.loads(call['feedback_path'].read_text())[case['id']]
            validate_feedback(minimal,2)
            assert minimal['kind']=='counterexamples'
        return dict(id=case['id'],raw_response=json.dumps(bad if len(calls)==1 else good))
    result=run_loop(fixture/'cases.json',fixture/'labels.json',case['id'],fixture/'instructions.txt',
                    output/'loop-results',max_repairs=3,generator=generate)
    assert calls==['initial','guided'] and result['status']=='exact' and result['objective']==3
    assert result['inference_mode']=='injected_software_fixture'
    # Characterize the stated trace-authentication limit, without claiming a real run.
    weak_record=dict(id=case['id'],raw_response=json.dumps(good),phase='guided',
                     output_tokens=385,generated_token_ids=[1]*385,messages=[
                         dict(role='system',content=instructions),
                         dict(role='user',content=json.dumps(dict(intention=case['intention'],data=case['data']))),
                         dict(role='assistant',content='prior model'),dict(role='user',content='prior oracle feedback')])
    assert _validate_record(weak_record,case,instructions,real=True)['valid']
    write(output/'raw.json',dict(
        status='finite_algebra_and_software_checks_passed',evidence_kind='NO LLM PERFORMANCE',
        generated_affine_rows=len(probes),integer_truth_evaluations=truth_checks,
        hand_computable_rows=len(handwritten),forbidden_expressions_rejected=len(forbidden),
        legacy_results_unchanged=len(legacy),reviewer_case_compilations=canonical_checks,
        loop=result,known_boundary_limitations=['Loop initial trace validation currently accepts a guided trace and token count 385; source authentication/caps need external checking.'],
        scope='Exact affine algebra and finite oracle-relative domains; audit-only encodings never enter inference.'))
    print('Exact affine/frontend and injected-loop software audit passed; trace reuse boundary limitation recorded.')


if __name__=='__main__':
    main()
