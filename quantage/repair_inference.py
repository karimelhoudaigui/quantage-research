"""One bounded real-model phase. No reference/gold input, no candidate exec."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import time
from .repair_model import parse_model
from .repair_feedback import validate_feedback


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--cases', type=Path, required=True)
    p.add_argument('--instructions', type=Path, required=True)
    p.add_argument('--phase', choices=('initial', 'direct', 'self', 'guided'), required=True)
    p.add_argument('--initial', type=Path)
    p.add_argument('--feedback', type=Path)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--max-new-tokens', type=int, default=384)
    a = p.parse_args()
    if a.phase in ('self', 'guided') and a.initial is None:
        p.error('revision phase needs initial records')
    if a.phase in ('initial', 'direct') and a.initial is not None:
        p.error('independent generation cannot read an initial response')
    if (a.phase == 'guided') != (a.feedback is not None):
        p.error('only guided phase reads minimal feedback')
    root = Path.cwd()
    os.environ.update(HF_HOME=str(root/'research/external/models/hf-local'),
        HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_HUB_DISABLE_IMPLICIT_TOKEN='1',
        HF_HUB_DISABLE_TELEMETRY='1', TOKENIZERS_PARALLELISM='false')
    import torch, transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM
    cases = json.loads(a.cases.read_text())
    need_ids = {r['id'] for r in cases}
    if len(need_ids) != len(cases):
        raise ValueError('duplicate cases')
    initial = {r['id']: r for r in (json.loads(s) for s in a.initial.read_text().splitlines())} if a.initial else {}
    feedback = json.loads(a.feedback.read_text()) if a.feedback else {}
    if a.phase in ('self', 'guided') and not need_ids <= set(initial):
        raise ValueError('missing initial observations, never impute')
    if a.phase == 'guided' and not need_ids <= set(feedback):
        raise ValueError('missing verifier feedback')
    acquisition = json.loads((root/'runs/20261113-c07-public-traces/model-acquisition.json').read_text())
    directory = root/'research/external/models/qwen2.5-0.5b-7ae5576'
    for row in acquisition['files']:
        if hashlib.sha256((directory/row['name']).read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('changed checkpoint')
    a.output.mkdir(parents=True, exist_ok=True)
    if (a.output/'raw.jsonl').exists():
        raise ValueError('refuse to overwrite responses')
    torch.set_num_threads(4)
    started = time.perf_counter(); cpu0 = time.process_time()
    tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(directory, local_files_only=True, trust_remote_code=False,
             use_safetensors=True, torch_dtype=torch.float32, attn_implementation='sdpa')
    model.eval()
    load_seconds = time.perf_counter()-started
    system = a.instructions.read_text()
    count = 0; input_total = 0; output_total = 0; status = 'running'; error = None
    try:
        with (a.output/'raw.jsonl').open('x') as raw:
            for case in sorted(cases, key=lambda r:r['id']):
                if time.perf_counter()-started > 1650:
                    raise TimeoutError('bounded inference phase')
                seed = (int(hashlib.sha256(case['id'].encode()).hexdigest()[:8], 16)
                        + (0 if a.phase == 'initial' else 1)) % (2**32)
                torch.manual_seed(seed)
                messages = [{'role':'system','content':system},
                            {'role':'user','content':json.dumps({'intention':case['intention'],'data':case['data']},ensure_ascii=False)}]
                if a.phase in ('self','guided'):
                    messages.append({'role':'assistant','content':initial[case['id']]['raw_response']})
                    if a.phase == 'self':
                        follow = 'Review the previous model against every original clause and numerical datum. Correct omissions, wrong coefficients or format. Return the COMPLETE revised JSON model only.'
                    else:
                        validate_feedback(feedback[case['id']], case['data']['n'])
                        follow = json.dumps({'verifier_feedback':feedback[case['id']],
                                 'instruction':'Use this verifier result to correct the previous model. Recheck ALL original clauses, not just the witness. Return COMPLETE revised JSON only.'},ensure_ascii=False)
                    messages.append({'role':'user','content':follow})
                prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = tokenizer(prompt, return_tensors='pt')
                input_tokens = int(inputs['input_ids'].shape[-1])
                if input_tokens > 4096:
                    raise ValueError('input cap, no truncation')
                t0 = time.perf_counter(); c0 = time.process_time()
                with torch.inference_mode():
                    generated = model.generate(**inputs, do_sample=True, temperature=.2, top_p=1.,
                                top_k=50, max_new_tokens=a.max_new_tokens, pad_token_id=tokenizer.eos_token_id,
                                return_dict_in_generate=True, output_scores=True)
                new = generated.sequences[0, input_tokens:]
                wall = time.perf_counter()-t0; cpu = time.process_time()-c0
                probabilities = [float(torch.log_softmax(scores[0].float(),dim=-1)[int(token)])
                                 for token,scores in zip(new,generated.scores)]
                if len(probabilities) != int(new.shape[-1]) or not all(float('-inf') < x < float('inf') for x in probabilities):
                    raise ValueError('nonfinite chosen-token scores')
                response = tokenizer.decode(new, skip_special_tokens=True)
                parsed = parse_model(response,case['data']['n'])
                eos = model.generation_config.eos_token_id
                eos = eos if isinstance(eos,list) else [eos]
                row = {'id':case['id'],'phase':a.phase,'seed':seed,'messages':messages,
                       'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
                       'raw_response':response,'parsed':parsed,
                       'input_tokens':input_tokens,'output_tokens':int(new.shape[-1]),
                       'generated_token_ids':[int(x) for x in new],
                       'generated_token_log_probabilities':probabilities,
                       'mean_generated_log_probability':sum(probabilities)/len(probabilities),
                       'log_probability_scope':'chosen tokens after temperature/top-k processors, EOS included',
                       'finish_reason':'eos' if int(new[-1]) in eos else 'token_limit',
                       'generation_wall_seconds':wall,'generation_cpu_seconds':cpu,
                       'wall_seconds':time.perf_counter()-t0,'cpu_seconds':time.process_time()-c0}
                raw.write(json.dumps(row,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n');raw.flush()
                count += 1;input_total += input_tokens;output_total += int(new.shape[-1])
                print(json.dumps({'completed':count,'phase':a.phase,'id':case['id'],'valid_schema':row['parsed']['valid'],'tokens':row['output_tokens']}),flush=True)
                del generated, new
        status = 'completed'
    except Exception as exc:
        status = 'partial_error';error = type(exc).__name__+': '+str(exc)
        raise
    finally:
        record = {'model':acquisition['model'],'revision':acquisition['revision'],'python':platform.python_version(),
                  'torch':torch.__version__,'transformers':transformers.__version__,'dtype':'float32','device':'cpu',
                  'threads':4,'phase':a.phase,'sampling':{'temperature':.2,'top_p':1.,'top_k':50},
                  'seed_rule':'first8hexsha256(id) + round index modulo2**32',
                  'max_new_tokens':a.max_new_tokens,'max_input_tokens':4096,'planned':len(cases),'completed':count,
                  'input_tokens':input_total,'output_tokens':output_total,'load_seconds':load_seconds,
                  'wall_seconds':time.perf_counter()-started,'cpu_seconds':time.process_time()-cpu0,
                  'peak_rss_native_units':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  'status':status,'error':error,'network_during_inference':False,'external_purchase_eur':0,
                  'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        (a.output/'generation.json').write_text(json.dumps(record,indent=2)+'\n')


if __name__ == '__main__':
    main()
