"""Compile the C28-updated manuscript with the pinned local Tectonic."""
import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


engine = ROOT / "research/external/tectonic/tectonic"
source = ROOT / "paper/main.tex"
metadata = json.loads((ROOT / "research/tectonic-acquisition.json").read_text())
if sha(engine) != metadata["binary_sha256"]:
    raise SystemExit("Pinned Tectonic binary hash mismatch")

out = ROOT / "paper/build-c28-v1"
out.mkdir()
(out / "main.tex").write_bytes(source.read_bytes())
cache = ROOT / "research/external/tectonic/cache"
cache.mkdir(exist_ok=True)
command = [
    str(engine), "--untrusted", "--only-cached", "--keep-logs",
    "--makefile-rules", str(out / "dependencies.mk"),
    "--outdir", str(out), str(out / "main.tex"),
]
environment = {
    "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
    "LANG": "fr_FR.UTF-8",
    "TECTONIC_CACHE_DIR": str(cache),
}
tex_hash_before = sha(source)
started = time.perf_counter()
error = None
exit_code = None
with (out / "stdout.txt").open("x") as stdout, (out / "stderr.txt").open("x") as stderr:
    try:
        exit_code = subprocess.run(
            command, cwd=ROOT, env=environment, stdout=stdout, stderr=stderr,
            timeout=480,
        ).returncode
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"

if exit_code == 0 and error is None:
    compiled_pdf = out / "main.pdf"
    if not compiled_pdf.is_file():
        error = "Tectonic exited successfully without producing main.pdf"
    else:
        shutil.copyfile(compiled_pdf, ROOT / "paper/main.pdf")

result = {
    "command": command,
    "binary_sha256": sha(engine),
    "tex_sha256_before": tex_hash_before,
    "tex_sha256_after": sha(source),
    "exit_code": exit_code,
    "error": error,
    "runtime_seconds": time.perf_counter() - started,
    "environment_scope": "PATH, LANG and local TECTONIC_CACHE_DIR only; no shell escape",
    "outputs": {
        str(path.relative_to(ROOT)): sha(path)
        for path in [*out.iterdir(), ROOT / "paper/main.pdf"]
        if path.is_file()
    },
    "scope": "Compilation checks syntax and layout, not scientific truth or submission readiness.",
}
(ROOT / "research/c28-pdf-build.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"exit_code": exit_code, "error": error, "runtime_seconds": result["runtime_seconds"]}))
raise SystemExit(0 if exit_code == 0 and error is None else 1)
