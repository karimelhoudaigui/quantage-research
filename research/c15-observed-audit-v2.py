"""Audit observed C15 records without inference, author gold or scorer imports."""
import argparse
import datetime
import hashlib
import itertools
import json
import math
from pathlib import Path
import re

from tokenizers import Tokenizer


FIELDS={'formulation','variables','sense','objective','constraints'}
SCHEMA_MESSAGE='Invalid JSON or documented model schema. Rebuild a complete binary_ilp object with variables,sense,objective,constraints and explicit integer rows.'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def actual_shape(raw,n,algebraic):
    """Independent checker of forms actually observed; no arbitrary AST parser."""
    body=raw.strip();lines=body.split('\n')
    if len(lines)>=3 and lines[0] in ('```','```json') and lines[-1]=='```':
        body='\n'.join(lines[1:-1])
    try:
        model=json.loads(body)
    except (ValueError,TypeError):
        return None
    if type(model) is not dict or set(model)!=FIELDS or model['formulation']!='binary_ilp' or model['sense']!='max':
        return None
    if type(model['variables']) is not list or model['variables']!=list(range(n)) or any(type(x) is not int for x in model['variables']):
        return None
    if type(model['objective']) is not list or len(model['objective'])!=n or any(type(x) is not int or abs(x)>10000 for x in model['objective']):
        return None
    if type(model['constraints']) is not list or len(model['constraints'])>32:
        return None
    normalized=[]
    for row in model['constraints']:
        if algebraic and type(row) is str:
            # The sole observed valid proposal uses only these four pair rows.
            match=re.fullmatch(r'\s*x([0-9]+)\s*\+\s*x([0-9]+)\s*<=\s*([0-9]+)\s*',row)
            if not match:
                raise AssertionError('Observed string exceeds the independently checked actual syntax: '+row)
            a,b,rhs=map(int,match.groups());coeffs=[0]*n
            assert 0<=a<n and 0<=b<n
            coeffs[a]+=1;coeffs[b]+=1;row=[coeffs,'<=',rhs]
        if type(row) is not list or len(row)!=3:
            return None
        coefficients,op,rhs=row
        if type(coefficients) is not list or len(coefficients)!=n or any(type(x) is not int or abs(x)>10000 for x in coefficients):
            return None
        if type(op) is not str or op not in ('<=','>=','==') or type(rhs) is not int or abs(rhs)>10000:
            return None
        normalized.append(row)
    return dict(model,constraints=normalized)


