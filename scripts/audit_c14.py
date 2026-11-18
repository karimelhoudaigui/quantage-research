"""Audit partial C14 provenance without imputing a semantic benchmark."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'runs/20261113-c14-model-scale'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    base = ROOT / 'runs/20261113-c11-frozen-transfer'
    public = json.loads((base / 'public_cases.json').read_text())
    labels = {r['id']: r for r in json.loads((base / 'gold.json').read_text())}
    strata = {}
    for r in public:
        label = labels[r['id']]
        strata.setdefault((label['family'], label['language']), set()).add(r['group_id'])
    groups = {g for values in strata.values() for g in sorted(values)[:4]}
    expected = [r for r in public if r['group_id'] in groups]
    cases = json.loads((RUN / 'cases.json').read_text())
    need(cases == expected and len(cases) == 32 and len(groups) == 16, 'selection changed')
    need(json.loads((RUN / 'gold.json').read_text()) == [labels[r['id']] for r in cases], 'gold subset changed')
    first = sorted(cases, key=lambda r: r['id'])[0]['id']
    for directory in ('generation', 'generation-bfloat16', 'precision-bfloat16'):
        d = json.loads((RUN / directory / 'manifest.json').read_text())
        status = 'completed' if directory == 'precision-bfloat16' else 'failed'
        need(d['run']['status'] == status, 'recorded failure overwritten')
        for r in d['input_artifacts']:
            need(hashlib.sha256((ROOT / r['path']).read_bytes()).hexdigest() == r['sha256'] == r['sha256_after'], 'stale input')
        for r in d['outputs']:
            need(hashlib.sha256((ROOT / r['path']).read_bytes()).hexdigest() == r['sha256'], 'stale output')
    fp = json.loads((RUN / 'probe-float16.json').read_text())
    bf = json.loads((RUN / 'precision-bfloat16/result.json').read_text())
    need(fp['case_id'] == bf['case_id'] == first, 'different precision diagnostic prompt')
    need(fp['vocabulary_logits'] == bf['vocabulary_logits'] == 151936, 'different diagnostic dimensions')
    need(fp['nan_logits'] == 151936 and fp['finite_logits'] == 0, 'float16 observation')
    need(bf['finite_logits'] == 151936 and bf['nan_logits'] == bf['infinite_logits'] == 0, 'bfloat16 observation')
    for directory in ('generation', 'generation-bfloat16'):
        records = [json.loads(s) for s in (RUN / directory / 'raw.jsonl').read_text().splitlines()]
        need(len(records) == 1 and records[0]['id'] == first, 'partial count changed')
        if directory == 'generation':
            need(records[0]['raw_response'] == '!' * 128 and not records[0]['parsed']['valid'], 'failed precision output')
        else:
            need(records[0]['parsed']['valid'] and records[0]['output_tokens'] == 49 and records[0]['finish_reason'] == 'eos', 'bfloat16 partial record')
        need(not (RUN / directory / 'generation.json').exists(), 'unobserved final metadata synthesized')
    need(json.loads((RUN / 'completion.json').read_text())['status'] == 'blocked', 'incomplete comparison relabelled complete')
    need(not (RUN / 'results/metrics.json').exists(), 'partial observations given a full performance score')
    print('OK: C14 fixed matched subset, two failed/partial arms preserved, finite-vs-NaN diagnostics, one unique case, no missing-response imputations or H14 performance claim. Self-audit only.')


if __name__ == '__main__':
    main()
