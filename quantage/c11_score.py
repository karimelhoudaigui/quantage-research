"""Offline C11 scoring. Gold is read here, never by inference or controllers."""
import argparse
import hashlib
import json
from pathlib import Path
import time

from .compact_agent import TASKS
from .compact_v2 import parse_v2
from .compact_v4 import execute_v4
from .contracts import verify_external
from .core import (MIS_INTENT, PHOTO_INTENT, understand, formulate,
                   choose_solver, solve_qubo, optical_probabilities, pipeline)
from .transferstudy import keyword_pipeline


def agent(request, parsed, numerical):
    """Common schema/data boundary; the numerical check is a real ablation."""
    if not parsed['valid']:
        return {'status': 'abstain', 'stage': 'format', 'reason': parsed['reason']}
    proposal = parsed['proposal']
    if proposal['action'] == 'abstain':
        return {'status': 'abstain', 'stage': 'model_abstention'}
    try:
        family = next(f for f, t in TASKS.items() if t == proposal['task'])
        intent = MIS_INTENT if family == 'mis' else PHOTO_INTENT
        problem = understand({'intent': intent, 'data': request['data']})
        model = formulate(problem)
        verification = verify_external(problem, model) if numerical else {'valid': None, 'stage': 'not_applied'}
        if numerical and not verification['valid']:
            return {'status': 'abstain', 'stage': 'numeric', 'verification': verification}
        solution = solve_qubo(model) if family == 'mis' else {'probabilities': optical_probabilities(model)}
        return {'status': 'accepted', 'stage': 'numeric' if numerical else 'unchecked',
                'task': proposal['task'], 'problem': problem, 'formulation': model,
                'verification': verification, 'solution': solution, 'route': choose_solver(problem),
                'semantic_certificate': False}
    except (ValueError, TypeError, KeyError, OverflowError) as exc:
        return {'status': 'abstain', 'stage': 'data_contract', 'reason': str(exc)}


def direct(parsed):
    if not parsed['valid']:
        return {'status': 'abstain', 'stage': 'format'}
    proposal = parsed['proposal']
    return {'status': 'decision_accept' if proposal['action'] == 'propose' else 'abstain',
            'stage': 'model_decision_only', 'task': proposal['task'],
            'execution_performed': False}


def complete(request, primary, secondary):
    """Two context-isolated real proposals, followed by frozen checks/local route."""
    if not secondary['valid'] or not primary['valid']:
        return {'status': 'abstain', 'stage': 'consensus_format'}
    a, b = primary['proposal'], secondary['proposal']
    if a['action'] != 'propose' or b['action'] != 'propose' or a['task'] != b['task']:
        return {'status': 'abstain', 'stage': 'consensus_disagreement'}
    result = execute_v4(request, primary, True)
    if result['status'] == 'accepted':
        # The hardware role grants local execution only. No QPU certificate.
        route = result['route']
        if route.get('hardware_readiness') != 'unverified' or route.get('qpu_submitted') is not False:
            raise ValueError('unexpected hardware claim')
        result['task'] = a['task']
        result['architecture'] = 'two real intent proposals, deterministic formalization/formulation, lexical/numerical checks, local documentary route'
    return result


def counts():
    return dict(observed=0, supported=0, unsupported=0, accepted_correct=0,
                accepted_wrong=0, accepted_unsupported=0, accepted_wrong_task_supported=0,
                abstained_supported=0, abstained_unsupported=0, format_refusals=0,
                semantic_wrong_with_numeric_certificate=0)


def accepted(result):
    return result['status'] in ('accepted', 'solved', 'decision_accept')


def accumulate(target, label, result):
    support = label['expected_action'] == 'propose'
    target['observed'] += 1
    target['supported' if support else 'unsupported'] += 1
    is_accepted = accepted(result)
    correct = support and result.get('task') == label['expected_task']
    if is_accepted:
        target['accepted_correct' if correct else 'accepted_wrong'] += 1
        target['accepted_unsupported'] += int(not support)
        target['accepted_wrong_task_supported'] += int(support and not correct)
        target['semantic_wrong_with_numeric_certificate'] += int(not correct and result.get('verification', {}).get('valid') is True)
    else:
        target['abstained_supported' if support else 'abstained_unsupported'] += 1
    target['format_refusals'] += int(result.get('stage') in ('format', 'consensus_format'))


