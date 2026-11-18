import unittest
from quantage.routing import review_route


class Routing(unittest.TestCase):
    def test_candidate_is_not_execution_permission(self):
        proposal = {"solver":"pasqal_analog", "provider":"Pasqal", "execution_kind":"candidate", "claim":"conditional_candidate"}
        # Policy edits cannot enable an executor which does not exist.
        for enabled in (False, True):
            policy = {"qpu_providers":["Pasqal","Quandela"], "qpu_submission_enabled":enabled}
            out = review_route({"family":"mis","n":3}, proposal, policy)
            self.assertTrue(out['acceptable_recommendation'])
            self.assertEqual(out['execution_permission'], 'not_authorized')
            self.assertEqual(out['hardware_readiness'], 'unverified')
            proposal['host_country'] = 'Canada'
        proposal['claim'] = 'hardware_verified'
        self.assertFalse(review_route({'family':'mis','n':3}, proposal, policy)['acceptable_recommendation'])

    def test_foreign_host_is_not_provider_nationality(self):
        proposal = {'provider':'ForeignVendor','host_country':'France','solver':'foreign_qpu','execution_kind':'candidate','claim':'conditional_candidate'}
        policy = {'qpu_providers':['Pasqal','Quandela'],'qpu_submission_enabled':False}
        self.assertTrue(review_route({'family':'mis'},proposal,policy,'name_only')['acceptable_recommendation'])
        self.assertFalse(review_route({'family':'mis'},proposal,policy)['acceptable_recommendation'])


if __name__ == '__main__':
    unittest.main()
