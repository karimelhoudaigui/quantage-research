"""Software boundary tests; fixtures are not measured LLM performance."""
import unittest

from quantage.c11_score import accumulate, counts, complete, hypothesis
from quantage.compact_agent import TASKS


class EvaluationBoundaries(unittest.TestCase):
    def test_wrong_task_is_error_even_on_supported_case(self):
        value = counts()
        label = {'expected_action': 'propose', 'expected_task': TASKS['mis']}
        accumulate(value, label, {'status': 'decision_accept', 'task': TASKS['photon']})
        self.assertEqual(value['accepted_correct'], 0)
        self.assertEqual(value['accepted_wrong_task_supported'], 1)
        self.assertEqual(value['accepted_wrong'], 1)

    def test_agreement_never_imputes_missing_or_invalid_proposal(self):
        proposal = {'valid': True, 'proposal': {'action': 'propose', 'task': TASKS['mis'], 'reason': 'fixture'}}
        result = complete({'intent': 'unused', 'data': {}}, proposal, {'valid': False, 'reason': 'missing'})
        self.assertEqual(result['status'], 'abstain')
        self.assertEqual(result['stage'], 'consensus_format')

    def test_zero_reference_errors_cannot_confirm_reduction(self):
        reference = dict(counts(), accepted_correct=4)
        self.assertEqual(hypothesis(reference, reference, .5, .9)['status'], 'unresolved')
        reference['accepted_wrong'] = 2
        guarded = dict(reference, accepted_correct=3, accepted_wrong=0)
        self.assertEqual(hypothesis(reference, guarded, .5, .9)['status'], 'not_supported_in_finite_test')


if __name__ == '__main__':
    unittest.main()
