"""Union eight recorded development responses; never generate or impute."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run = Path("runs/20261115-c16-quantized-repair")
    sources = [run / p / "driver" for p in ("dev-preflight-v2", "dev-remaining-v1")]
    payloads = [(p / "raw.jsonl").read_bytes() for p in sources]
    records = [json.loads(line) for payload in payloads for line in payload.splitlines()]
    expected = {r["id"] for r in json.loads((run / "dev_cases.json").read_text())}
    assert len(records) == 8 and {r["id"] for r in records} == expected
    assert len({r["id"] for r in records}) == 8 and all(r["phase"] == "initial" for r in records)
    metadata = [json.loads((p / "generation.json").read_text()) for p in sources]
    assert all(m["status"] == "completed" for m in metadata)
    assert [m["completed"] for m in metadata] == [2, 6]
    output = args.output / "driver"
    output.mkdir()
    (output / "raw.jsonl").write_bytes(b"".join(payloads))
    merged = {"status": "completed", "completed": 8, "planned": 8,
              "aggregate_of": [str(p) for p in sources],
              "scope": "union of actual 2 v1 and 6 v2 development responses, not a new inference phase or uniform-prompt estimate",
              "physical_generation_calls": 8, "phase": "initial"}
    for field in ("input_tokens", "output_tokens", "wall_seconds", "cpu_seconds",
                  "load_seconds", "client_cpu_seconds", "server_cpu_seconds"):
        merged[field] = sum(m[field] for m in metadata)
    (output / "generation.json").write_text(json.dumps(merged, indent=2) + "\n")
    print(json.dumps({"actual_records": 8, "new_generation_calls": 0}))


if __name__ == "__main__":
    main()
