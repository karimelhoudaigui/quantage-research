"""Replay the four fixed local experiments in a fresh temp directory.

Commands are static project code; never execute commands read from a manifest.
Only per-row/process timings are removed before deterministic comparison.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def without_times(value):
    if isinstance(value, dict):
        return {k:without_times(v) for k,v in value.items() if k != 'elapsed_seconds'}
    if isinstance(value, list):
        return [without_times(v) for v in value]
    return value


def replay():
    jobs = [
        ('20261113-c01-foundation', ['quantage.benchmark', 'foundation']),
        ('20261113-c02-formulation', ['quantage.faultstudy']),
        ('20261113-c03-routing', ['quantage.routingstudy','--cases','runs/20261113-c03-routing/cases.json','--policy','config/policy.json']),
        ('20261113-c04-transfer', ['quantage.transferstudy','--cases','runs/20261113-c04-transfer/cases.json'])]
    with tempfile.TemporaryDirectory(prefix='quantage-replay-') as temp:
        for name, args in jobs:
            output = Path(temp)/name
            subprocess.run([sys.executable,'-m']+args+['--output',str(output)], cwd=ROOT,
                           check=True, timeout=60, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            expected = ROOT/'runs'/name/'results'
            rows = lambda path: [without_times(json.loads(s)) for s in path.read_text().splitlines()]
            if rows(output/'raw.jsonl') != rows(expected/'raw.jsonl'):
                raise ValueError('raw replay mismatch '+name)
            if without_times(json.loads((output/'metrics.json').read_text())) != without_times(json.loads((expected/'metrics.json').read_text())):
                raise ValueError('metric replay mismatch '+name)
            print('Reproduced',name,'all rows and metrics excluding elapsed_seconds')


if __name__ == '__main__':
    replay()
