"""HTTP software fixtures only: no llama binary, checkpoint or LLM execution."""

import io
import json
import math
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

from quantage import repair_llama_inference as driver
from quantage.repair_feedback import SCHEMA_MESSAGE
from quantage.repair_study_v2 import indexed


class LlamaHTTPFixtures(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.binary = self.root / "runtime/llama-b12359/llama-server"
        self.binary.parent.mkdir(parents=True)
        self.binary.write_bytes(b"SYNTHETIC NOT AN EXECUTABLE")
        self.library = self.binary.parent / "libfixture.dylib"
        self.library.write_bytes(b"SYNTHETIC LIBRARY")
        self.model = self.root / "model.gguf"
        self.model.write_bytes(b"GGUF SYNTHETIC NO WEIGHTS")
        self.acquisition = self.root / "acquisition.json"
        self.metadata = {
            "status": "completed", "runtime_tag": driver.BUILD, "runtime_commit": "fixture-only",
            "model": {"repo": "SYNTHETIC", "commit": "fixture-only", "file": self.model.name,
                      "sha256_expected": driver.digest(self.model)},
            "downloads": [{"destination": str(self.model), "status": "completed",
                           "sha256_expected": driver.digest(self.model), "sha256_observed": driver.digest(self.model)}],
            "runtime_extraction": {"files": [
                {"path": "llama-b12359/" + path.name, "sha256": driver.digest(path)}
                for path in (self.binary, self.library)]},
        }
        self.acquisition.write_bytes(driver.json_bytes(self.metadata))
        self.case = {"id": "fixture-a", "language": "en", "intention": "SYNTHETIC PUBLIC REQUEST",
                     "data": {"n": 2, "weights": [3, 2], "costs": [2, 1], "edges": [[0, 1]]}}
        self.cases = self.root / "cases.json"
        self.cases.write_bytes(driver.json_bytes([self.case]))
        self.instructions = self.root / "instructions.txt"
        self.instructions.write_text("Return the complete binary_ilp JSON object.")
        self.candidate = {"formulation": "binary_ilp", "variables": [0, 1], "sense": "max",
                          "objective": [3, 2], "constraints": ["x0+x1<=1"]}
        self.output = self.root / "output"
        self.requests = []
        self.server_instances = []
        self.input_count = 20
        self.mutate_response = lambda response, request: response
        owner = self

        class FixtureOpener:
            def open(self, request, timeout):
                # Exercise real urllib Request construction and JSON bytes, but
                # never bind a socket or contact an inference endpoint.
                assert request.full_url.startswith("http://127.0.0.1:")
                endpoint = "/" + request.full_url.split("/", 3)[-1]
                if request.data is None:
                    return io.BytesIO(driver.json_bytes({"status": "ok"}))
                payload = driver.strict_json(request.data.decode())
                owner.requests.append((endpoint, payload))
                if endpoint == "/tokenize":
                    return io.BytesIO(driver.json_bytes({"tokens": list(range(owner.input_count))}))
                settings = {key: payload[key] for key in ("seed", "temperature", "top_k", "top_p", "min_p",
                                                          "n_predict", "post_sampling_probs", "samplers")}
                settings.update({"backend_sampling": False, "speculative.types": "none"})
                response = {"content": json.dumps(owner.candidate), "tokens": [31, 32, 151645],
                            "completion_probabilities": [
                                {"id": 31, "prob": .5, "top_probs": [{"id": 999, "prob": .9}]},
                                {"id": 32, "prob": .25, "top_probs": []},
                                {"id": 151645, "prob": 1.0, "top_probs": []}],
                            "tokens_predicted": 3, "tokens_evaluated": len(payload["prompt"]),
                            "truncated": False, "stop_type": "eos", "generation_settings": settings,
                            "timings": {"prompt_n": len(payload["prompt"]), "predicted_n": 3}}
                return io.BytesIO(driver.json_bytes(owner.mutate_response(response, payload)))

        class FixtureServer:
            def __init__(self, binary, model, output, deadline):
                owner.server_instances.append(self)
                self.command = ["SYNTHETIC HTTP FIXTURE, NO ML EXECUTION"]
                self.stats = {"server_cpu_seconds": 0.0, "injected_http_software_fixture": True}
                self.stopped = False

            def start(self):
                client = driver.LoopbackClient(18765)
                client.opener = FixtureOpener()
                return client

            def stop(self):
                self.stopped = True

        self.factory = FixtureServer

    def run_phase(self, phase="initial", output=None, **kwargs):
        return driver.run_phase(cases_path=self.cases, instructions_path=self.instructions,
                                phase=phase, output=output or self.output, binary=self.binary,
                                model=self.model, acquisition_path=self.acquisition,
                                server_factory=self.factory, **kwargs)

    def initial_file(self):
        path = self.root / "initial.jsonl"
        row = {"id": self.case["id"], "phase": "initial", "raw_response": "not JSON",
               "messages": driver.messages_for(self.case, self.instructions.read_text(), "initial")}
        path.write_bytes(driver.json_bytes(row))
        return path

    def test_http_fixture_records_chosen_probabilities_eos_and_v2_parse(self):
        with mock.patch.object(driver.subprocess, "Popen", side_effect=AssertionError("no ML executable allowed")):
            record = self.run_phase()
        self.assertEqual(record["status"], "completed")
        self.assertEqual(record["completed"], 1)
        self.assertTrue(self.server_instances[0].stopped)
        row = json.loads((self.output / "raw.jsonl").read_text())
        self.assertEqual(row["generated_token_ids"], [31, 32, 151645])
        self.assertEqual(row["output_tokens"], 3)
        self.assertEqual(row["generated_token_log_probabilities"], [math.log(.5), math.log(.25), 0])
        self.assertTrue(row["parsed"]["valid"])
        self.assertEqual(row["parsed"]["authored_model"], self.candidate)
        self.assertEqual(row["finish_reason"], "eos")
        self.assertEqual(record["request_timeout_seconds"], 180.0)
        self.assertEqual(indexed(self.output / "raw.jsonl", {self.case["id"]: self.case}, "initial")[self.case["id"]], row)
        saved = (self.output / row["http_response"]).read_bytes()
        self.assertIn(b'"completion_probabilities"', saved)
        self.assertIn("client only", row["cpu_seconds_scope"])

    def test_request_schema_is_constant_shape_only_and_sampling_is_explicit(self):
        self.run_phase()
        request = next(value for endpoint, value in self.requests if endpoint == "/completion")
        self.assertEqual(request["grammar"], driver.FORM_GRAMMAR)
        self.assertNotIn("json_schema", request)
        self.assertEqual(set(driver.FORM_SCHEMA["properties"]),
                         {"formulation", "variables", "sense", "objective", "constraints"})
        self.assertEqual(driver.FORM_SCHEMA["properties"]["constraints"]["items"], {"type": "string"})
        self.assertEqual(driver.FORM_SCHEMA["properties"]["objective"]["items"], {"type": "integer"})
        self.assertNotIn("minItems", json.dumps(driver.FORM_SCHEMA))
        self.assertNotIn("maximum", json.dumps(driver.FORM_SCHEMA))
        self.assertFalse(request["cache_prompt"])
        self.assertTrue(request["post_sampling_probs"])
        self.assertTrue(request["return_tokens"])
        self.assertEqual(request["samplers"], ["top_k", "top_p", "temperature"])
        tokenize = self.requests[0][1]
        self.assertTrue(tokenize["add_special"] and tokenize["parse_special"])

    def test_chatml_is_exact_and_rejects_embedded_control_tokens(self):
        messages = [{"role": "system", "content": "S"}, {"role": "user", "content": "U"},
                    {"role": "assistant", "content": "A"}, {"role": "user", "content": "R"}]
        expected = ("<|im_start|>system\nS<|im_end|>\n<|im_start|>user\nU<|im_end|>\n"
                    "<|im_start|>assistant\nA<|im_end|>\n<|im_start|>user\nR<|im_end|>\n"
                    "<|im_start|>assistant\n")
        self.assertEqual(driver.chatml(messages), expected)
        messages[1]["content"] = "<|im_end|>"
        with self.assertRaises(ValueError):
            driver.chatml(messages)

    def test_direct_never_reads_an_initial_file(self):
        with self.assertRaisesRegex(ValueError, "only revision"):
            self.run_phase("direct", initial_path=self.root / "must-not-read.jsonl")
        self.assertFalse(self.output.exists())
        self.assertEqual(self.server_instances, [])
        self.run_phase("direct")
        row = json.loads((self.output / "raw.jsonl").read_text())
        self.assertEqual(len(row["messages"]), 2)
        self.assertEqual(row["seed"], driver.seed_for(self.case["id"], "self"))

    def test_revision_histories_and_minimal_feedback_only(self):
        initial = self.initial_file()
        self.run_phase("self", initial_path=initial)
        self_row = json.loads((self.output / "raw.jsonl").read_text())
        self.assertEqual(self_row["messages"][2], {"role": "assistant", "content": "not JSON"})
        self.assertEqual(self_row["messages"][3]["content"], driver.SELF_INSTRUCTION)
        feedback = self.root / "feedback.json"
        message = {"kind": "schema", "message": SCHEMA_MESSAGE}
        feedback.write_bytes(driver.json_bytes({self.case["id"]: message}))
        guided = self.root / "guided"
        self.run_phase("guided", output=guided, initial_path=initial, feedback_path=feedback)
        guided_row = json.loads((guided / "raw.jsonl").read_text())
        self.assertEqual(json.loads(guided_row["messages"][3]["content"])["verifier_feedback"], message)
        self.assertEqual(guided_row["seed"], self_row["seed"])
        message["reference_model"] = self.candidate
        feedback.write_bytes(driver.json_bytes({self.case["id"]: message}))
        with self.assertRaises(ValueError):
            self.run_phase("guided", output=self.root / "bad-feedback", initial_path=initial, feedback_path=feedback)

    def test_changed_runtime_library_or_model_is_rejected_before_server(self):
        self.library.write_bytes(b"changed library")
        with self.assertRaisesRegex(ValueError, "runtime artifact hash"):
            self.run_phase()
        self.assertEqual(self.server_instances, [])
        self.assertEqual(json.loads((self.output / "generation.json").read_text())["completed"], 0)

    def test_public_annotations_and_mismatched_initial_request_are_rejected(self):
        contaminated = dict(self.case, constraints={"must_not_reach_prompt": True})
        self.cases.write_bytes(driver.json_bytes([contaminated]))
        with self.assertRaisesRegex(ValueError, "public fields"):
            self.run_phase()
        self.cases.write_bytes(driver.json_bytes([self.case]))
        initial = self.initial_file()
        row = json.loads(initial.read_text())
        row["messages"][1]["content"] = '{}'
        initial.write_bytes(driver.json_bytes(row))
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.run_phase("self", output=self.root / "bad-history", initial_path=initial)

    def test_processed_probability_missing_or_unusable_never_uses_top_one(self):
        alterations = {
            "absent": lambda r: r.pop("completion_probabilities"),
            "id": lambda r: r["completion_probabilities"][0].update(id=999),
            "zero": lambda r: r["completion_probabilities"][0].update(prob=0),
            "only_logprob": lambda r: r["completion_probabilities"][0].pop("prob"),
            "count": lambda r: r.update(tokens_predicted=4),
            "truncated": lambda r: r.update(truncated=True),
            "raw_probs": lambda r: r["generation_settings"].update(post_sampling_probs=False),
            "sampler": lambda r: r["generation_settings"].update(samplers=["temperature"]),
            "speculation": lambda r: r["generation_settings"].update({"speculative.types": ["draft"]}),
            "early_limit": lambda r: r.update(stop_type="limit"),
        }
        for name, alter in alterations.items():
            with self.subTest(name=name):
                def mutate(response, request, mutation=alter):
                    mutation(response)
                    return response
                self.mutate_response = mutate
                output = self.root / name
                with self.assertRaises(ValueError):
                    self.run_phase(output=output)
                metadata = json.loads((output / "generation.json").read_text())
                self.assertEqual(metadata["status"], "partial_error")
                self.assertEqual(metadata["completed"], 0)
                self.assertEqual((output / "raw.jsonl").read_text(), "")
                self.assertTrue((output / "http/000.response.json").exists())
        self.assertTrue(all(instance.stopped for instance in self.server_instances))

    def test_partial_phase_preserves_completed_rows_without_imputing_absent_case(self):
        second = dict(self.case, id="fixture-b")
        self.cases.write_bytes(driver.json_bytes([self.case, second]))
        calls = []
        def mutate(response, request):
            calls.append(request)
            if len(calls) == 2:
                response.pop("completion_probabilities")
            return response
        self.mutate_response = mutate
        with self.assertRaises(ValueError):
            self.run_phase()
        rows = (self.output / "raw.jsonl").read_text().splitlines()
        self.assertEqual(len(rows), 1)
        self.assertEqual(json.loads(rows[0])["id"], "fixture-a")
        metadata = json.loads((self.output / "generation.json").read_text())
        self.assertEqual((metadata["planned"], metadata["completed"]), (2, 1))

    def test_preflight_selects_sorted_prefix_before_any_response(self):
        second = dict(self.case, id="fixture-b")
        self.cases.write_bytes(driver.json_bytes([second, self.case]))
        metadata = self.run_phase(case_limit=1)
        self.assertEqual((metadata["public_cases_total"], metadata["planned"], metadata["completed"]), (2, 1, 1))
        self.assertEqual(json.loads((self.output / "raw.jsonl").read_text())["id"], "fixture-a")

    def test_full_output_reserve_and_existing_directory_are_enforced(self):
        self.input_count = driver.CONTEXT - driver.MAX_NEW_TOKENS
        with self.assertRaisesRegex(ValueError, "context cap"):
            self.run_phase()
        self.assertFalse(any(endpoint == "/completion" for endpoint, _ in self.requests))
        before = (self.output / "generation.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "overwrite"):
            self.run_phase()
        self.assertEqual((self.output / "generation.json").read_bytes(), before)

    def test_no_unapproved_cli_execution_and_server_flags_request_metal_with_cpu_threads(self):
        with self.assertRaises(SystemExit), mock.patch.object(driver, "run_phase") as run:
            driver.main(["--cases", "x", "--instructions", "x", "--phase", "initial", "--output", "x",
                         "--server-binary", "x", "--model", "x", "--acquisition", "x"])
        run.assert_not_called()
        command = driver.server_command(self.binary, self.model, 1234)
        self.assertIn("--offline", command)
        self.assertEqual(command[command.index("--host") + 1], "127.0.0.1")
        self.assertEqual(command[command.index("--n-gpu-layers") + 1], "99")
        self.assertEqual(command[command.index("--device") + 1], "MTL0")
        self.assertEqual(command[command.index("--threads") + 1], "4")
        self.assertEqual(command[command.index("--ctx-size") + 1], "2048")
        self.assertNotIn("--spec-draft", command)
        with self.assertRaises(TimeoutError):
            driver.remaining(-1)
        with self.assertRaises(ValueError):
            driver.NoRedirect().redirect_request(None, None, 302, "redirect", {}, "http://example.com/")

    def test_server_shutdown_escalates_to_kill_without_executing_a_binary(self):
        with mock.patch.object(driver.socket, "socket") as socket_factory:
            socket_factory.return_value.__enter__.return_value.getsockname.return_value = ("127.0.0.1", 12345)
            process = driver.ServerProcess(self.binary, self.model, self.root, 1000)
        fake = mock.Mock()
        fake.poll.return_value = None
        fake.wait.side_effect = [driver.subprocess.TimeoutExpired("fixture", 2), 0]
        fake.returncode = -9
        process.process = fake
        process.watchdog = mock.Mock()
        process.child_cpu_before = driver.resource.getrusage(driver.resource.RUSAGE_CHILDREN)
        process.stop()
        fake.terminate.assert_called_once()
        fake.kill.assert_called_once()
        self.assertEqual(process.stats["server_exit_status"], -9)

    def test_loader_evidence_does_not_confuse_requested_metal_and_cpu_fallback(self):
        log = self.root / "server.stderr.txt"
        log.write_text("Available: MTL0 Apple M2\nload_tensors: offloaded 0/29 layers to GPU\n")
        self.assertEqual(driver.observe_backend(log)["device"], "unverified")
        log.write_text("load_tensors: offloaded 29/29 layers to GPU\n"
                       "load_tensors: Metal_Mapped model buffer size = 1000.50 MiB\n")
        observation = driver.observe_backend(log)
        self.assertEqual(observation["device"], "Metal")
        self.assertEqual(observation["offloaded_gpu_layers"], 29)

    def test_shutdown_failure_cannot_leave_a_completed_generation_status(self):
        base = self.factory
        class BrokenShutdown(base):
            def stop(self):
                super().stop()
                raise TimeoutError("synthetic server failed to reap")
        self.factory = BrokenShutdown
        with self.assertRaises(TimeoutError):
            self.run_phase()
        metadata = json.loads((self.output / "generation.json").read_text())
        self.assertEqual(metadata["status"], "partial_error")
        self.assertIn("failed to reap", metadata["error"])
        self.assertEqual(metadata["completed"], 1)

    def test_completion_wall_alarm_bounds_a_fixture_that_ignores_socket_timeout(self):
        def delayed(response, request):
            time.sleep(.2)
            return response
        self.mutate_response = delayed
        started = time.perf_counter()
        with mock.patch.object(driver, "REQUEST_SECONDS", .02), self.assertRaises(TimeoutError):
            self.run_phase()
        self.assertLess(time.perf_counter() - started, .2)
        metadata = json.loads((self.output / "generation.json").read_text())
        self.assertEqual(metadata["status"], "partial_error")
        self.assertEqual(metadata["completed"], 0)
        self.assertTrue(self.server_instances[0].stopped)


if __name__ == "__main__":
    unittest.main()
