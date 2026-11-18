"""Audit saved local-model records and scores, without importing model libraries."""
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def need(value,message):
    if not value:raise ValueError(message)


def rows(path):return [json.loads(s) for s in path.read_text().splitlines()]


def verify_manifest(path):
    data=json.loads(path.read_text());need(data['run']['status']=='completed','unsuccessful manifest '+str(path))
    for row in data['input_artifacts']:
        digest=hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()
        need(digest==row['sha256']==row['sha256_after'],'stale input '+row['path'])
    for row in data['outputs']:
        need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'changed output '+row['path'])


def numeric(result):
    if result['status'] not in ('accepted','solved'):return
    problem=result['problem'];solution=result['solution']
    if problem['family']=='mis':
        feasible=[];n=problem['n']
        for size in range(n+1):
            for subset in itertools.combinations(range(n),size):
                if all(not (i in subset and j in subset) for i,j in problem['edges']):
                    feasible.append((sum(problem['weights'][i] for i in subset),subset))
        best=max(x[0] for x in feasible)
        expected={tuple(int(i in subset) for i in range(n)) for value,subset in feasible if value==best}
        need({tuple(x) for x in solution['solutions']}==expected,'solution set mismatch')
    else:
        a,b,p=problem['a'],problem['b'],problem['phi']
        expected=math.cos(a)**2*math.cos(b)**2+math.sin(a)**2*math.sin(b)**2-2*math.cos(a)*math.sin(a)*math.cos(b)*math.sin(b)*math.cos(p)
        probabilities=solution['probabilities']
        need(len(probabilities)==2 and abs(sum(probabilities)-1)<1e-12,'normalization')
        need(max(abs(probabilities[0]-expected),abs(probabilities[1]-(1-expected)))<1e-12,'optical oracle')
    route=result.get('route',{})
    need(route.get('hardware_readiness')=='unverified' and route.get('qpu_submitted') is False,'hardware overclaim')


def check_scores(directory,flat):
    data=rows(directory/'raw.jsonl');metrics=json.loads((directory/'metrics.json').read_text())
    flattened=data if flat else [{'id':r['id'],'method':k,'gold':r['gold'],'result':v} for r in data for k,v in r['results'].items()]
    for method,counts in metrics['methods'].items():
        subset=[r for r in flattened if r['method']==method]
        observed={k:0 for k in ('accepted_supported','false_accept','false_abstention','correct_abstention')}
        for row in subset:
            accepted=row['result']['status'] in ('accepted','solved');supported=row['gold']['expected_action']=='propose'
            key=('accepted_supported' if supported else 'false_accept') if accepted else ('false_abstention' if supported else 'correct_abstention')
            observed[key]+=1;numeric(row['result'])
        need(len(subset)==counts['observed'],'observed count')
        need(all(counts[k]==v for k,v in observed.items()),'aggregate '+method)
        accepted=counts['accepted_supported']+counts['false_accept']
        expected=counts['false_accept']/accepted if accepted else None
        need(counts['risk_among_accepts']==expected,'risk denominator')


def main():
    a=ROOT/'runs/20261113-c08-local-agent';b=ROOT/'runs/20261113-c09-heldout-guard';c=ROOT/'runs/20261113-c10-regression-release'
    groups_a={r['group_id'] for r in json.loads((a/'cases.json').read_text())};groups_b={r['group_id'] for r in json.loads((b/'cases.json').read_text())}
    need(not groups_a & groups_b and len(groups_a)==len(groups_b)==8,'group leakage')
    cases_a={r['id']:r for r in json.loads((a/'cases.json').read_text())};cases_b={r['id']:r for r in json.loads((b/'cases.json').read_text())}
    need(not set(cases_a)&set(cases_b) and len(cases_a)==len(cases_b)==16,'case leakage')
    total=0
    for cycle,cases,arms in [(a,cases_a,('alone','documented')),(b,cases_b,('nonredundant',))]:
        generated=rows(cycle/'generation/raw.jsonl');meta=json.loads((cycle/'generation/generation.json').read_text())
        need(len(generated)==len(cases)*len(arms)==meta['generation_calls_completed'],'generation count')
        need({(r['id'],r['arm']) for r in generated}=={(i,arm) for i in cases for arm in arms},'missing/duplicate generation')
        need(sum(r['input_tokens'] for r in generated)==meta['input_tokens'],'input token count')
        need(sum(r['output_tokens'] for r in generated)==meta['output_tokens'],'output token count')
        for row in generated:
            need(row['messages'][1]['content']==json.dumps(cases[row['id']]['request'],ensure_ascii=False),'model input changed')
            need(row['finish_reason']=='eos','truncation or unexplained stop')
        need(meta['model']=='Qwen/Qwen2.5-0.5B-Instruct' and meta['network_during_inference'] is False,'model/provenance')
        verify_manifest(cycle/'generation/manifest.json');verify_manifest(cycle/'results/manifest.json')
        check_scores(cycle/'results',cycle==a);total+=len(generated)
    for subdir in ('results','results-v4'):
        verify_manifest(c/subdir/'manifest.json');check_scores(c/subdir,False)
    final=json.loads((c/'results-v4/metrics.json').read_text())['methods']['guarded']
    need(final['accepted_supported']==7 and final['false_accept']==0,'development regression result')
    # Preserve the primary held-out residual error, not replaced by regression.
    primary=json.loads((b/'results/metrics.json').read_text())['methods']['guarded']
    need(primary['accepted_supported']==5 and primary['false_accept']==1,'primary result overwritten')
    for record in json.loads((c/'cli-integration.json').read_text())['records']:
        need(record['raw_response_reproduced_exactly'] and record['exit_code']==record['expected_exit_code'],'CLI v3 replay')
    last=json.loads((c/'cli-integration-v4.json').read_text())
    need(last['raw_response_reproduced_exactly'] and last['pipeline_status']=='abstain','CLI v4 replay')
    acquired=json.loads((ROOT/'runs/20261113-c07-public-traces/public-acquisition.json').read_text())
    for row in acquired['files']:
        need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'changed public source')
    print('OK:',total,'real primary generations on32unique cases, disjoint group stages, token totals, finite numerical solutions, scores and manifests. Three exact raw-text CLI replays. Primary held-out errors preserved; v4 is development only.')


if __name__=='__main__':main()
