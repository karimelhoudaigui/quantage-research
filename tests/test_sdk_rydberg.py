"""Analytic finite-Hamiltonian tests; no Pulser/QuTiP import or simulation."""
import math
import importlib.util
import unittest
from quantage.sdk_rydberg import hamiltonian,oracle_probabilities


@unittest.skipUnless(importlib.util.find_spec("numpy"), "optional NumPy oracle dependency unavailable")
class RydbergOracle(unittest.TestCase):
    def test_zero_drive_preserves_ground(self):
        probabilities=oracle_probabilities(hamiltonian(0,1,math.pi/2,17),0.5)
        self.assertEqual(probabilities,[1,0,0,0])

    def test_no_interaction_is_product_of_rabi_rotations(self):
        omega,time=2.3,0.7
        p=math.sin(omega*time/2)**2
        expected=[(1-p)**2,p*(1-p),p*(1-p),p**2]
        for phase in (0,math.pi/2):
            observed=oracle_probabilities(hamiltonian(omega,0,phase,0),time)
            for x,y in zip(observed,expected):self.assertAlmostEqual(x,y,places=12)

    def test_interaction_lifts_only_double_excitation(self):
        before=hamiltonian(2,0.5,0,0);after=hamiltonian(2,0.5,0,7)
        for i in range(4):
            for j in range(4):self.assertEqual(after[i][j]-before[i][j],7 if i==j==3 else 0)
