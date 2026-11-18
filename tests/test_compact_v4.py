"""Known-development regressions; not held-out scientific cases."""
import unittest
from quantage.compact_v2 import parse_v2
from quantage.compact_v4 import execute_v4
from quantage.benchmark import mis_request


class CompactV4(unittest.TestCase):
    def test_unresolved_direction_overrides_positive_words(self):
        p=parse_v2('{"action":"propose","task":"maximum_weight_independent_set","reason":"fixture"}')
        request=mis_request(1,[])
        request['intent']='I have not decided whether the goal is greatest total weight or greatest number of independent vertices.'
        self.assertEqual(execute_v4(request,p,True)['stage'],'semantic_veto')
        request['intent']='Choose an independent set whose weights have the greatest total value.'
        self.assertEqual(execute_v4(request,p,True)['status'],'accepted')


if __name__=='__main__':unittest.main()