def ratios(target):
    result = dict(target)
    total = target['accepted_correct'] + target['accepted_wrong']
    result['coverage_all'] = total / target['observed'] if target['observed'] else None
    result['recall_supported'] = target['accepted_correct'] / target['supported'] if target['supported'] else None
    result['risk_among_accepted'] = target['accepted_wrong'] / total if total else None
    return result


def load_responses(path, public):
    if path is None:
        return {}
    result = {}
    for line in path.read_text().splitlines():
        row = json.loads(line)
        if row['id'] not in public or row['id'] in result:
            raise ValueError('unknown or duplicated generation')
        request = public[row['id']]['request']
        if row['messages'][1]['content'] != json.dumps(request, ensure_ascii=False):
            raise ValueError('generation/public input differs')
        if parse_v2(row['raw_response']) != row['parsed']:
            raise ValueError('saved parser result changed')
        result[row['id']] = row
    return result


def hypothesis(base, guarded, fraction_errors, fraction_correct):
    if base['accepted_wrong'] == 0 or base['accepted_correct'] == 0:
        return {'status': 'unresolved', 'reason': 'zero errors or zero correct acceptances in reference arm'}
    error_reduction = 1 - guarded['accepted_wrong'] / base['accepted_wrong']
    retention = guarded['accepted_correct'] / base['accepted_correct']
    return {'status': 'supported_in_finite_test' if error_reduction >= fraction_errors and retention >= fraction_correct else 'not_supported_in_finite_test',
            'error_reduction': error_reduction, 'correct_acceptance_retention': retention,
            'required_error_reduction': fraction_errors, 'required_correct_retention': fraction_correct}


