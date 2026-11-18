"""Run one real local LLM contract proposal, then v3 checks and local solver."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from .compact_v3 import execute_v3
from .evaluation import load_json

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--request',type=Path,required=True)
    parser.add_argument('--record-dir',type=Path,required=True)
    parser.add_argument('--model',type=Path,default=ROOT/'research/external/models/qwen2.5-0.5b-7ae5576')
    args=parser.parse_args();request=load_json(args.request)
    if type(request) is not dict or set(request)!={'intent','data'} or type(request['intent']) is not str:
        parser.error('request must contain exactly intent text and data object')
    args.record_dir.mkdir(parents=True,exist_ok=False)
    cases=args.record_dir/'cases.json'
    cases.write_text(json.dumps([{'id':'local_request','request':request}],ensure_ascii=False,indent=2)+'\n')
    command=[sys.executable,'-m','quantage.local_inference_v2','--cases',str(cases.resolve()),
             '--instructions',str(ROOT/'runs/20261113-c09-heldout-guard/instructions.md'),
             '--model',str(args.model.resolve()),'--model-manifest',str(ROOT/'runs/20261113-c07-public-traces/model-acquisition.json'),
             '--output',str((args.record_dir/'generation').resolve())]
    with (args.record_dir/'inference.log').open('w') as log:
        subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    rows=[json.loads(s) for s in (args.record_dir/'generation/raw.jsonl').read_text().splitlines()]
    if len(rows)!=1:raise ValueError('single request expected')
    result=execute_v3(request,rows[0]['parsed'],True)
    record={'result':result,'raw_model_response':rows[0]['raw_response'],
            'input_tokens':rows[0]['input_tokens'],'output_tokens':rows[0]['output_tokens'],
            'record_directory':str(args.record_dir),'scope':'local research prototype, heuristic semantic veto, no QPU'}
    (args.record_dir/'result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False))
    return 0 if result['status']=='accepted' else 2


if __name__=='__main__':raise SystemExit(main())
