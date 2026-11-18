"""Software fixtures only; none of these proposals is a native-agent result."""
import copy
import unittest
from quantage.agent_pipeline import process_proposal
from quantage.benchmark import mis_request, photon_request
from quantage.core import formulate, understand


def fixture(request):
    p=understand(request);mis=p['family']=='mis'
    return {'id':'software_fixture','action':'propose','problem':p,'formulation':formulate(p),
            'solver':{'local_solver':'exhaustive_qubo' if mis else 'single_photon_amplitudes',
                      'quantum_provider':'Pasqal' if mis else 'Quandela','hardware_status':'unverified','execution_kind':'local'},
            'reason':'Test fixture, not an agent-generated scientific response.'}


class AgentBoundary(unittest.TestCase):
    def test_two_families_execute_locally(self):
        for request in (mis_request(3,[[0,1],[0,2]],[5,1,1]),photon_request(.2,.3,.4)):
            out=process_proposal(request,fixture(request))
            self.assertEqual(out['status'],'accepted')
            self.assertFalse(out['qpu_submitted'])
            self.assertFalse(out['semantic_certificate'])

    def test_changed_data_and_false_hardware_claim(self):
        req=mis_request(2,[[0,1]],[1,2]);proposal=fixture(req)
        proposal['problem']['weights'][0]=3
        self.assertEqual(process_proposal(req,proposal)['stage'],'contract_boundary')
        proposal=fixture(req);proposal['solver']['execution_kind']='physical'
        self.assertEqual(process_proposal(req,proposal)['stage'],'contract_boundary')

    def test_paired_numeric_intervention(self):
        req=mis_request(2,[[0,1]],[1,1]);proposal=fixture(req)
        proposal['formulation']['quadratic']=[[0,1,1]];proposal['formulation']['penalty']=1
        self.assertEqual(process_proposal(req,proposal,numerical=False)['status'],'accepted')
        self.assertEqual(process_proposal(req,proposal,numerical=True)['stage'],'numerical_verifier')

    def test_original_semantics_is_not_certified(self):
        req=mis_request(2,[[0,1]],[1,2]);proposal=fixture(req)
        changed=copy.deepcopy(req);changed['intent']='Count all independent sets.'
        result=process_proposal(changed,proposal)
        self.assertEqual(result['status'],'accepted')
        self.assertFalse(result['semantic_certificate'])

    def test_abstention_does_not_execute_model(self):
        req=mis_request(1,[])
        proposal={'id':'fixture','action':'abstain','problem':None,'formulation':None,'solver':None,'reason':'Unsupported.'}
        self.assertEqual(process_proposal(req,proposal)['stage'],'agent_decision')
        proposal['formulation']={'kind':'unexpected'}
        self.assertEqual(process_proposal(req,proposal)['stage'],'contract_boundary')


if __name__=='__main__':unittest.main()
