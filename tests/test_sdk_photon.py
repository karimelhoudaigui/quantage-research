"""Independent hand-computable checks; no optional SDK or LLM required."""
import math
import unittest
from quantage.sdk_photon import bosonic_probabilities,oracle_unitary


class BosonicOracle(unittest.TestCase):
    def test_bunching_has_bosonic_factor(self):
        probabilities=bosonic_probabilities(oracle_unitary(math.pi/4,0,0,0),(1,1,0))
        self.assertAlmostEqual(probabilities[(2,0,0)],0.5)
        self.assertAlmostEqual(probabilities[(0,2,0)],0.5)
        self.assertAlmostEqual(probabilities[(1,1,0)],0)

    def test_colliding_input_normalization(self):
        probabilities=bosonic_probabilities(oracle_unitary(math.pi/4,0,0,0),(2,0,0))
        self.assertAlmostEqual(probabilities[(2,0,0)],0.25)
        self.assertAlmostEqual(probabilities[(1,1,0)],0.5)
        self.assertAlmostEqual(probabilities[(0,2,0)],0.25)
        self.assertAlmostEqual(sum(probabilities.values()),1)

    def test_recombined_phase_changes_interference(self):
        before=bosonic_probabilities(oracle_unitary(math.pi/4,math.pi/4,math.pi/4,0),(1,1,0))
        after=bosonic_probabilities(oracle_unitary(math.pi/4,math.pi/4,math.pi/4,math.pi/2),(1,1,0))
        self.assertGreater(max(abs(before[k]-after[k]) for k in before),0.1)
        self.assertAlmostEqual(sum(before.values()),1)
        self.assertAlmostEqual(sum(after.values()),1)