def score(cases_path, gold_path, primary_path, secondary_path, output):
    started = time.perf_counter()
    cases = json.loads(cases_path.read_text())
    labels = json.loads(gold_path.read_text())
    public = {x['id']: x for x in cases}
    gold = {x['id']: x for x in labels}
    if len(public) != len(cases) or len(gold) != len(labels) or set(public) != set(gold):
        raise ValueError('duplicate or missing public/gold IDs')
    groups = {}
    for i, label in gold.items():
        if label.get('expected_action') not in ('propose', 'abstain') or label.get('family') not in TASKS:
            raise ValueError('unknown gold action/family')
        expected = TASKS[label['family']] if label['expected_action'] == 'propose' else None
        if label.get('expected_task') != expected or label.get('group_id') != public[i]['group_id']:
            raise ValueError('gold task/group mismatch')
        family = groups.setdefault(label['group_id'], label['family'])
        if family != label['family']:
            raise ValueError('mixed-family group')
    primary = load_responses(primary_path, public)
    secondary = load_responses(secondary_path, public)
    output.mkdir(parents=True, exist_ok=True)
    if (output / 'raw.jsonl').exists() or (output / 'metrics.json').exists():
        raise ValueError('refuse to overwrite scores')
    totals, strata, rows, decisions = {}, {}, [], {}
    semantic_decisions = {'qwen': dict(observed=0, valid_format=0, faithful_action_and_task=0, valid_model_abstentions=0),
                          'smol': dict(observed=0, valid_format=0, faithful_action_and_task=0, valid_model_abstentions=0)}
    for case in cases:
        label = gold[case['id']]
        results = {}
        for name, method in (('strict', pipeline), ('keywords', keyword_pipeline)):
            result = method(case['request'])
            if result['status'] == 'solved':
                result['task'] = TASKS[result['problem']['family']]
            results[name] = result
        for model_name, responses in (('qwen', primary), ('smol', secondary)):
            if case['id'] not in responses:
                continue  # Missing observations are not model abstentions.
            parsed = responses[case['id']]['parsed']
            diagnostic = semantic_decisions[model_name]
            diagnostic['observed'] += 1
            diagnostic['valid_format'] += int(parsed['valid'])
            if parsed['valid']:
                p = parsed['proposal']
                diagnostic['faithful_action_and_task'] += int(p['action'] == label['expected_action'] and p['task'] == label['expected_task'])
                diagnostic['valid_model_abstentions'] += int(p['action'] == 'abstain')
            results[model_name + '_direct'] = direct(parsed)
            results[model_name + '_unchecked'] = agent(case['request'], parsed, False)
            results[model_name + '_numeric'] = agent(case['request'], parsed, True)
            result = execute_v4(case['request'], parsed, True)
            if result['status'] == 'accepted':
                result['task'] = parsed['proposal']['task']
            results[model_name + '_semantic'] = result
        if case['id'] in primary and case['id'] in secondary:
            results['complete'] = complete(case['request'], primary[case['id']]['parsed'], secondary[case['id']]['parsed'])
        for name, result in results.items():
            target = totals.setdefault(name, counts())
            accumulate(target, label, result)
            for key in ('family', 'language', 'changed_clause'):
                value = label.get(key, 'unknown')
                by_value = strata.setdefault(key, {}).setdefault(value, {}).setdefault(name, counts())
                accumulate(by_value, label, result)
            decisions[(case['id'], name)] = result
        rows.append({'id': case['id'], 'group_id': case['group_id'], 'gold': label, 'results': results})
    paired = {}
    for model_name in ('qwen', 'smol'):
        pairs = dict(observed=0, removed_wrong=0, removed_correct=0, added_acceptance=0, numerical_decision_changes=0)
        for case in cases:
            i = case['id']
            if (i, model_name + '_numeric') not in decisions:
                continue
            a, b = decisions[(i, model_name + '_numeric')], decisions[(i, model_name + '_semantic')]
            faithful = gold[i]['expected_action'] == 'propose' and a.get('task') == gold[i]['expected_task']
            pairs['observed'] += 1
            pairs['removed_wrong'] += int(accepted(a) and not accepted(b) and not faithful)
            pairs['removed_correct'] += int(accepted(a) and not accepted(b) and faithful)
            pairs['added_acceptance'] += int(not accepted(a) and accepted(b))
            pairs['numerical_decision_changes'] += int(accepted(a) != accepted(decisions[(i, model_name + '_unchecked')]))
        paired[model_name] = pairs
    with (output / 'raw.jsonl').open('x') as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False) + '\n')
    qn, qs = totals.get('qwen_numeric', counts()), totals.get('qwen_semantic', counts())
    h3 = {'status': 'unresolved', 'reason': 'complete model matrix or nonzero reference correct count unavailable'}
    if len(primary) == len(secondary) == len(cases) and qs['accepted_correct']:
        full = totals['complete']
        h3 = {'status': 'supported_in_finite_test' if full['accepted_wrong'] < qs['accepted_wrong'] and full['accepted_correct'] / qs['accepted_correct'] >= .8 else 'not_supported_in_finite_test',
              'wrong_reduction_absolute': qs['accepted_wrong'] - full['accepted_wrong'],
              'correct_acceptance_retention': full['accepted_correct'] / qs['accepted_correct']}
    h1 = hypothesis(qn, qs, .5, .9)
    if len(primary) != len(cases):
        h1['observed_subset_result'] = h1['status']
        h1['status'] = 'unresolved_partial_generation'
    metrics = {'cases': len(cases), 'groups': len({r['group_id'] for r in cases}),
               'observed_generations': {'qwen': len(primary), 'smol': len(secondary)},
               'methods': {k: ratios(v) for k, v in totals.items()},
               'strata': {k: {v: {m: ratios(c) for m, c in methods.items()} for v, methods in values.items()} for k, values in strata.items()},
               'model_semantic_decisions': semantic_decisions, 'paired': paired,
               'hypotheses': {'H1': h1,
                              'H2': {'status': 'numeric_sufficiency_refuted_by_real_counterexample' if qn['semantic_wrong_with_numeric_certificate'] else 'unresolved',
                                     'observed_qwen_counterexamples': qn['semantic_wrong_with_numeric_certificate']},
                              'H3': h3},
               'generation_costs': {name: {key: sum(r[key] for r in responses.values()) for key in ('input_tokens', 'output_tokens', 'wall_seconds', 'cpu_seconds')} for name, responses in (('qwen', primary), ('smol', secondary))},
               'scoring_wall_seconds': time.perf_counter() - started,
               'non_claims': ['no population confidence interval for author-crafted convenience corpus', 'direct measures decisions, not execution', 'numeric ablation may be null because formulation is deterministic', 'lexical semantic checks are not universal certificates', 'no QPU or physical compatibility established']}
    (output / 'metrics.json').write_text(json.dumps(metrics, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'methods': metrics['methods'], 'hypotheses': metrics['hypotheses']}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cases', type=Path, required=True)
    parser.add_argument('--gold', type=Path, required=True)
    parser.add_argument('--primary', type=Path, required=True)
    parser.add_argument('--secondary', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    score(a.cases, a.gold, a.primary, a.secondary, a.output)
