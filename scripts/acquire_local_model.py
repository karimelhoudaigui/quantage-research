"""Download a pinned public Safetensors checkpoint without credentials.

No hub SDK, login, shell commands, pickle weights, or remote Python code.
The file list, byte limits, deadline, revision and hashes are recorded.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import time
import urllib.request

MODEL='Qwen/Qwen2.5-0.5B-Instruct'
REVISION='7ae557604adf67be50417f59c2c2f167def9a775'
FILES=('LICENSE','README.md','config.json','generation_config.json','merges.txt',
       'model.safetensors','tokenizer.json','tokenizer_config.json','vocab.json')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--directory',type=Path,required=True)
    parser.add_argument('--manifest',type=Path,required=True)
    args=parser.parse_args();args.directory.mkdir(parents=True,exist_ok=True)
    started=time.monotonic();records=[];total=0
    # Credential-free public metadata; the response pins LFS SHA-256 values.
    url='https://huggingface.co/api/models/'+MODEL+'/tree/'+REVISION
    with urllib.request.urlopen(url,timeout=30) as response:tree=json.load(response)
    indexed={row['path']:row for row in tree}
    for name in FILES:
        expected=indexed[name];size=expected['size']
        if size>1100*1024*1024 or total+size>1200*1024*1024:
            raise ValueError('declared download byte cap exceeded')
        path=args.directory/name
        if path.exists():raise ValueError('refuse to overwrite '+str(path))
        source='https://huggingface.co/'+MODEL+'/resolve/'+REVISION+'/'+name
        digest=hashlib.sha256();observed=0
        with urllib.request.urlopen(source,timeout=30) as response, path.open('xb') as destination:
            while True:
                if time.monotonic()-started>240:raise TimeoutError('acquisition deadline')
                chunk=response.read(1024*1024)
                if not chunk:break
                observed+=len(chunk)
                if observed>size:raise ValueError('observed bytes exceed metadata')
                destination.write(chunk);digest.update(chunk)
        if observed!=size:raise ValueError('size mismatch '+name)
        expected_hash=expected.get('lfs',{}).get('oid')
        if expected_hash and digest.hexdigest()!=expected_hash:
            raise ValueError('LFS SHA-256 mismatch '+name)
        total+=observed
        records.append({'name':name,'url':source,'bytes':observed,'sha256':digest.hexdigest(),
                        'expected_lfs_sha256':expected_hash})
        print('Acquired',name,observed,flush=True)
    manifest={'model':MODEL,'revision':REVISION,'format':'safetensors','credential_use':False,
              'remote_code_execution':False,'external_purchase_eur':0,'total_bytes':total,
              'elapsed_seconds':time.monotonic()-started,'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'files':records,'source_tree_metadata':tree,'license':'Apache-2.0'}
    args.manifest.write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':main()
