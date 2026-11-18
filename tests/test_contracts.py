import copy
import unittest
from quantage.benchmark import mis_request, photon_request
from quantage.core import formulate, understand
from quantage.contracts import verify_external


class ExternalContracts(unittest.TestCase):
    def test_unknown_sense_never_uses_max_default(self):
        p = understand(mis_request(2, [[0,1]], [1,2]))
        m = {'kind':'qubo','linear':[1,2],'quadratic':[[0,1,-3]],'constant':0,'sense':'banana'}
        self.assertFalse(verify_external(p,m)['valid'])
        m['sense'] = 'maximize'
        self.assertTrue(verify_external(p,m)['valid'])

    def test_python_indices_and_boolean_indices_rejected(self):
        p = understand(mis_request(2, [[0,1]], [1,2]))
        for j in (-1, True, 2):
            m = formulate(p);m['quadratic'] = [[0,j,3]]
            self.assertEqual(verify_external(p,m)['stage'],'schema')

    def test_metadata_and_overflow_fail_before_execution(self):
        p = understand(mis_request(1, []))
        for key in ('constant','penalty'):
            m = formulate(p);m[key] = float('nan')
            self.assertEqual(verify_external(p,m)['stage'],'schema')
        m = formulate(p);m['linear'] = [1e308];m['constant'] = 1e308;m['sense']='maximize'
        self.assertEqual(verify_external(p,m)['stage'],'schema')

    def test_optical_enums_and_tolerance(self):
        p = understand(photon_request(.2,.3,.4))
        changes = [('order','garbage'),('output','garbage'),('coherent','false'),('phase_mode',-1),('input_mode',True)]
        for key,value in changes:
            m = formulate(p);m[key]=value
            self.assertEqual(verify_external(p,m)['stage'],'schema')
        for tolerance in (0,-1,float('inf'),float('nan'),True,1):
            self.assertEqual(verify_external(p,formulate(p),tolerance)['stage'],'schema')
        p['family']='unsupported_family'
        self.assertFalse(verify_external(p,formulate(understand(photon_request(.2,.3,.4))))['valid'])

    def test_output_equivalent_models_remain_admissible(self):
        p = understand(mis_request(3,[[0,1],[0,2]],[5,1,1]));m = formulate(p)
        m['constant'] += 7
        self.assertTrue(verify_external(p,m)['valid'])
        p = understand(photon_request(.2,.3,.4));m = formulate(p)
        m['global_phase']=1.23;m['order']='R_a P R_b'
        self.assertTrue(verify_external(p,m)['valid'])
        other=copy.deepcopy(m);other['b']=.9
        self.assertFalse(verify_external(p,other)['valid'])


if __name__ == '__main__':
    unittest.main()
