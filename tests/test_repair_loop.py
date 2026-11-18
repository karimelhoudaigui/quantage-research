"""Deterministic controller fixtures, never measured LLM performance."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from quantage.repair_feedback import SCHEMA_MESSAGE
from quantage.repair_loop import run_loop


class RepairLoopSoftwareTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.case = {"id": "fixture", "intention": "Select at least one item, respect budget 2 and exclusion.",
                     "data": {"n": 2, "weights": [3, 2], "costs": [2, 1], "edges": [[0, 1]]}}
        self.reference = {"budget": 2, "min_count": 1, "max_count": None,
                          "required": [], "forbidden": [], "implications": []}
        self.good = {"formulation": "binary_ilp", "variables": [0, 1], "sense": "max",
                     "objective": [3, 2], "constraints": [
                         "x0+x1<=1", "2*x0+x1<=2", "x0+x1>=1"]}
        self.bad = copy.deepcopy(self.good)
        self.bad["constraints"] = []
        self.cases = self.root / "cases.json"
        self.gold = self.root / "gold.json"
        self.instructions = self.root / "instructions.txt"
        self.instructions.write_text("Return an explicit binary_ilp model.")
        self._write_inputs()

    def _write_inputs(self):
        self.cases.write_text(json.dumps([self.case]))
        self.gold.write_text(json.dumps([{"id": "fixture", "constraints": self.reference,
                                         "private_annotation": "never pass this to inference"}]))

    def _record(self, model):
        return {"id": "fixture", "raw_response": json.dumps(model) if not isinstance(model, str) else model}

    def _run(self, generator, **kwargs):
        return run_loop(self.cases, self.gold, "fixture", self.instructions,
                        self.root / "output", generator=generator, **kwargs)

    def test_counterexample_is_used_and_success_stops_early(self):
        calls = []

        def generate(**call):
            calls.append(call)
            self.assertNotIn("gold_path", call)
            self.assertEqual(call["case"], self.case)
            self.assertEqual(json.loads(call["cases_path"].read_text()), [self.case])
            if len(calls) == 1:
                self.assertEqual(call["phase"], "initial")
                self.assertIsNone(call["feedback_path"])
                return self._record(self.bad)
            self.assertEqual(call["phase"], "guided")
            feedback = json.loads(call["feedback_path"].read_text())["fixture"]
            self.assertEqual(feedback["kind"], "counterexamples")
            self.assertTrue(any(w["x"] == [0, 0] for w in feedback["witnesses"]))
            self.assertNotIn("constraints", feedback)
            previous = json.loads(call["previous_record_path"].read_text())
            self.assertEqual(json.loads(previous["raw_response"]), self.bad)
            return self._record(self.good)

        result = self._run(generate, max_repairs=3)
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["status"], "exact")
        self.assertTrue(result["usable_for_original"])
        self.assertEqual(result["objective"], 3)
        self.assertEqual(result["inference_mode"], "injected_software_fixture")
        self.assertEqual(len(result["iterations"]), 2)
        saved = json.loads((self.root / "output/iteration-01/proposal.jsonl").read_text())
        self.assertEqual(json.loads(saved["raw_response"])["constraints"], self.good["constraints"])

    def test_faithful_initial_model_needs_no_repair(self):
        calls = []

        def generate(**call):
            calls.append(call)
            return self._record(self.good)

        result = self._run(generate, max_repairs=3)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["status"], "exact")
        self.assertEqual(result["stop_reason"], "finite_certificate")

    def test_zero_repair_budget_still_solves_candidate_without_certifying_original(self):
        result = self._run(lambda **_: self._record(self.bad), max_repairs=0)
        self.assertEqual(result["status"], "repair_budget_exhausted")
        self.assertFalse(result["usable_for_original"])
        self.assertIsNone(result["objective"])
        self.assertTrue(result["portfolio"]["concordance"])
        self.assertEqual(result["portfolio"]["objective"], 5)

    def test_invalid_model_uses_only_closed_schema_feedback(self):
        calls = []

        def generate(**call):
            calls.append(call)
            if len(calls) == 1:
                return self._record("not JSON; no corrected model belongs in feedback")
            feedback = json.loads(call["feedback_path"].read_text())["fixture"]
            self.assertEqual(feedback, {"kind": "schema", "message": SCHEMA_MESSAGE})
            return self._record(self.good)

        self.assertEqual(self._run(generate)["status"], "exact")

    def test_infeasible_reference_is_a_successful_exact_outcome(self):
        self.reference["max_count"] = 0
        self._write_inputs()
        impossible = copy.deepcopy(self.good)
        impossible["constraints"].append([[1, 1], "<=", 0])
        result = self._run(lambda **_: self._record(impossible))
        self.assertEqual(result["status"], "infeasible")
        self.assertTrue(result["usable_for_original"])
        self.assertIsNone(result["solution"])

    def test_initial_trace_fixture_reused_without_source_mutation(self):
        source = self.root / "source.jsonl"
        row = self._record(self.bad)
        row.update({"output_tokens": 1, "generated_token_ids": [1], "messages": [
            {"role": "system", "content": self.instructions.read_text()},
            {"role": "user", "content": json.dumps({"intention": self.case["intention"], "data": self.case["data"]})}]})
        source.write_text(json.dumps(row) + "\n")
        original = source.read_bytes()
        calls = []

        def generate(**call):
            calls.append(call)
            self.assertEqual(call["phase"], "guided")
            return self._record(self.good)

        result = self._run(generate, initial_records=source)
        self.assertEqual(result["status"], "exact")
        self.assertEqual(len(calls), 1)
        self.assertTrue(result["initial_record_reused"])
        self.assertEqual(source.read_bytes(), original)
        self.assertEqual((self.root / "output/initial_source.jsonl").read_bytes(), original)

    def test_timeout_stops_without_fabricated_generation_or_solver_results(self):
        def generate(**_):
            raise TimeoutError("software fixture timeout")

        result = self._run(generate)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["stop_reason"], "time_limit")
        self.assertEqual(result["iterations"], [])
        self.assertIsNone(result["portfolio"])
        self.assertTrue((self.root / "output/result.json").is_file())

    def test_repair_limit_and_existing_output_are_rejected_before_generation(self):
        def never(**_):
            self.fail("generator must not be called")

        with self.assertRaises(ValueError):
            self._run(never, max_repairs=4)
        output = self.root / "output"
        output.mkdir()
        sentinel = output / "preserve.txt"
        sentinel.write_text("existing result")
        with self.assertRaises(ValueError):
            self._run(never)
        self.assertEqual(sentinel.read_text(), "existing result")

    def test_reused_trace_must_match_public_request_not_just_id(self):
        source = self.root / "source.jsonl"
        row = self._record(self.good)
        row.update({"output_tokens": 1, "generated_token_ids": [1], "messages": [
            {"role": "system", "content": self.instructions.read_text()},
            {"role": "user", "content": json.dumps({"intention": "different request", "data": self.case["data"]})}]})
        source.write_text(json.dumps(row) + "\n")
        with self.assertRaises(ValueError):
            self._run(lambda **_: self._record(self.good), initial_records=source)


if __name__ == "__main__":
    unittest.main()
