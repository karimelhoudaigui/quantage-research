"""Boundary and counterexample tests, not fabricated agent results."""
import copy
import unittest
from quantage.repair_model import parse_model, verify_model
from quantage.repair_feedback import validate_feedback, feedback_for_model, optimization_diagnostics


class FiniteCounterexamples(unittest.TestCase):
    def setUp(self):
        self.data={'n':3,'weights':[4,2,3],'costs':[2,1,2],'edges':[[0,2]]}
        self.reference={'budget':3,'min_count':1,'max_count':None,'required':[],
                        'forbidden':[],'implications':[]}
        self.model={'formulation':'binary_ilp','variables':[0,1,2],'sense':'max',
                    'objective':[4,2,3],
                    'constraints':[[[1,0,1],'<=',1],[[2,1,2],'<=',3],[[1,1,1],'>=',1]]}

    def test_missing_cardinality_gets_actual_counterexample(self):
        wrong=copy.deepcopy(self.model);wrong['constraints'].pop()
        result=verify_model(self.data,self.reference,{'valid':True,'model':wrong})
        self.assertFalse(result['faithful'])
        witness=result['feedback']['witnesses'][0]
        self.assertEqual(witness,{'kind':'feasibility','x':[0,0,0],'expected_feasible':False,'proposed_feasible':True})
        self.assertNotIn('constraints',result['feedback'])
        validate_feedback(result['feedback'],3)

    def test_redundant_and_reordered_constraints_are_accepted(self):
        m=copy.deepcopy(self.model);m['constraints'].reverse();m['constraints'].append([[1,0,0],'<=',1])
        self.assertTrue(verify_model(self.data,self.reference,{'valid':True,'model':m})['faithful'])

    def test_scaled_objective_is_separated_from_optimization_equivalence(self):
        m=copy.deepcopy(self.model);m['objective']=[8,4,6]
        result=verify_model(self.data,self.reference,{'valid':True,'model':m})
        self.assertFalse(result['faithful'])
        self.assertTrue(optimization_diagnostics(self.data,self.reference,{'valid':True,'model':m})['finite_optimization_equivalent'])
        self.assertGreater(result['objective_mismatches'],0)

    def test_invalid_json_types_and_feedback_cannot_carry_a_model(self):
        self.assertFalse(parse_model('{"variables":[],"variables":[]}',3)['valid'])
        with self.assertRaises(ValueError):
            validate_feedback({'kind':'counterexamples','witnesses':[],'model':self.model},3)


if __name__ == '__main__':
    unittest.main()
