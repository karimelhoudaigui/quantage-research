"""Acquire one pinned public community GGUF, reusing the verified local runtime."""
import json
from pathlib import Path
import shutil
import time
from acquire_c16_runtime import _opener, _public_json, download, acquisition_deadline

ROOT = Path(__file__).resolve().parents[1]
REPO = "SoAIHQ/Qwen3.5-2B-GGUF"
COMMIT = "377fa65bb36aa83414de1ab3b40f6f15b0324cdc"
NAME = "Qwen3.5-2B-Q4_K_M.gguf"
SHA = "a8b50de00b780c0f3c16f07cb041a1ecd678b6e22fd8cde91e57fe4b5031523b"
SIZE = 1312165056


def main():
    dest = ROOT / "research/external/c17-public-v2"
    record_path = ROOT / "runs/20261115-c17-capacity-repair/acquisition-v2.json"
    if dest.exists() or record_path.exists():
        raise ValueError("fresh acquisition paths required")
    dest.mkdir()
    record = {"status": "running", "model_execution": False, "external_purchase_eur": 0,
              "publisher": "SoAIHQ community quantization; source identity declared, conversion not reproduced"}
    start = time.monotonic()
    try:
        with acquisition_deadline(600):
            info = _public_json(_opener(), "https://huggingface.co/api/models/" + REPO +
                                "/revision/" + COMMIT + "?blobs=true")
            assert info["sha"] == COMMIT
            entry = next(x for x in info["siblings"] if x["rfilename"] == NAME)
            assert entry["lfs"]["sha256"] == SHA and entry["lfs"]["size"] == SIZE
            assert shutil.disk_usage(dest).free >= SIZE + 1024**3, "1GiB reserve required"
            prior = json.loads((ROOT / "runs/20261115-c16-quantized-repair/acquisition.json").read_text())
            record.update({k: prior[k] for k in ("runtime_tag", "runtime_commit", "runtime_extraction")})
            record["runtime_reused_from"] = "runs/20261115-c16-quantized-repair/acquisition.json"
            url = "https://huggingface.co/" + REPO + "/resolve/" + COMMIT + "/" + NAME
            record["model"] = {"repo": REPO, "commit": COMMIT, "file": NAME,
                               "sha256_expected": SHA, "size_expected": SIZE, "url": url,
                               "license": "Apache-2.0 as declared by publisher and original Qwen release"}
            record["downloads"] = []
            (dest / "models").mkdir()
            download(_opener(), url, dest / "models" / NAME, SHA, SIZE, record["downloads"], size_expected=SIZE)
            record["free_after_bytes"] = shutil.disk_usage(dest).free
            record["status"] = "completed"
    except BaseException as exc:
        record["status"] = "failed"
        record["error"] = type(exc).__name__ + ": " + str(exc)
        raise
    finally:
        record["elapsed_seconds"] = time.monotonic() - start
        text = json.dumps(record, indent=2) + "\n"
        record_path.write_text(text)
        (dest / "acquisition.json").write_text(text)
    print(json.dumps({"status": record["status"], "seconds": record["elapsed_seconds"],
                      "free_after_bytes": record["free_after_bytes"]}))


if __name__ == "__main__":
    main()
