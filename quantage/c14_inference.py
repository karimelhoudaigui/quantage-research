"""Real offline checkpoint inference. No gold labels, network or candidate exec."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import time


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--cases',type=Path,required=True)
    parser.add_argument('--instructions',type=Path,required=True)
    parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--model-manifest',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    root=Path.cwd()
    os.environ.update(HF_HOME=str(root/'research/external/models/hf-local'),HF_HUB_OFFLINE='1',
        TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_IMPLICIT_TOKEN='1',HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false')
    import torch,transformers
    from transformers import AutoTokenizer,AutoModelForCausalLM
    cases=json.loads(args.cases.read_text());instructions=args.instructions.read_text();docs=''
    acquisition=json.loads(args.model_manifest.read_text())
    for row in acquisition['files']:
        if hashlib.sha256((args.model/row['name']).read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('changed checkpoint file '+row['name'])
    args.output.mkdir(parents=True,exist_ok=True)
    if (args.output/'raw.jsonl').exists():raise ValueError('do not overwrite response traces')
    torch.set_num_threads(4);torch.manual_seed(20261113)
    started=time.perf_counter();cpu0=time.process_time()
    tokenizer=AutoTokenizer.from_pretrained(args.model,local_files_only=True,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,trust_remote_code=False,
              use_safetensors=True,torch_dtype=torch.float16,attn_implementation='sdpa')
    model.eval();loaded=time.perf_counter()-started
    model.generation_config.temperature=1.;model.generation_config.top_p=1.;model.generation_config.top_k=50
    completed=0;input_total=0;output_total=0;status='running';error=None
    from .compact_v2 import parse_v2
    try:
        with (args.output/'raw.jsonl').open('x') as raw:
            for case in sorted(cases,key=lambda x:x['id']):
                for arm in ('nonredundant',):
                    if time.perf_counter()-started>1650:raise TimeoutError('C14 generation budget')
                    system=instructions+('\n\nDOCUMENTATION:\n'+docs if arm=='documented' else '')
                    messages=[{'role':'system','content':system},{'role':'user','content':json.dumps(case['request'],ensure_ascii=False)}]
                    text=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
                    inputs=tokenizer(text,return_tensors='pt')
                    if inputs['input_ids'].shape[-1]>4096:raise ValueError('input token budget, no silent truncation')
                    t0=time.perf_counter();c0=time.process_time()
                    with torch.inference_mode():
                        outputs=model.generate(**inputs,do_sample=False,max_new_tokens=128,pad_token_id=tokenizer.eos_token_id)
                    new=outputs[0,inputs['input_ids'].shape[-1]:]
                    response=tokenizer.decode(new,skip_special_tokens=True)
                    eos=model.generation_config.eos_token_id;eos=eos if isinstance(eos,list) else [eos]
                    row={'id':case['id'],'arm':arm,'messages':messages,
                         'request_sha256':hashlib.sha256(json.dumps(case['request'],sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
                         'chat_template_sha256':hashlib.sha256(text.encode()).hexdigest(),
                         'input_tokens':int(inputs['input_ids'].shape[-1]),'output_tokens':int(new.shape[-1]),
                         'wall_seconds':time.perf_counter()-t0,'cpu_seconds':time.process_time()-c0,
                         'finish_reason':'eos' if int(new[-1]) in eos else 'token_limit',
                         'raw_response':response,'parsed':parse_v2(response)}
                    raw.write(json.dumps(row,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n');raw.flush()
                    completed+=1;input_total+=row['input_tokens'];output_total+=row['output_tokens']
                    print(json.dumps({'completed':completed,'id':case['id'],'arm':arm,'tokens':row['output_tokens'],
                                      'seconds':round(row['wall_seconds'],3),'parse_valid':row['parsed']['valid']}),flush=True)
        status='completed'
    except Exception as exc:
        status='partial_error';error=type(exc).__name__+': '+str(exc)
        raise
    finally:
        record={'model':acquisition['model'],'revision':acquisition['revision'],'device':'cpu','dtype':'float16',
                'python':platform.python_version(),'torch':torch.__version__,'transformers':transformers.__version__,
                'threads':4,'seed':20261113,'do_sample':False,'max_new_tokens':128,'max_input_tokens':4096,
                'generation_calls_completed':completed,'generation_calls_planned':len(cases),
                'input_tokens':input_total,'output_tokens':output_total,'load_seconds':loaded,
                'wall_seconds':time.perf_counter()-started,'cpu_seconds':time.process_time()-cpu0,
                'status':status,'error':error,'peak_rss_native_units':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'rss_native_unit_note':'macOS bytes, Linux KiB','external_purchase_eur':0,'hardware_energy_cost':None,
                'network_during_inference':False,'remote_code':False,'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        (args.output/'generation.json').write_text(json.dumps(record,indent=2)+'\n')


if __name__=='__main__':main()
