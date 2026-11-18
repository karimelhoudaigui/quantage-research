"""Acquire a small fixed collection of public trace files as inert data."""
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

SOURCES={
 'QuantBlockchain/quantum-circuit-vision':[
   'LICENSE','dataset/README.md','dataset/experiment_results/README.md',
   'dataset/experiment_results/raw/claude-haiku-4.5_bv_A04_single_rx_raw.txt',
   'dataset/experiment_results/raw/claude-haiku-4.5_bv_A05_single_ry_raw.txt',
   'dataset/experiment_results/raw/claude-haiku-4.5_bv_A06_single_rz_raw.txt'],
 'Elias-Abebe-Gasparini/PQID-Bench':[
   'LICENSE.md','LICENSES/CC-BY-4.0.txt','LICENSES/MIT.txt',
   'artifacts/pqid_bench_external_generation_prompts.jsonl',
   'artifacts/external_model_batches/responses/huggingface_or_local_qwen_qwen2_5-coder-7b-instruct_responses.jsonl',
   'artifacts/external_model_batches/requests/huggingface_or_local_qwen_qwen2_5-coder-7b-instruct_requests.jsonl']}


def main():
    records=[];total=0
    root=Path('research/external/public-traces');root.mkdir(parents=True,exist_ok=True)
    for repo,paths in SOURCES.items():
        with urllib.request.urlopen('https://api.github.com/repos/'+repo+'/commits/main',timeout=30) as response:
            commit=json.load(response)['sha']
        for path in paths:
            source='https://raw.githubusercontent.com/'+repo+'/'+commit+'/'+path
            with urllib.request.urlopen(source,timeout=30) as response:data=response.read(1024*1024+1)
            if len(data)>1024*1024 or total+len(data)>6*1024*1024:raise ValueError('acquisition cap')
            target=root/repo.split('/')[-1]/path;target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as out:out.write(data)
            total+=len(data);records.append({'repository':repo,'commit':commit,'path':str(target),
                 'source_url':source,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    report={'checked_on':'2026-11-13','recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'files':records,'total_bytes':total,'executed_remote_code':False,'provider_calls':0,
            'limits':['Publisher-declared model identity, not provider authentication',
                      'QCV MIT dataset; PQID scoped licenses and third-party/provider terms retained',
                      'No claim that archived tasks match C06, no evaluation performed by downloader']}
    Path('runs/20261113-c07-public-traces/public-acquisition.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'files':len(records),'bytes':total,'repositories':list(SOURCES)}))


if __name__=='__main__':main()
