"""C19 development-only operational loop with one repair and a reused initial.

This controller uses the frozen linear llama.cpp driver and pinned C19 paths.
It never samples a new initial: one matching recorded initial is required.
The trusted reference is read only by this controller, never by inference.
Only the public request, previous raw proposal and closed feedback are sent.
Run the real GPU flow only through the authorized outer 1800-second process-
group watchdog; CLI --execute is required. No model was run by this module's
author. This new adaptation has self-review only, not independent review.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

from .repair_feedback import feedback_for_model, validate_feedback
from .repair_language import parse_proposal
from .repair_model import verify_model


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAX_SECONDS = 1800.0
DRIVER_MODULE = "quantage.repair_llama_linear"
SERVER_BINARY = PROJECT_ROOT / "research/external/c16-public/runtime/llama-b12359/llama-server"
MODEL_PATH = PROJECT_ROOT / "research/external/c19-public/models/Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf"
ACQUISITION_PATH = PROJECT_ROOT / "runs/20261115-c19-instruct-repair/acquisition.json"
DEFAULT_INITIAL_RECORDS = PROJECT_ROOT / "runs/20261115-c19-instruct-repair/development-remaining-v1/driver/raw.jsonl"
REFERENCE_FIELDS = {"budget", "min_count", "max_count", "required", "forbidden", "implications"}


def _dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def _unique_rows(path):
    rows = json.loads(path.read_text())
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("cases and gold must be JSON lists of objects")
    indexed = {}
    for row in rows:
        identity = row.get("id")
        if not isinstance(identity, str) or identity in indexed:
            raise ValueError("missing or duplicate case ID")
        indexed[identity] = row
    return indexed


def _selected_inputs(cases_path, gold_path, case_id):
    public = _unique_rows(cases_path)
    reference = _unique_rows(gold_path)
    if case_id not in public or case_id not in reference:
        raise ValueError("selected ID must occur exactly once in cases and gold")
    source = public[case_id]
    data = source.get("data")
    if not isinstance(source.get("intention"), str) or not isinstance(data, dict):
        raise ValueError("public request requires intention and data")
    if set(data) != {"n", "weights", "costs", "edges"}:
        raise ValueError("unexpected public data fields")
    n = data["n"]
    if type(n) is not int or not 1 <= n <= 7:
        raise ValueError("finite domain requires 1 <= n <= 7")
    for key in ("weights", "costs"):
        if (type(data[key]) is not list or len(data[key]) != n
                or any(type(x) is not int or not 0 < x <= 10000 for x in data[key])):
            raise ValueError("invalid public coefficients")
    contract = reference[case_id].get("constraints")
    if not isinstance(contract, dict) or set(contract) != REFERENCE_FIELDS:
        raise ValueError("invalid trusted reference schema")
    for key in ("budget", "min_count", "max_count"):
        if contract[key] is not None and (type(contract[key]) is not int or contract[key] < 0):
            raise ValueError("invalid reference bound")
    for pairs in (data["edges"], contract["implications"]):
        if type(pairs) is not list or any(
            type(pair) is not list or len(pair) != 2
            or any(type(i) is not int or not 0 <= i < n for i in pair) for pair in pairs
        ):
            raise ValueError("invalid edge or implication")
    for key in ("required", "forbidden"):
        if type(contract[key]) is not list or any(type(i) is not int or not 0 <= i < n for i in contract[key]):
            raise ValueError("invalid required or forbidden index")
    # Whitelist the request: no private labels or incidental corpus metadata.
    if source.get("language") not in ("fr", "en"):
        raise ValueError("public language must be fr or en")
    case = {"id": case_id, "language": source["language"], "intention": source["intention"], "data": data}
    return case, contract


def _remaining(deadline):
    remaining = deadline - time.perf_counter()
    if remaining <= 0:
        raise TimeoutError("global 1800-second loop budget exhausted")
    return remaining


def _matching_trace(path, case, instructions):
    matching = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if isinstance(row, dict) and row.get("id") == case["id"]:
            matching.append((row, line))
    if len(matching) != 1:
        raise ValueError("initial-records must contain one unique matching observation")
    row, source_line = matching[0]
    if row.get("phase") != "initial":
        raise ValueError("only an actually recorded initial phase may be reused")
    _validate_record(row, case, instructions, real=True)
    return row, source_line


def _validate_record(row, case, instructions, real):
    if (not isinstance(row, dict) or row.get("id") != case["id"]
            or not isinstance(row.get("raw_response"), str)):
        raise ValueError("generation must return one matching raw response")
    parsed = parse_proposal(row["raw_response"], case["data"]["n"])
    if "parsed" in row and row["parsed"] != parsed:
        raise ValueError("saved parse does not match the raw generation")
    if real:
        tokens = row.get("generated_token_ids")
        if (type(row.get("output_tokens")) is not int or not 0 < row["output_tokens"] <= 512
                or type(tokens) is not list or len(tokens) != row["output_tokens"]
                or any(type(token) is not int or token < 0 for token in tokens)):
            raise ValueError("reused/real observation requires recorded generated tokens")
        messages = row.get("messages")
        if not isinstance(messages, list) or len(messages) < 2:
            raise ValueError("recorded prompt is missing")
        if messages[0] != {"role": "system", "content": instructions}:
            raise ValueError("recorded system instructions differ")
        if not isinstance(messages[1], dict) or messages[1].get("role") != "user":
            raise ValueError("recorded public request is missing")
        prompt_request = json.loads(messages[1]["content"])
        if prompt_request != {"intention": case["intention"], "data": case["data"]}:
            raise ValueError("recorded public request differs despite matching ID")
    return parsed


def _real_generator(*, case, cases_path, instructions_path, phase,
                    previous_record_path, feedback_path, output_dir, timeout):
    """Invoke only the fixed C19 driver, sharing the outer watchdog's group."""
    if phase != "guided" or previous_record_path is None or feedback_path is None:
        raise ValueError("this controller only generates one guided repair of a recorded initial")
    for path in (SERVER_BINARY, MODEL_PATH, ACQUISITION_PATH):
        if not path.is_file():
            raise RuntimeError("pinned C19 artifact is missing; no acquisition or retry here")
    output_dir.mkdir()
    driver_output = output_dir / "driver"
    command = [sys.executable, "-m", DRIVER_MODULE,
               "--cases", str(cases_path), "--instructions", str(instructions_path),
               "--phase", "guided", "--output", str(driver_output), "--max-new-tokens", "512",
               "--initial", str(previous_record_path), "--feedback", str(feedback_path),
               "--server-binary", str(SERVER_BINARY), "--model", str(MODEL_PATH),
               "--acquisition", str(ACQUISITION_PATH), "--execute"]
    _dump(output_dir / "command.json", command)
    with (output_dir / "stdout.txt").open("x") as stdout, (output_dir / "stderr.txt").open("x") as stderr:
        # Do not detach: the outer watchdog owns controller, driver and server.
        process = subprocess.Popen(command, cwd=str(PROJECT_ROOT), stdout=stdout, stderr=stderr)
        try:
            returncode = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
            raise TimeoutError("C19 repair subprocess exceeded the remaining loop budget") from exc
    if returncode != 0:
        raise RuntimeError("inference process failed with exit code " + str(returncode))
    records = [json.loads(line) for line in (driver_output / "raw.jsonl").read_text().splitlines() if line.strip()]
    if len(records) != 1 or records[0].get("id") != case["id"]:
        raise ValueError("inference did not record exactly the selected case")
    return records[0]


