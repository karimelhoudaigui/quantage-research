"""Reaggregate saved rows without importing the scientific implementation."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_run(name):
    directory = ROOT/'runs'/name/'results'
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest['run']['status'] != 'completed':
        raise ValueError('unsuccessful run '+name)
    for item in manifest['input_artifacts']:
        actual = hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()
        if actual != item['sha256'] or actual != item['sha256_after']:
            raise ValueError('stale input '+item['path'])
    for item in manifest['outputs']:
        if hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('modified output '+item['path'])
    rows = [json.loads(line) for line in (directory/'raw.jsonl').read_text().splitlines()]
    return rows, json.loads((directory/'metrics.json').read_text()), manifest


def require(value, message):
    if not value:
        raise ValueError(message)


def audit():
    rows, m, first = read_run('20261113-c01-foundation')
    require(len(rows) == m['mis']+m['photon'] == 1324, 'C01 count')
    require(len({r['id'] for r in rows}) == len(rows), 'C01 duplicate IDs')
    unique = len({json.dumps(r['request'], sort_keys=True) for r in rows})
    require(unique == 1319, 'C01 distinct input count')
    require(all(r['result']['status'] == 'solved' for r in rows), 'C01 failed row')
    mis = [r for r in rows if r['result']['problem']['family'] == 'mis']
    require(len(mis) == m['mis'] == 1199, 'C01 MIS count')
    require(sum(r.get('greedy_absolute_gap',0) > 0 for r in rows) == m['greedy_suboptimal'], 'C01 greedy count')
    require(max(r.get('greedy_absolute_gap',0) for r in rows) == m['max_greedy_absolute_gap'], 'C01 greedy gap')
    require(sum(r['result']['verification']['states_checked'] for r in mis) == m['states_checked'], 'C01 states')
    photons = [r for r in rows if r['result']['problem']['family'] == 'photon']
    require(max(r['result']['verification']['max_abs_error'] for r in photons) == m['max_probability_error'], 'C01 error')
    rows, m, _ = read_run('20261113-c02-formulation')
    require(len(rows) == sum(g['cases'] for g in m['groups'].values()) == 2225, 'C02 count')
    for key, group in m['groups'].items():
        family, mutation = key.split('/')
        sub = [r for r in rows if r['mutation'] == mutation and (r['proposal']['kind'] == 'qubo') == (family == 'mis')]
        require(len(sub) == group['cases'], 'C02 group count')
        require(sum(not r['equivalent_on_instance'] for r in sub) == group['effective'], 'C02 effective count')
        for method, counts in group['methods'].items():
            require(sum(r['accepted'][method] and not r['equivalent_on_instance'] for r in sub) == counts['false_accept'], 'C02 false accept')
            require(sum(not r['accepted'][method] and r['equivalent_on_instance'] for r in sub) == counts['false_reject'], 'C02 false reject')
            require(sum(not r['accepted'][method] for r in sub) == counts['rejected'], 'C02 rejected')
    rows, m, _ = read_run('20261113-c03-routing')
    require(len(rows) == m['cases'] == 20, 'C03 count')
    for method, counts in m['methods'].items():
        observed = dict.fromkeys(('tp','tn','fp','fn'),0)
        for r in rows:
            a, b = r['results'][method]['acceptable_recommendation'], r['case']['expected_acceptable']
            observed[('t' if a == b else 'f')+('p' if a else 'n')] += 1
        require(observed == counts, 'C03 confusion matrix')
    require(all(r['results']['guarded']['execution_permission'] != 'allowed_qpu' for r in rows), 'C03 QPU permission')
    rows, m, last = read_run('20261113-c04-transfer')
    require(len(rows) == m['cases'] == 24, 'C04 count')
    for method, counts in m['methods'].items():
        observed = dict.fromkeys(('correct_accepts','false_accepts','false_abstentions','correct_abstentions'),0)
        groups = {}
        certificates = 0
        for row in rows:
            a, b = row['results'][method]['status'] == 'solved', row['case']['contract_equivalent']
            key = ('correct_accepts' if b else 'false_accepts') if a else ('false_abstentions' if b else 'correct_abstentions')
            observed[key] += 1
            g = groups.setdefault(row['case']['group'], {'cases':0,'accepted':0})
            g['cases'] += 1; g['accepted'] += int(a)
            certificates += int(a and row['results'][method]['verification']['valid'])
        require(all(counts[k] == v for k,v in observed.items()), 'C04 metrics')
        require(groups == counts['groups'], 'C04 groups')
        require(certificates == counts['accepted_with_numerical_certificate'], 'C04 certificates')
    for path in ('quantage/core.py','quantage/verification.py','quantage/benchmark.py'):
        before = next(x['sha256'] for x in first['input_artifacts'] if x['path'] == path)
        after = next(x['sha256'] for x in last['input_artifacts'] if x['path'] == path)
        require(before == after, 'C04 engine not frozen')
    print('OK: four raw datasets reaggregated; recorded input/output hashes and frozen engine checked. C01: 1324 evaluations, 1319 distinct requests (5 repeated MIS). Self-audit only.')


if __name__ == '__main__':
    audit()
