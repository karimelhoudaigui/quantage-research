"""Exact algebra, parser boundaries and rejected execution syntax; no LLM mocks."""

import itertools
import json
import unittest

from quantage.repair_language import compile_constraint, parse_proposal
from quantage.repair_model import model_feasible, parse_model


def authored(constraints):
    return {"formulation": "binary_ilp", "variables": [0, 1, 2], "sense": "max",
            "objective": [7, 4, 5], "constraints": constraints}


class LinearLanguageTests(unittest.TestCase):
    def test_both_sides_constants_and_signs_are_rearranged_exactly(self):
        cases = [
            ("3*x0+2*x1<=7", [[3, 2, 0], "<=", 7]),
            ("3*x0+2<=x1+7", [[3, -1, 0], "<=", 5]),
            ("7>=3*x0+2*x1", [[-3, -2, 0], ">=", -7]),
            ("x0-x1==2-3*x1", [[1, 2, 0], "==", 2]),
            ("-(x0-2*x2)+1 >= -x1-3", [[-1, 1, 2], ">=", -4]),
            ("(2+3)*(x0+1)<=9", [[5, 0, 0], "<=", 4]),
            ("x2==1", [[0, 0, 1], "==", 1]),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(compile_constraint(text, 3), expected)

    def test_aliases_refer_to_the_same_declared_variable(self):
        self.assertEqual(compile_constraint("x0+x_0+x[0]-x1<=2", 3),
                         [[3, -1, 0], "<=", 2])
        for text in ("x01<=1", "x_01<=1", "x3<=1", "y0<=1", "x[-1]<=1", "x[1+1]<=1"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                compile_constraint(text, 3)

    def test_unicode_relations_and_single_equal_are_only_notation_changes(self):
        self.assertEqual(compile_constraint("x0+x_1≤1", 3), [[1, 1, 0], "<=", 1])
        self.assertEqual(compile_constraint("x[2]≥1", 3), [[0, 0, 1], ">=", 1])
        self.assertEqual(compile_constraint("x2=1", 3), [[0, 0, 1], "==", 1])

    def test_string_truth_table_matches_independent_direct_arithmetic(self):
        strings = ["2*x0+x1<=3-x2", "x2-x0<=0", "x1+x2>=1"]
        parsed = parse_proposal(json.dumps(authored(strings)), 3)
        self.assertTrue(parsed["valid"], parsed)
        for x in itertools.product((0, 1), repeat=3):
            expected = 2*x[0] + x[1] <= 3-x[2] and x[2]-x[0] <= 0 and x[1]+x[2] >= 1
            self.assertEqual(model_feasible(parsed["model"], x), expected)

    def test_authored_model_and_row_count_are_preserved_without_missing_clause_repair(self):
        source = authored(["x0+x1<=1", [[0, 0, 1], ">=", 1]])
        parsed = parse_proposal(json.dumps(source), 3)
        self.assertTrue(parsed["valid"], parsed)
        self.assertEqual(parsed["authored_model"], source)
        self.assertEqual(len(parsed["model"]["constraints"]), len(source["constraints"]))
        self.assertEqual(parsed["model"]["objective"], source["objective"])
        self.assertEqual(parsed["model"]["variables"], source["variables"])
        self.assertEqual(parsed["model"]["constraints"][1], source["constraints"][1])
        self.assertEqual(source["constraints"][0], "x0+x1<=1")

    def test_legacy_valid_and_invalid_parse_results_are_identical(self):
        for raw in (json.dumps(authored([[[1, 1, 0], "<=", 1]])), "invalid JSON",
                    json.dumps(authored([[[0, 1], "<=", 1]])),
                    '{"variables":[],"variables":[]}'):
            with self.subTest(raw=raw):
                self.assertEqual(parse_proposal(raw, 3), parse_model(raw, 3))

    def test_unsupported_or_executable_syntax_is_rejected(self):
        expressions = [
            "__import__('os').system('echo no')<=0", "sum([x0,x1])<=1", "x0.real<=1",
            "x0*x1<=1", "(x0-x0)*x1<=1", "0*x0*x1<=1", "x0**2<=1",
            "x0/2<=1", "x0//2<=1", "x0%2<=1", "x0^1<=1", "~x0<=1",
            "x[True]<=1", "x[0.0]<=1", "x['0']<=1", "x[0:1]<=1", "y[0]<=1",
            "x0<=True", "x0<=1.0", "x0<=...", "x0+x1+...+x2<=1",
            "0<=x0<=1", "x0<1", "x0!=1", "x0 is x1", "x0<=1 and x1<=1",
            "x0<=1 # ignored comment", "x0<=1; x1<=1", "x0<=1\nx1<=1",
        ]
        for expression in expressions:
            with self.subTest(expression=expression), self.assertRaises(ValueError):
                compile_constraint(expression, 3)

    def test_final_frozen_bounds_apply_after_exact_cancellation(self):
        accepted = parse_proposal(json.dumps(authored(["10001*x0-x0<=10000"])), 3)
        self.assertTrue(accepted["valid"], accepted)
        for expression in ("10001*x0<=1", "x0<=10001"):
            rejected = parse_proposal(json.dumps(authored([expression])), 3)
            self.assertFalse(rejected["valid"], rejected)
            self.assertEqual(rejected["authored_model"]["constraints"], [expression])

    def test_extra_fields_duplicate_keys_and_row_explosion_are_rejected(self):
        source = authored(["x0<=1"])
        source["read_gold"] = True
        self.assertFalse(parse_proposal(json.dumps(source), 3)["valid"])
        self.assertFalse(parse_proposal(json.dumps(authored(["x0<=1"] * 33)), 3)["valid"])
        duplicated = json.dumps(authored(["x0<=1"]))[:-1] + ',"objective":[1,2,3]}'
        self.assertFalse(parse_proposal(duplicated, 3)["valid"])
        for expression in ("x0" + "+1" * 200 + "<=1", "9" * 300 + "*x0<=1"):
            with self.subTest(expression=expression), self.assertRaises(ValueError):
                compile_constraint(expression, 3)


if __name__ == "__main__":
    unittest.main()
