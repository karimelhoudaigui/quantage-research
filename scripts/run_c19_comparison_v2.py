"""Execute the frozen C19 comparison once, stopping at the first failed phase."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    freeze = json.loads(Path("runs/20261115-c19-instruct-repair/freeze-test-v2.json").read_text())
    for phase in ("initial", "feedback", "direct", "self", "guided", "score"):
        for name, expected in freeze["sha256"].items():
            if hashlib.sha256(Path(name).read_bytes()).hexdigest() != expected:
                raise SystemExit("frozen input changed: " + name)
        print("C19 phase " + phase, flush=True)
        subprocess.run([sys.executable, "scripts/run_c19_phase_v2.py", phase, "--split", "test"], check=True)


if __name__ == "__main__":
    main()
