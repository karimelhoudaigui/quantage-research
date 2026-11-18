"""Audit C05/C06 records, treating all embedded replay sources as data."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from quantage.boundarystudy import decode
from quantage.contracts import verify_external


def require(condition,message):
    if not condition:raise ValueError(message)


def main():
    c05=ROOT/'runs/20261113-c05-semantic-contracts'
    audit=json.loads((c05/'external-contract-audit.json').read_text())
    saved={r['id']:r for r in audit['recorded_run']['results']}
    require(len(saved)==len(audit['cases'])==109,'independent case count')
    for path,before in audit['recorded_run']['input_hashes_before'].items():
        require(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==before,'stale reviewed input '+path)
        require(audit['recorded_run']['input_hashes_after'][path]==before,'changed reviewed input '+path)
    for raw in audit['cases']:
        c=decode(raw);result=verify_external(c['problem'],c['proposal'],c['tolerance'])
        require(result['valid']==c['expected_valid'] and result['stage']==c['expected_stage'],'independent expectation '+c['id'])
        require(result==saved[c['id']]['result'],'independent replay '+c['id'])
    rows=[json.loads(s) for s in (c05/'results/raw.jsonl').read_text().splitlines()]
    m=json.loads((c05/'results/metrics.json').read_text())
    require(len(rows)==m['cases']==73,'C05 row count')
    proposals=[r for r in rows if 'external' in r]
    require(len(proposals)==m['proposal_cases']==67,'C05 proposal count')
    for method in ('legacy','external'):
        require(sum(r[method]['valid'] and not r['expected_valid'] for r in proposals)==m[method]['false_accept'],'C05 false accepts')
        require(sum(not r[method]['valid'] and r['expected_valid'] for r in proposals)==m[method]['false_reject'],'C05 false rejects')
    c06=ROOT/'runs/20261113-c06-native-agents'
    public=json.loads((c06/'public_cases.json').read_text());gold=json.loads((c06/'private_gold.v2.json').read_text())
    old=json.loads((c06/'private_gold.json').read_text());revision=json.loads((c06/'annotation-revision.json').read_text())
    require(len(public)==len(gold)==32,'C06 corpus count')
    require({r['id'] for r in public}=={r['id'] for r in gold},'C06 label coverage')
    require(sum(g['expected_action']=='propose' for g in gold)==19,'C06 supported count')
    changed=[g['id'] for a,g in zip(old,gold) if a!=g]
    require(changed==[revision['id']],'only adjudicated label changed')
    for file,key in [('private_gold.json','old_gold_sha256'),('private_gold.v2.json','new_gold_sha256')]:
        require(hashlib.sha256((c06/file).read_bytes()).hexdigest()==revision[key],'adjudication hash')
    raw=[json.loads(s) for s in (c06/'results-baselines/raw.jsonl').read_text().splitlines()]
    metrics=json.loads((c06/'results-baselines/metrics.json').read_text())
    require(len(raw)==32 and metrics['agent_cases_evaluated']==0,'C06 missing native cases')
    for method,counts in metrics['methods'].items():
        actual={k:0 for k in ('accepted_supported','false_accept','false_abstention','correct_abstention')}
        for row in raw:
            accepted=row['results'][method]['result']['status'] in ('accepted','solved')
            supported=row['gold']['expected_action']=='propose'
            key=('accepted_supported' if supported else 'false_accept') if accepted else ('false_abstention' if supported else 'correct_abstention')
            actual[key]+=1
        require(all(counts[k]==v for k,v in actual.items()),'C06 aggregate '+method)
    print('OK: C05 independent 109-case replay, 73-case metrics and C06 32-case labels/baselines; no embedded code executed, no native performance imputed.')


if __name__=='__main__':main()
