"""Protocol software fixtures, never recorded model responses."""
import json
import unittest
from quantage.compact_agent import parse_compact,execute_compact
from quantage.benchmark import mis_request,photon_request


class Compact(unittest.TestCase):
    def test_two_supported_contracts(self):
        for family,task,request in [('mis','maximum_weight_independent_set',mis_request(2,[[0,1]],[1,2])),
                                    ('photon','ideal_single_photon_probabilities',photon_request(.2,.3,.4))]:
            parsed=parse_compact(json.dumps({'action':'propose','family':family,'task':task,'reason':'fixture'}))
            self.assertEqual(execute_compact(request,parsed)['status'],'accepted')

    def test_no_repair_and_explicit_abstention(self):
        for raw in ('{"action":','prefix {"action":"abstain"}','{"action":"abstain","family":"other","task":null,"reason":"x"}'):
            self.assertFalse(parse_compact(raw)['valid'])
        p=parse_compact('{"action":"abstain","family":"mis","task":null,"reason":"unsupported"}')
        self.assertEqual(execute_compact(mis_request(1,[]),p)['stage'],'model_abstention')

    def test_whole_single_code_fence_only(self):
        raw='{"action":"abstain","family":"photon","task":null,"reason":"fixture"}'
        self.assertTrue(parse_compact('```json\n'+raw+'\n```')['valid'])
        self.assertFalse(parse_compact('Here is JSON:\n```json\n'+raw+'\n```')['valid'])


if __name__=='__main__':unittest.main()
