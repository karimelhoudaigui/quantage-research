"""Small real-solver checks; these timings are not performance evidence."""

import unittest

from quantage.repair_model import model_feasible
from quantage.repair_solvers import enumeration_dfs, portfolio, scipy_highs_milp


def proposed_model(objective, constraints):
    return {
        "formulation": "binary_ilp",
        "variables": list(range(len(objective))),
        "sense": "max",
        "objective": objective,
        "constraints": constraints,
    }


class EnumerationTests(unittest.TestCase):
    def test_every_binary_leaf_and_all_tied_optima(self):
        model = proposed_model([0] * 7, [])
        result = enumeration_dfs(model)
        self.assertEqual(result["status"], "optimal")
        self.assertEqual(result["visited_leaves"], 128)
        self.assertEqual(len(result["all_optima"]), 128)
        self.assertEqual(len({tuple(x) for x in result["all_optima"]}), 128)

    def test_infeasibility_is_not_an_empty_optimal_solution(self):
        model = proposed_model([1], [[[1], ">=", 1], [[1], "<=", 0]])
        result = enumeration_dfs(model)
        self.assertEqual(result["status"], "infeasible")
        self.assertIsNone(result["objective"])
        self.assertIsNone(result["solution"])
        self.assertEqual(result["all_optima"], [])


class RealHighsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from scipy.optimize import milp
        except ImportError as exc:
            raise unittest.SkipTest("SciPy milp is not installed: " + str(exc))
        if not callable(milp):
            raise unittest.SkipTest("SciPy milp is unavailable")

    def test_multiple_optima_compare_values_without_forcing_same_vector(self):
        model = proposed_model([1, 1], [[[1, 1], "<=", 1]])
        exact = enumeration_dfs(model)
        highs = scipy_highs_milp(model)
        self.assertEqual(exact["all_optima"], [[0, 1], [1, 0]])
        self.assertEqual(highs["status"], "optimal", highs)
        self.assertEqual(highs["objective"], 1)
        self.assertIn(highs["solution"], exact["all_optima"])
        result = portfolio(model)
        self.assertTrue(result["concordance"], result)
        self.assertEqual(result["objective"], 1)
        self.assertIn(result["solution"], exact["all_optima"])

    def test_combined_exclusion_budget_and_exact_cardinality(self):
        model = proposed_model([5, 4, 3], [
            [[1, 1, 0], "<=", 1],
            [[4, 3, 2], "<=", 5],
            [[1, 1, 1], "==", 2],
        ])
        result = portfolio(model)
        self.assertTrue(result["concordance"], result)
        self.assertEqual(result["objective"], 7)
        self.assertEqual(result["solution"], [0, 1, 1])
        self.assertEqual(len(result["solvers"]), 2)
        selected = next(r for r in result["solvers"]
                        if r["solver"] == result["selected_solver"])
        self.assertEqual(result["selected_solver_seconds"], selected["seconds"])
        self.assertGreaterEqual(result["total_portfolio_seconds"],
                                sum(r["seconds"] for r in result["solvers"]))

    def test_integer_constraint_is_not_a_continuous_relaxation(self):
        model = proposed_model([1, 1, 1], [[[2, 2, 2], "<=", 3]])
        result = scipy_highs_milp(model)
        self.assertEqual(result["status"], "optimal", result)
        self.assertEqual(result["objective"], 1)
        self.assertTrue(model_feasible(model, result["solution"]))
        self.assertEqual(sum(result["solution"]), 1)

    def test_negative_objective_and_lower_bound(self):
        model = proposed_model([-1, -2], [[[1, 1], ">=", 1]])
        result = portfolio(model)
        self.assertTrue(result["concordance"], result)
        self.assertEqual(result["objective"], -1)
        self.assertEqual(result["solution"], [1, 0])

    def test_infeasible_models_concord_without_inventing_optimum(self):
        model = proposed_model([1, 1], [
            [[1, 1], ">=", 1], [[1, 1], "<=", 0],
        ])
        result = portfolio(model)
        self.assertTrue(result["concordance"], result)
        self.assertEqual([r["status"] for r in result["solvers"]],
                         ["infeasible", "infeasible"])
        self.assertIsNone(result["objective"])
        self.assertIsNone(result["solution"])

    def test_empty_constraint_list_preserves_binary_bounds(self):
        result = portfolio(proposed_model([4, 3], []))
        self.assertTrue(result["concordance"], result)
        self.assertEqual(result["objective"], 7)
        self.assertEqual(result["solution"], [1, 1])

    def test_zero_optimum_is_kept_as_a_feasible_optimum(self):
        result = portfolio(proposed_model([0, 0], [[[1, 1], ">=", 1]]))
        self.assertTrue(result["concordance"], result)
        self.assertEqual(result["objective"], 0)
        self.assertIsNotNone(result["solution"])
        self.assertGreaterEqual(sum(result["solution"]), 1)


if __name__ == "__main__":
    unittest.main()
