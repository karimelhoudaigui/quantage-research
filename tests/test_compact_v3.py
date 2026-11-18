"""Development regressions after C09, not new scientific test cases."""
import json
import unittest
from quantage.compact_v2 import parse_v2
from quantage.compact_v3 import execute_v3
from quantage.benchmark import mis_request,photon_request


class CompactV3(unittest.TestCase):
    def test_explicit_unknown_input_refused(self):
        p=parse_v2('{"action":"propose","task":"ideal_single_photon_probabilities","reason":"fixture"}')
        r=photon_request(.3,.2,.1)
        r['intent']='Ideal output probabilities, coherent circuit. Its input mode is not specified and may be mode0 or mode1.'
        self.assertEqual(execute_v3(r,p,True)['stage'],'semantic_veto')
        r['intent']='Ideal output distribution for one photon in mode0, phase on mode1.'
        self.assertEqual(execute_v3(r,p,True)['status'],'accepted')

    def test_greatest_weight_synonym_without_relaxing_cardinality(self):
        p=parse_v2('{"action":"propose","task":"maximum_weight_independent_set","reason":"fixture"}')
        r=mis_request(2,[[0,1]],[1,2]);r['intent']='Choose nonadjacent vertices with the greatest total weight.'
        self.assertEqual(execute_v3(r,p,True)['status'],'accepted')
        r['intent']='Choose nonadjacent vertices with the greatest cardinality, ignoring weights.'
        self.assertEqual(execute_v3(r,p,True)['stage'],'semantic_veto')


if __name__=='__main__':unittest.main()
