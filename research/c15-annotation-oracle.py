"""Independent exact binary oracle from public data and frozen reviewer labels.

Does not import QuantAge code and never opens author annotations.
Command: python3 research/c15-annotation-oracle.py --output OUTPUT_JSON
"""
import argparse
import itertools
import json
from pathlib import Path


def solve(data, clauses):
    """Literal finite semantics: 1 includes item; implication [a,b] is a=>b."""
    feasible = []
    for bits in itertools.product((0, 1), repeat=data['n']):
        chosen = {i for i, bit in enumerate(bits) if bit}
        if any(a in chosen and b in chosen for a, b in data['edges']):
            continue
        if clauses['budget'] is not None and sum(data['costs'][i] for i in chosen) > clauses['budget']:
            continue
        if clauses['min_count'] is not None and len(chosen) < clauses['min_count']:
            continue
        if clauses['max_count'] is not None and len(chosen) > clauses['max_count']:
            continue
        if not set(clauses['required']).issubset(chosen):
            continue
        if set(clauses['forbidden']).intersection(chosen):
            continue
        if any(a in chosen and b not in chosen for a, b in clauses['implications']):
            continue
        feasible.append((sum(1 << i for i in chosen), sum(data['weights'][i] for i in chosen)))
    best = max((weight for _, weight in feasible), default=None)
    return {'feasible_masks': sorted(mask for mask, _ in feasible),
            'feasible_count': len(feasible), 'max_weight': best,
            'optimal_masks': sorted(mask for mask, weight in feasible if weight == best)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    base = Path('runs/20261114-c15-formulation-repair')
    cases = {case['id']: (split, case) for split in ('dev', 'test')
             for case in json.loads((base / (split + '_cases.json')).read_text())}
    labels = json.loads((base / 'private_gold.review.json').read_text())
    assert len(cases) == len(labels) == 24
    assert set(cases) == {label['id'] for label in labels}
    # Hand-computable controls check index convention, edge and implication
    # direction, costs versus weights, ties, and contradictory cardinalities.
    empty = dict(budget=None, min_count=None, max_count=None, required=[], forbidden=[], implications=[])
    sample = dict(n=2, weights=[3, 7], costs=[9, 2], edges=[])
    assert solve(sample, empty)['optimal_masks'] == [3]
    assert solve(sample, dict(empty, budget=2))['optimal_masks'] == [2]
    assert solve(sample, dict(empty, implications=[[0, 1]]))['feasible_masks'] == [0, 2, 3]
    assert solve(dict(sample, edges=[[0, 1]]), empty)['feasible_masks'] == [0, 1, 2]
    assert solve(sample, dict(empty, min_count=2, max_count=1))['max_weight'] is None
    assert solve(dict(sample, weights=[3, 3], edges=[[0, 1]]), empty)['optimal_masks'] == [1, 2]
    rows = []
    for label in labels:
        split, case = cases[label['id']]
        assert split == label['split']
        rows.append(dict(id=label['id'], split=split, **solve(case['data'], label['constraints'])))
    result = {'assertion_tested': 'Exact feasible domain and maximizing weight for every binary assignment in 24 public C15 instances under independently extracted reviewer clauses.',
              'arithmetic': 'integer, exact', 'bit_convention': 'bit i is inclusion of item i',
              'label_source': 'private_gold.review.json frozen before author comparison',
              'cases': rows,
              'infeasible_ids': [row['id'] for row in rows if row['feasible_count'] == 0],
              'hand_controls_passed': 6,
              'non_claims': ['No LLM performance measured.', 'Finite exact semantics do not certify arbitrary free text.', 'No author labels or production solver imported.']}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print('Computed 24 exact reviewer domains; infeasible: ' + ', '.join(result['infeasible_ids']))


if __name__ == '__main__':
    main()