def table(model):
    result={}
    for bits in itertools.product((0,1),repeat=len(model['variables'])):
        okay=True
        for coefficients,relation,rhs in model['constraints']:
            lhs=sum(coefficients[i]*bits[i] for i in range(len(bits)))
            okay &= {'<=':lhs<=rhs,'>=':lhs>=rhs,'==':lhs==rhs}[relation]
        result[bits]=(bool(okay),sum(model['objective'][i]*bits[i] for i in range(len(bits))))
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    output=parser.parse_args().output
    root=Path('runs/20261114-c15-formulation-repair')
    public={split:{r['id']:r for r in json.loads((root/(split+'_cases.json')).read_text())} for split in ('dev','test')}
    review=json.loads((root/'private_gold.review.json').read_text())
    assert digest(root/'private_gold.review.json')=='1bb31ff6323f79987c2d53a541b0738a625e56019475b02095169bcb8bfaa4e2'
    expected={r['id']:r for r in json.loads(Path('research/c15-annotation-oracle/raw.json').read_text())['cases']}
    checkpoint=Path('research/external/models/qwen2.5-0.5b-7ae5576')
    tokenizer=Tokenizer.from_file(str(checkpoint/'tokenizer.json'))
    eos_ids=json.loads((checkpoint/'generation_config.json').read_text())['eos_token_id']
    summaries={};valid_models={};source_checks={};timestamp_notes=[]
    for name,split,version,instruction_name in [
        ('dev-initial-v1','dev','v1','instructions.v1.txt'),
        ('dev-initial-v2','dev','v2','instructions.v2.txt'),
        ('test-initial-v2','test','v2','instructions.v2.txt')]:
        directory=root/name;records=load_rows(directory/'raw.jsonl')
        assert len({r['id'] for r in records})==len(records)
        assert {r['id'] for r in records}<=set(public[split])
        if split=='dev':assert {r['id'] for r in records}==set(public[split])
        instruction=(root/instruction_name).read_text()
        manifest=json.loads((directory/'manifest.json').read_text())
        assert '--gold' not in manifest['command'] and '--feedback' not in manifest['command'] and '--initial' not in manifest['command']
        if '--max-new-tokens' in manifest['command']:
            assert manifest['command'][manifest['command'].index('--max-new-tokens')+1]=='384'
        outputs=[]
        for artifact in manifest['outputs']:
            path=Path(artifact['path']);assert digest(path)==artifact['sha256']
            outputs.append(dict(path=str(path),hash_verified=True))
        sources=[]
        for artifact in manifest['input_artifacts']:
            assert artifact['sha256']==artifact['sha256_after']
            # Preserve annotation independence; author/reference files are not opened.
            if Path(artifact['path']).name in ('private_gold.author.json','gold.json','build_corpus.py','corpus-provenance.md'):
                sources.append(dict(path=artifact['path'],opened=False,reason='independent reviewer scope'))
            else:
                sources.append(dict(path=artifact['path'],current_hash_matches=digest(Path(artifact['path']))==artifact['sha256']))
        source_checks[name]=dict(run_status=manifest['run']['status'],outputs=outputs,inputs=sources)
        row_results=[]
        for record in records:
            case=public[split][record['id']];n=case['data']['n']
            assert record['phase']=='initial'
            assert record['seed']==int(hashlib.sha256(record['id'].encode()).hexdigest()[:8],16)%(2**32)
            messages=record['messages']
            assert len(messages)==2 and messages[0]==dict(role='system',content=instruction)
            assert messages[1]['role']=='user'
            assert json.loads(messages[1]['content'])==dict(intention=case['intention'],data=case['data'])
            prompt=''.join('<|im_start|>'+m['role']+'\n'+m['content']+'<|im_end|>\n' for m in messages)+'<|im_start|>assistant\n'
            assert hashlib.sha256(prompt.encode()).hexdigest()==record['prompt_sha256']
            assert len(tokenizer.encode(prompt).ids)==record['input_tokens']
            ids=record['generated_token_ids'];logps=record['generated_token_log_probabilities']
            assert type(record['output_tokens']) is int and 0<record['output_tokens']<=384
            assert type(record['input_tokens']) is int and 0<record['input_tokens']<=4096
            assert len(ids)==len(logps)==record['output_tokens'] and all(type(x) is int and x>=0 for x in ids)
            assert all(type(x) in (float,int) and math.isfinite(x) and x<=1e-7 for x in logps)
            assert math.isfinite(record['mean_generated_log_probability'])
            assert math.isclose(sum(logps)/len(logps),record['mean_generated_log_probability'],abs_tol=1e-12)
            assert tokenizer.decode(ids,skip_special_tokens=True)==record['raw_response']
            if record['finish_reason']=='eos':assert ids[-1] in eos_ids
            else:assert record['finish_reason']=='token_limit' and len(ids)==384
            independently_parsed=actual_shape(record['raw_response'],n,version=='v2')
            assert (independently_parsed is not None)==record['parsed']['valid']
            finite=None
            if independently_parsed is not None:
                assert independently_parsed==record['parsed']['model']
                values=table(independently_parsed)
                reference_masks=set(expected[record['id']]['feasible_masks'])
                wrong_f=wrong_v=0;witnesses=[]
                for bits,(f,v) in values.items():
                    ref_f=sum(bit<<i for i,bit in enumerate(bits)) in reference_masks
                    ref_v=sum(case['data']['weights'][i]*bits[i] for i in range(n))
                    wrong_f+=f!=ref_f;wrong_v+=v!=ref_v
                    if len(witnesses)<3:
                        if f!=ref_f:witnesses.append(dict(kind='feasibility',x=list(bits),expected_feasible=ref_f,proposed_feasible=f))
                        elif v!=ref_v:witnesses.append(dict(kind='objective',x=list(bits),expected_value=ref_v,proposed_value=v))
                finite=dict(assignments=2**n,feasibility_mismatches=wrong_f,objective_mismatches=wrong_v,
                            proposed_feasible_count=sum(f for f,v in values.values()),reference_feasible_count=len(reference_masks),
                            proposed_best=max((v for f,v in values.values() if f),default=None),reference_best=expected[record['id']]['max_weight'],
                            witnesses=witnesses,faithful=wrong_f==wrong_v==0)
                valid_models[record['id']]=dict(model=independently_parsed,finite=finite)
            row_results.append(dict(id=record['id'],schema_valid=record['parsed']['valid'],finite=finite,
                                    input_tokens=record['input_tokens'],output_tokens=record['output_tokens'],
                                    finish_reason=record['finish_reason'],wall_seconds=record['wall_seconds'],cpu_seconds=record['cpu_seconds']))
        summary=dict(observed=len(records),planned=len(public[split]),missing_ids=sorted(set(public[split])-{r['id'] for r in records}),
                     schema_valid=sum(r['schema_valid'] for r in row_results),faithful=sum(bool(r['finite'] and r['finite']['faithful']) for r in row_results),
                     eos=sum(r['finish_reason']=='eos' for r in row_results),token_limit=sum(r['finish_reason']=='token_limit' for r in row_results),
                     completed_row_cost={k:sum(r[k] for r in records) for k in ('input_tokens','output_tokens','wall_seconds','cpu_seconds')},
                     wrapper_seconds=manifest['run']['runtime_seconds'],exit_status=manifest['run']['exit_status'],records=row_results)
        if (directory/'generation.json').exists():
            meta=json.loads((directory/'generation.json').read_text())
            assert meta['status']=='completed' and meta['completed']==len(records)==8
            assert meta['revision']=='7ae557604adf67be50417f59c2c2f167def9a775' and meta['model']=='Qwen/Qwen2.5-0.5B-Instruct'
            assert (meta['python'],meta['torch'],meta['transformers'])==('3.9.6','2.8.0','4.45.2')
            assert meta['dtype']=='float32' and meta['device']=='cpu' and meta['threads']==4
            assert meta['sampling']==dict(temperature=.2,top_p=1.,top_k=50)
            assert meta['max_new_tokens']==384 and meta['max_input_tokens']==4096
            for key in ('input_tokens','output_tokens'):assert meta[key]==summary['completed_row_cost'][key]
            summary['generation_metadata']=meta
            start=datetime.datetime.fromisoformat(manifest['run']['started_at'])
            stamp=datetime.datetime.fromisoformat(meta['recorded_at_utc'])
            delta=(stamp-start).total_seconds()-manifest['run']['runtime_seconds']
            if abs(delta)>30:timestamp_notes.append(dict(phase=name,utc_discrepancy_seconds=delta,interpretation='UTC chronology and monotonic duration disagree; cause not established.'))
        else:
            assert name=='test-initial-v2' and manifest['run']['status']=='failed' and manifest['run']['exit_status']==-15
            summary['generation_metadata']='missing; not synthesized'
        summaries[name]=summary
    assert summaries['dev-initial-v1']['observed']==8 and summaries['dev-initial-v1']['schema_valid']==0
    assert summaries['dev-initial-v2']['observed']==8 and summaries['dev-initial-v2']['schema_valid']==1
    assert set(valid_models)=={'31d8b6f0'}
    finite=valid_models['31d8b6f0']['finite']
    assert finite['feasibility_mismatches']==23 and finite['objective_mismatches']==0
    assert finite['proposed_feasible_count']==32 and finite['reference_feasible_count']==9
    assert finite['proposed_best']==31 and finite['reference_best']==17
    minimal=json.loads((root/'dev-feedback-v2/minimal.json').read_text())
    assert set(minimal)==set(public['dev'])
    for cid,entry in minimal.items():
        expected_feedback=dict(kind='counterexamples',witnesses=finite['witnesses']) if cid=='31d8b6f0' else dict(kind='schema',message=SCHEMA_MESSAGE)
        assert entry==expected_feedback
    metrics=json.loads((root/'dev-score-v2/metrics.json').read_text())
    method=metrics['methods']['initial']
    assert metrics['cases']==8 and metrics['H15']==dict(status='development_only')
    assert (method['observed'],method['schema_valid'],method['faithful'],method['feasibility_mismatches'],method['objective_mismatches'],method['assignments_compared'])==(8,1,0,23,0,32)
    assert metrics['physical_generation_calls']==8 and metrics['physical_generation_cost']==summaries['dev-initial-v2']['completed_row_cost']
    for row in load_rows(root/'dev-score-v2/raw.jsonl'):
        candidate=row['results']['initial']
        if row['id']=='31d8b6f0':
            assert candidate['model']==valid_models[row['id']]['model']
            assert candidate['verification']['feasibility_mismatches']==23
            for solver in candidate['portfolio']['solvers']:
                assert solver['status']=='optimal' and solver['objective']==31 and solver['solution']==[1]*5
            assert candidate['portfolio']['concordance'] and not candidate['usable_for_original_problem']
        else:assert candidate['portfolio'] is None
    test=summaries['test-initial-v2']
    assert test['observed']==1 and len(test['missing_ids'])==15 and test['schema_valid']==0
    assert not (root/'test-initial-v2/generation.json').exists()
    assert not any(root.glob('test-direct*')) and not any(root.glob('test-self*')) and not any(root.glob('test-guided*'))
    stop=json.loads((root/'test-initial-resource-stop.json').read_text())
    assert stop['responses_observed_before_stop']==0 and stop['signal']=='SIGTERM'
    write=dict(status='observed_records_audited',phases=summaries,source_and_output_hash_checks=source_checks,
               independent_finite_result=finite,feedback_minimal_verified=True,timestamp_notes=timestamp_notes,
               resource_stop_reconciliation=dict(pre_stop_inspection_count=0,final_flushed_record_count=1,unobserved_initial_cases=15,
                                                generation_metadata='missing',H15='unresolved; no comparison phases'),
               non_claims=['No inference executed by this audit.', 'No imputation of missing cases.', 'No causal v1/v2 performance claim.', 'Recorded host compression does not isolate the cause of runtime slowdown.'])
    output.write_text(json.dumps(write,ensure_ascii=False,indent=2)+'\n')
    print('Audited 16 dev records and ONE final flushed test record; 15 missing; H15 unresolved.')


if __name__=='__main__':main()
