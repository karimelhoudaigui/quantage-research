"""Check C11 corpus/labels and historical preservation before generation."""
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from quantage.compact_agent import TASKS
from quantage.core import MIS_INTENT, PHOTO_INTENT, understand

RUN = ROOT / 'runs/20261113-c11-frozen-transfer'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canon(request):
    return json.dumps(request, sort_keys=True, ensure_ascii=False, allow_nan=False)


def text_key(text):
    normalized = unicodedata.normalize('NFKC', text).casefold()
    return re.sub(r'[^\w]+', ' ', normalized).strip()


def requests(value):
    if isinstance(value, dict):
        if set(value) == {'intent', 'data'} and isinstance(value['intent'], str):
            yield value
        for item in value.values():
            yield from requests(item)
    elif isinstance(value, list):
        for item in value:
            yield from requests(item)


def main():
    public = json.loads((RUN / 'public_cases.json').read_text())
    labels = json.loads((RUN / 'gold.json').read_text())
    gold = {r['id']: r for r in labels}
    need(len(public) == len(gold) == len(labels) == 128, '128 unique labelled cases required')
    need({r['id'] for r in public} == set(gold), 'ID mismatch')
    new_requests = set()
    new_texts = set()
    groups = {}
    for row in public:
        label = gold[row['id']]
        need(label['expected_action'] in ('propose', 'abstain') and label['family'] in TASKS, 'label enums')
        expected = TASKS[label['family']] if label['expected_action'] == 'propose' else None
        need(label['expected_task'] == expected and label['group_id'] == row['group_id'], 'label task/group')
        request = row['request']
        understand({'intent': MIS_INTENT if label['family'] == 'mis' else PHOTO_INTENT, 'data': request['data']})
        key = canon(request)
        text = text_key(request['intent'])
        need(key not in new_requests and text not in new_texts, 'duplicate new request/text')
        new_requests.add(key)
        new_texts.add(text)
        groups.setdefault(row['group_id'], []).append(row)
    need(len(groups) == 64 and all(len(v) == 2 for v in groups.values()), '64 paired groups')
    for pair in groups.values():
        need(pair[0]['request']['data'] == pair[1]['request']['data'], 'paired numeric input differs')
        need(len({gold[r['id']]['family'] for r in pair}) == 1, 'mixed family group')
    snapshot = json.loads((RUN / 'historical-snapshot.json').read_text())
    for name, digest in snapshot['files'].items():
        need(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, 'changed historical file ' + name)
    frozen = json.loads((RUN / 'frozen-inputs.json').read_text())
    for name, digest in frozen['files'].items():
        need(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, 'changed frozen code ' + name)
    old_requests, old_texts, files = set(), set(), []
    for name in sorted(snapshot['files']):
        path = ROOT / name
        if path.suffix not in ('.json', '.jsonl'):
            continue
        values = [json.loads(s) for s in path.read_text().splitlines()] if path.suffix == '.jsonl' else [json.loads(path.read_text())]
        found = [r for value in values for r in requests(value)]
        if found:
            files.append(str(path.relative_to(ROOT)))
        for request in found:
            old_requests.add(canon(request))
            old_texts.add(text_key(request['intent']))
    need(not new_requests & old_requests and not new_texts & old_texts, 'historical duplicate')
    report = {'status': 'passed', 'cases': len(public), 'groups': len(groups),
              'actions': {k: sum(r['expected_action'] == k for r in labels) for k in ('propose', 'abstain')},
              'families': {k: sum(r['family'] == k for r in labels) for k in TASKS},
              'languages': {k: sum(r['language'] == k for r in labels) for k in sorted({r['language'] for r in labels})},
              'historical_files_checked_unchanged': len(snapshot['files']),
              'old_public_request_files': files, 'old_requests_distinct': len(old_requests),
              'old_texts_distinct': len(old_texts), 'request_overlap': 0, 'normalized_text_overlap': 0,
              'public_sha256': hashlib.sha256((RUN / 'public_cases.json').read_bytes()).hexdigest(),
              'gold_sha256': hashlib.sha256((RUN / 'gold.json').read_bytes()).hexdigest(),
              'limitations': 'Exact/normalized text duplicate checks, not semantic or pretraining contamination proof.'}
    (RUN / 'preflight.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