def _portfolio_process(model, output, deadline):
    """Keep the portfolio, including imports, inside the global hard timeout."""
    model_path = output / "final_model.json"
    result_path = output / "portfolio.json"
    _dump(model_path, model)
    command = [sys.executable, "-m", "quantage.repair_loop_linear", "_portfolio",
               str(model_path), str(result_path)]
    _dump(output / "portfolio_command.json", command)
    with (output / "portfolio_stdout.txt").open("x") as stdout, (output / "portfolio_stderr.txt").open("x") as stderr:
        completed = subprocess.run(command, cwd=str(PROJECT_ROOT), stdout=stdout,
                                   stderr=stderr, timeout=_remaining(deadline), check=False)
    if completed.returncode != 0:
        raise RuntimeError("portfolio process failed with exit code " + str(completed.returncode))
    return json.loads(result_path.read_text())


def run_loop(cases_path, gold_path, case_id, instructions_path, output,
             max_repairs=1, initial_records=DEFAULT_INITIAL_RECORDS, generator=None,
             time_budget_seconds=MAX_SECONDS, execute=False):
    """Run one case. An injected generator is labelled software-only evidence."""
    started = time.perf_counter()
    if type(max_repairs) is not int or not 0 <= max_repairs <= 1:
        raise ValueError("max_repairs must be an integer from 0 to 1")
    if (isinstance(time_budget_seconds, bool) or not isinstance(time_budget_seconds, (int, float))
            or not math.isfinite(time_budget_seconds) or not 0 < time_budget_seconds <= MAX_SECONDS):
        raise ValueError("time budget must be positive and at most 1800 seconds")
    if initial_records is None:
        raise ValueError("a recorded initial is required; initial resampling is forbidden")
    if generator is None and execute is not True:
        raise ValueError("execute=True is required for a real GPU repair")
    deadline = started + time_budget_seconds
    cases_path, gold_path, instructions_path = map(Path, (cases_path, gold_path, instructions_path))
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("output must be a new directory")
    case, contract = _selected_inputs(cases_path, gold_path, case_id)
    instructions = instructions_path.read_text()
    source = _matching_trace(Path(initial_records), case, instructions) if initial_records is not None else None
    output.mkdir(parents=True)
    public_path = output / "public_case.json"
    frozen_instructions = output / "instructions.txt"
    _dump(public_path, [case])
    frozen_instructions.write_text(instructions)
    _dump(output / "inputs.json", {
        "id": case_id,
        "public_cases_sha256": hashlib.sha256(cases_path.read_bytes()).hexdigest(),
        "reference_sha256": hashlib.sha256(gold_path.read_bytes()).hexdigest(),
        "instructions_sha256": hashlib.sha256(instructions.encode()).hexdigest(),
        "max_repairs": max_repairs, "time_budget_seconds": time_budget_seconds,
        "driver_module": DRIVER_MODULE,
        "server_binary": str(SERVER_BINARY), "model_path": str(MODEL_PATH),
        "acquisition_sha256": hashlib.sha256(ACQUISITION_PATH.read_bytes()).hexdigest(),
        "initial_records_sha256": hashlib.sha256(Path(initial_records).read_bytes()).hexdigest(),
        "reference_scope": "trusted annotated contract; never an inference input",
    })
    if source:
        (output / "initial_source.jsonl").write_text(source[1] + "\n")
    fixture = generator is not None
    generate = generator or _real_generator
    iterations = []
    previous_path = feedback_path = None
    parsed = report = solved = None
    generation_calls = 0
    stop_reason = "repair_budget_exhausted"
    failure = None
    try:
        for index in range(max_repairs + 1):
            _remaining(deadline)
            iteration = output / ("iteration-%02d" % index)
            iteration.mkdir()
            reused = index == 0 and source is not None
            t0 = time.perf_counter()
            if reused:
                record = source[0]
            else:
                generation_calls += 1
                record = generate(case=case, cases_path=public_path,
                                  instructions_path=frozen_instructions,
                                  phase="initial" if index == 0 else "guided",
                                  previous_record_path=previous_path,
                                  feedback_path=feedback_path,
                                  output_dir=iteration / "inference",
                                  timeout=_remaining(deadline))
            generation_seconds = time.perf_counter() - t0
            _remaining(deadline)
            parsed = _validate_record(record, case, instructions, real=not fixture or reused)
            previous_path = iteration / "proposal.jsonl"
            previous_path.write_text(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
            t0 = time.perf_counter()
            report = verify_model(case["data"], contract, parsed)
            minimal = feedback_for_model(report, case["data"]["n"])
            validate_feedback(minimal, case["data"]["n"])
            feedback_path = iteration / "feedback.json"
            # The inference API accepts an ID-indexed map; nothing else is sent.
            _dump(feedback_path, {case_id: minimal})
            verification_seconds = time.perf_counter() - t0
            _dump(iteration / "verification.json", report)
            summary = {"iteration": index, "reused_initial": reused,
                       "schema_valid": parsed["valid"], "faithful": report["faithful"],
                       "generation_seconds": generation_seconds,
                       "verification_seconds": verification_seconds,
                       "feedback_kind": minimal["kind"]}
            _dump(iteration / "timings.json", summary)
            iterations.append(summary)
            _dump(output / "iterations.json", iterations)
            if report["faithful"]:
                stop_reason = "finite_certificate"
                break
        _remaining(deadline)
        if parsed is not None and parsed["valid"]:
            solved = _portfolio_process(parsed["model"], output, deadline)
        _remaining(deadline)
    except (Exception,) as exc:
        failure = type(exc).__name__ + ": " + str(exc)
        stop_reason = "time_limit" if isinstance(exc, (TimeoutError, subprocess.TimeoutExpired)) else "execution_error"
    usable = bool(failure is None and report and report["faithful"]
                  and solved and solved["concordance"])
    if failure is not None:
        status = "blocked"
    elif usable:
        status = "infeasible" if solved["solvers"][0]["status"] == "infeasible" else "exact"
    else:
        status = "repair_budget_exhausted"
        if report and report["faithful"]:
            stop_reason = "portfolio_not_concordant"
    result = {"id": case_id, "status": status, "stop_reason": stop_reason,
              "usable_for_original": usable, "objective": solved["objective"] if usable else None,
              "solution": solved["solution"] if usable else None,
              "iterations": iterations, "max_repairs": max_repairs,
              "generation_calls_attempted": generation_calls,
              "initial_record_reused": source is not None,
              "initial_resampling_permitted": False,
              "historical_initial_calls_reused": 1,
              "driver_module": DRIVER_MODULE,
              "outer_process_group_watchdog_required_seconds": 1800,
              "review_independence": "self_review_only_for_this_new_controller",
              "demonstration_scope": "development operational demonstration, separate from C19 held-out comparison",
              "inference_mode": "injected_software_fixture" if fixture else "real_subprocess",
              "final_verification": report, "portfolio": solved,
              "error": failure, "wall_seconds": time.perf_counter() - started,
              "time_budget_seconds": time_budget_seconds,
              "scope": "finite structured oracle; no arbitrary-NL certificate or QPU execution"}
    _dump(output / "result.json", result)
    return result


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "_portfolio":
        if len(argv) != 3:
            raise ValueError("internal portfolio expects model and result paths")
        from .repair_solvers import portfolio
        _dump(Path(argv[2]), portfolio(json.loads(Path(argv[1]).read_text())))
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--id", required=True)
    parser.add_argument("--instructions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-repairs", type=int, default=1, choices=range(2))
    parser.add_argument("--initial-records", type=Path, default=DEFAULT_INITIAL_RECORDS)
    parser.add_argument("--execute", action="store_true")

    args = parser.parse_args(argv)
    if not args.execute:
        parser.error("--execute is required for the real GPU loop; run only under the outer watchdog")
    result = run_loop(args.cases, args.gold, args.id, args.instructions, args.output,
                      max_repairs=args.max_repairs, initial_records=args.initial_records, execute=True)
    print(json.dumps({key: result[key] for key in
                      ("id", "status", "usable_for_original", "generation_calls_attempted", "wall_seconds")},
                     allow_nan=False))
    return 0 if result["usable_for_original"] else 2


if __name__ == "__main__":
    sys.exit(main())
