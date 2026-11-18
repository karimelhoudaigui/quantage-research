"""Bounded CLI runner. Importing it never launches Codex."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT))
from scripts.check import validate_completion


def invoke(cmd, prompt, log, timeout):
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT,
                               text=True, start_new_session=(os.name == "posix"))
    try:
        process.communicate(input=prompt, timeout=timeout)
    except (subprocess.TimeoutExpired, KeyboardInterrupt):
        if os.name == "posix":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:
            process.kill()
        process.communicate()
        raise
    if process.returncode:
        raise subprocess.CalledProcessError(process.returncode, cmd)


def main(argv=None, root=ROOT, executor=invoke):
    root = Path(root)
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycles", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    policy = json.loads((root/"config/policy.json").read_text())
    if not 1 <= args.cycles <= policy["max_cycles_per_launch"]:
        parser.error("Invalid cycle count")
    cmd = ["codex", "exec", "-C", str(root), "--sandbox", "workspace-write", "-"]
    if args.dry_run:
        print(cmd, args.cycles)
        return 0
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip():
        print("Review and commit changes first.", file=sys.stderr)
        return 1
    previous = sorted((root/"runs").glob("*/prompt.md"))
    if previous:
        try:
            prior = validate_completion(previous[-1].with_name("completion.json"))
            if prior["status"] == "blocked":
                raise ValueError("previous run is blocked")
        except (OSError, ValueError) as exc:
            print("Review previous run before resuming: %s" % exc, file=sys.stderr)
            return 1
    lock = root/".runner.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        print("Runner lock exists; inspect the running process before removing it.", file=sys.stderr)
        return 1
    os.close(fd)
    try:
        for _ in range(args.cycles):
            run = root/"runs"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            run.mkdir(parents=True)
            prompt = ((root/"prompts/cycle.md").read_text() +
                      "\nCycle directory: %s. Write summary.md and completion.json with status, question, next_action. Budget %s seconds."
                      % (run.relative_to(root), policy["seconds_per_cycle"]))
            (run/"prompt.md").write_text(prompt)
            try:
                with (run/"codex.log").open("w") as log:
                    executor(cmd, prompt, log, policy["seconds_per_cycle"])
                subprocess.run([sys.executable, str(root/"scripts/check.py")], cwd=root, check=True)
                result = validate_completion(run/"completion.json")
                if result["status"] == "blocked":
                    raise ValueError("cycle explicitly blocked: "+result["next_action"])
            except (Exception, KeyboardInterrupt) as exc:
                (run/"runner-error.txt").write_text(type(exc).__name__+": "+str(exc)+"\n")
                print("Stopped: inspect %s" % run, file=sys.stderr)
                return 1
            print("Completed", run.name)
    finally:
        lock.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
