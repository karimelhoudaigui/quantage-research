import copy
import math
import unittest
from quantage.benchmark import mis_request, photon_request
from quantage.core import formulate, understand, pipeline
from quantage.verification import verify


class Contracts(unittest.TestCase):
    def test_penalty_boundary_retains_all_optima(self):
        p = understand(mis_request(2, [[0, 1]]))
        m = formulate(p)
        self.assertTrue(verify(p, m)["valid"])
        m["quadratic"][0][2] = 1
        # A best-feasible-only test would miss the infeasible tied minimizer 11.
        self.assertFalse(verify(p, m)["valid"])

    def test_weighted_not_cardinality(self):
        result = pipeline(mis_request(3, [[0, 1], [0, 2]], [5, 1, 1]))
        self.assertEqual(result["solution"]["solutions"], [[1, 0, 0]])

    def test_interference_and_global_phase(self):
        p = understand(photon_request(math.pi/4, math.pi/4, 0))
        m = formulate(p)
        self.assertTrue(verify(p, m)["valid"])
        m["coherent"] = False
        self.assertFalse(verify(p, m)["valid"])
        m = formulate(p)
        m["global_phase"] = 1.234
        self.assertTrue(verify(p, m)["valid"])

    def test_strict_input_validation(self):
        good = mis_request(2, [[0, 1]])
        for edge in ([[0, 0]], [[0, 1], [1, 0]], [[-1, 0]], [[True, 0]], [[0, 2]], [[0]]):
            bad = copy.deepcopy(good)
            bad["data"]["edges"] = edge
            self.assertEqual(pipeline(bad)["status"], "abstain")
        for value in (float("nan"), float("inf"), True, "pi"):
            bad = photon_request(value, 0, 0)
            self.assertEqual(pipeline(bad)["status"], "abstain")
        bad = copy.deepcopy(good)
        bad["data"]["extra_constraint"] = "include vertex 0"
        self.assertEqual(pipeline(bad)["status"], "abstain")

    def test_no_false_hardware_access(self):
        for req in (mis_request(1, []), photon_request(.1, .2, .3)):
            route = pipeline(req)["route"]
            self.assertFalse(route["qpu_submitted"])
            self.assertEqual(route["hardware_readiness"], "unverified")


if __name__ == "__main__":
    unittest.main()
