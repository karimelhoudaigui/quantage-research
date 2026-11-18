"""Reaggregate C11 from immutable records, no model/scorer imports."""
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'runs/20261113-c11-frozen-transfer'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def manifest(path):
    d = json.loads(path.read_text())
    need(d['run']['status'] == 'completed', 'incomplete run ' + str(path))
    for r in d['input_artifacts']:
        need(hashlib.sha256((ROOT / r['path']).read_bytes()).hexdigest() == r['sha256'] == r['sha256_after'], 'stale input ' + r['path'])
    for r in d['outputs']:
        need(hashlib.sha256((ROOT / r['path']).read_bytes()).hexdigest() == r['sha256'], 'stale output ' + r['path'])


def numerical(request, result):
    if result['status'] not in ('accepted', 'solved'):
        return
    p, solution, data = result['problem'], result['solution'], request['data']
    if p['family'] == 'mis':
        need(p['n'] == data['n'] and p['weights'] == data['weights'], 'altered graph/weights')
        need(sorted(sorted(e) for e in p['edges']) == sorted(sorted(e) for e in data['edges']), 'altered edges')
        states = []
        for bits in itertools.product((0, 1), repeat=data['n']):
            if all(not (bits[a] and bits[b]) for a, b in data['edges']):
                states.append((sum(w * b for w, b in zip(data['weights'], bits)), bits))
        best = max(v for v, unused in states)
        need({tuple(x) for x in solution['solutions']} == {s for v, s in states if v == best}, 'wrong MIS solution set')
    else:
        need(all(p[k] == data[k] for k in ('a', 'b', 'phi')), 'altered angles')
        a, b, phase = data['a'], data['b'], data['phi']
        expected = math.cos(a)**2 * math.cos(b)**2 + math.sin(a)**2 * math.sin(b)**2 - 2 * math.cos(a)*math.sin(a)*math.cos(b)*math.sin(b)*math.cos(phase)
        got = solution['probabilities']
        need(len(got) == 2 and abs(got[0] - expected) < 1e-12 and abs(got[1] - (1 - expected)) < 1e-12, 'photon oracle mismatch')
    need(result['route']['hardware_readiness'] == 'unverified' and result['route']['qpu_submitted'] is False, 'false physical claim')


def main():
    public = {r['id']: r for r in json.loads((RUN / 'public_cases.json').read_text())}
    gold = {r['id']: r for r in json.loads((RUN / 'gold.json').read_text())}
    adjudication = json.loads((RUN / 'adjudication.json').read_text())
    for name, key in [('private_gold.author.json', 'author_sha256'), ('private_gold.review.json', 'review_sha256'), ('gold.json', 'gold_sha256')]:
        need(hashlib.sha256((RUN / name).read_bytes()).hexdigest() == adjudication[key], 'changed annotation')
    for filename in ('historical-snapshot.json', 'frozen-inputs.json'):
        for name, digest in json.loads((RUN / filename).read_text())['files'].items():
            need(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, 'changed history/frozen code ' + name)
    generations = {}
    for model, expected in [('qwen', 'Qwen/Qwen2.5-0.5B-Instruct'), ('smol', 'HuggingFaceTB/SmolLM2-135M-Instruct')]:
        directory = RUN / ('generation-' + model)
        records = read_rows(directory / 'raw.jsonl')
        meta = json.loads((directory / 'generation.json').read_text())
        need(len(records) == len(public) == meta['generation_calls_completed'] == 128, 'incomplete generation matrix')
        need({r['id'] for r in records} == set(public), 'missing/duplicate generation')
        need(meta['model'] == expected and meta['dtype'] == 'float32' and meta['network_during_inference'] is False, 'model identity/runtime')
        for key in ('input_tokens', 'output_tokens'):
            need(sum(r[key] for r in records) == meta[key], 'token aggregate')
        for r in records:
            need(r['messages'][1]['content'] == json.dumps(public[r['id']]['request'], ensure_ascii=False), 'changed model request')
            need(r['messages'][0]['content'] == (ROOT / 'runs/20261113-c09-heldout-guard/instructions.md').read_text(), 'changed prompt')
        need(not any('gold' in r['path'] for r in json.loads((directory / 'manifest.json').read_text())['input_artifacts']), 'gold declared as inference input')
        generations[model] = records
        manifest(directory / 'manifest.json')
    for suffix in ('results-primary', 'results'):
        directory = RUN / suffix
        manifest(directory / 'manifest.json')
        rows = read_rows(directory / 'raw.jsonl')
        metrics = json.loads((directory / 'metrics.json').read_text())
        need(len(rows) == 128 and {r['id'] for r in rows} == set(public), 'missing/duplicate scored rows')
        for method, counts in metrics['methods'].items():
            correct = wrong = no_supported = no_unsupported = observed = 0
            for row in rows:
                if method not in row['results']:
                    continue
                result = row['results'][method]
                need(row['gold'] == gold[row['id']], 'scoring changed gold')
                observed += 1
                supported = gold[row['id']]['expected_action'] == 'propose'
                is_accept = result['status'] in ('accepted', 'solved', 'decision_accept')
                faithful = supported and result.get('task') == gold[row['id']]['expected_task']
                correct += int(is_accept and faithful)
                wrong += int(is_accept and not faithful)
                no_supported += int(not is_accept and supported)
                no_unsupported += int(not is_accept and not supported)
                numerical(public[row['id']]['request'], result)
            need((observed, correct, wrong, no_supported, no_unsupported) == tuple(counts[k] for k in ('observed', 'accepted_correct', 'accepted_wrong', 'abstained_supported', 'abstained_unsupported')), 'counter mismatch ' + method)
            n = correct + wrong
            need(counts['risk_among_accepted'] == (wrong / n if n else None), 'risk denominator')
            need(counts['coverage_all'] == n / observed, 'coverage denominator')
        base, guarded = metrics['methods']['qwen_numeric'], metrics['methods']['qwen_semantic']
        h = metrics['hypotheses']['H1']
        need(h['error_reduction'] == 1 - guarded['accepted_wrong'] / base['accepted_wrong'], 'H1 error reduction')
        need(h['correct_acceptance_retention'] == guarded['accepted_correct'] / base['accepted_correct'], 'H1 retention')
        need(h['status'] == 'not_supported_in_finite_test', 'primary negative overwritten')
    need(sum(r['finish_reason'] == 'token_limit' for r in generations['smol']) == 106, 'truncations changed')
    print('OK: 256 actual generations/128 new cases, labels/frozen history, model identities/tokens, all decision counts and numerical outputs; H1 negative preserved. Self-audit of C11 results; prior independent annotations/protocol review only.')


if __name__ == '__main__':
    main()
