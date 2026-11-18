"""Acquire one pinned public comparison checkpoint, no credentials or code."""
import datetime
import hashlib
import json
from pathlib import Path
import time
import urllib.request

MODEL = 'HuggingFaceTB/SmolLM2-135M-Instruct'
REVISION = '12fd25f77366fa6b3b4b768ec3050bf629380bac'
DIRECTORY = Path('research/external/models/smollm2-135m-12fd25f')
MANIFEST = Path('runs/20261113-c11-frozen-transfer/model-smol.json')
FILES = ('README.md', 'config.json', 'generation_config.json', 'merges.txt',
         'model.safetensors', 'special_tokens_map.json', 'tokenizer.json',
         'tokenizer_config.json', 'vocab.json')


def main():
    started = time.monotonic()
    url = 'https://huggingface.co/api/models/' + MODEL + '/tree/' + REVISION
    with urllib.request.urlopen(url, timeout=30) as response:
        tree = json.load(response)
    indexed = {row['path']: row for row in tree}
    if sum(indexed[name]['size'] for name in FILES) > 400 * 1024 * 1024:
        raise ValueError('download cap')
    DIRECTORY.mkdir(parents=True, exist_ok=False)
    records = []
    for name in FILES:
        source = 'https://huggingface.co/' + MODEL + '/resolve/' + REVISION + '/' + name
        size = indexed[name]['size']
        digest = hashlib.sha256()
        observed = 0
        with urllib.request.urlopen(source, timeout=30) as response, (DIRECTORY / name).open('xb') as target:
            while True:
                if time.monotonic() - started > 240:
                    raise TimeoutError('public acquisition deadline')
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                observed += len(chunk)
                if observed > size:
                    raise ValueError('unexpected download size')
                target.write(chunk)
                digest.update(chunk)
        expected = indexed[name].get('lfs', {}).get('oid')
        if observed != size or (expected and digest.hexdigest() != expected):
            raise ValueError('checkpoint integrity ' + name)
        records.append({'name': name, 'url': source, 'bytes': observed,
                        'sha256': digest.hexdigest(), 'expected_lfs_sha256': expected})
        print('Acquired', name, observed, flush=True)
    MANIFEST.write_text(json.dumps({
        'model': MODEL, 'revision': REVISION, 'format': 'safetensors',
        'files': records, 'source_tree_metadata': tree,
        'license': 'Apache-2.0 declared in retained model card and primary repository metadata',
        'credential_use': False, 'remote_code_execution': False,
        'external_purchase_eur': 0, 'total_bytes': sum(r['bytes'] for r in records),
        'elapsed_seconds': time.monotonic() - started,
        'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()
    }, indent=2) + '\n')


if __name__ == '__main__':
    main()
