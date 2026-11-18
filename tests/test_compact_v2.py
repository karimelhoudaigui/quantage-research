"""Protocol fixtures only, no scientific response data."""
import json
import unittest
from quantage.compact_v2 import parse_v2,execute_v2
from quantage.benchmark import mis_request,photon_request


class CompactV2(unittest.TestCase):
    def test_nonredundant_task_and_no_silent_repair(self):
        p={'action':'propose','task':'ideal_single_photon_probabilities','reason':'fixture'}
        request=photon_request(.2,.3,.4);request['intent']='Compute ideal probabilities for one photon in mode0, phase on mode1.'
        self.assertEqual(execute_v2(request,parse_v2(json.dumps(p)),True)['status'],'accepted')
        p['family']='mis'
        self.assertFalse(parse_v2(json.dumps(p))['valid'])

    def test_same_response_before_after_veto(self):
        p=parse_v2('{"action":"propose","task":"maximum_weight_independent_set","reason":"fixture"}')
        req=mis_request(3,[[0,1]],[1,2,3]);req['intent']='Maximize the cardinality of an independent set, ignoring weights.'
        self.assertEqual(execute_v2(req,p,False)['status'],'accepted')
        self.assertEqual(execute_v2(req,p,True)['stage'],'semantic_veto')
        req['intent']='Maximize the total weight of an independent set.'
        self.assertEqual(execute_v2(req,p,True)['status'],'accepted')


if __name__=='__main__':unittest.main()
