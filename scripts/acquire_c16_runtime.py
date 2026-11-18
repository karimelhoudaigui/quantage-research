"""Acquire pinned public C16 assets; never install or execute downloaded code.

Run explicitly from the repository:
    python3 scripts/acquire_c16_runtime.py --output research/external/c16-public

Only public HTTPS endpoints are used, without authentication, cookies, proxy
environment configuration, Hub login, or secret-file reads. HF metadata pins
the repository commit and checks its LFS identity before streaming the GGUF.
Every archive member is validated before manual extraction. Internal file links
are materialized as ordinary copies; no symlink, hardlink, device, owner,
extended attribute or archive-specified permission is installed. Failures keep
their partial artifacts and failed manifest, without retries or execution.
"""

import argparse
import contextlib
import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import signal
import sys
import tarfile
import time
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_TAG = "b12359"
RUNTIME_COMMIT = "b1b770d90d94cad9e9ea5b993bdbc383a522fb28"
RUNTIME_URL = "https://github.com/ggml-org/llama.cpp/releases/download/b12359/llama-b12359-bin-macos-arm64.tar.gz"
RUNTIME_SHA256 = "82b00abc740160e1b9980e6cc79c117345fa34af058c80e6c0a69aa8ddccde75"
MODEL_REPO = "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
MODEL_FILE = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
MODEL_SHA256 = "6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e"
MAX_ARCHIVE_BYTES = 64 * 1024**2
MAX_EXTRACTED_BYTES = 512 * 1024**2
MAX_MODEL_BYTES = 1500 * 1024**2
MAX_METADATA_BYTES = 4 * 1024**2
MAX_MEMBERS = 5000
CHUNK = 1024**2


def _check_url(url):
    parsed = urllib.parse.urlsplit(url)
    host = (parsed.hostname or "").lower()
    trusted = (host in ("github.com", "huggingface.co")
               or host.endswith(".githubusercontent.com")
               or host.endswith(".huggingface.co") or host.endswith(".hf.co"))
    if (parsed.scheme != "https" or not trusted or parsed.username is not None
            or parsed.password is not None or parsed.port not in (None, 443)):
        raise ValueError("public HTTPS redirect left the allowed asset hosts")
    return url


class PublicRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, newurl):
        _check_url(newurl)
        return super().redirect_request(request, response, code, message, headers, newurl)


def _opener():
    # Explicitly disable environment proxies. No authentication/cookie handler.
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), PublicRedirects())


def _request(opener, url):
    _check_url(url)
    request = urllib.request.Request(url, headers={
        "User-Agent": "QuantAge-C16-public-acquisition/1",
        "Accept-Encoding": "identity",
    })
    return opener.open(request, timeout=30)


def _public_json(opener, url):
    with _request(opener, url) as response:
        payload = response.read(MAX_METADATA_BYTES + 1)
    if len(payload) > MAX_METADATA_BYTES:
        raise ValueError("oversized public metadata response")
    return json.loads(payload)


def pin_model(opener):
    api = "https://huggingface.co/api/models/" + MODEL_REPO + "/revision/main?blobs=true"
    metadata = _public_json(opener, api)
    commit = metadata.get("sha")
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise ValueError("HF metadata did not provide a pinned commit")
    files = [row for row in metadata.get("siblings", []) if row.get("rfilename") == MODEL_FILE]
    if len(files) != 1 or not isinstance(files[0].get("lfs"), dict):
        raise ValueError("public model does not expose one matching LFS file")
    lfs = files[0]["lfs"]
    digest = lfs.get("sha256") or lfs.get("oid")
    if isinstance(digest, str):
        digest = digest.removeprefix("sha256:")
    size = lfs.get("size")
    if digest != MODEL_SHA256:
        raise ValueError("public model LFS SHA differs from the reviewed SHA")
    if type(size) is not int or not 0 < size <= MAX_MODEL_BYTES:
        raise ValueError("public model size is missing or exceeds the acquisition cap")
    return {
        "repo": MODEL_REPO, "commit": commit, "file": MODEL_FILE,
        "sha256_expected": MODEL_SHA256, "size_expected": size, "metadata_url": api,
        "url": "https://huggingface.co/" + MODEL_REPO + "/resolve/" + commit + "/" + MODEL_FILE,
    }


def download(opener, url, destination, digest_expected, maximum, records, size_expected=None):
    record = {"destination": str(destination), "source_url": url,
              "sha256_expected": digest_expected, "bytes": 0, "status": "running"}
    records.append(record)
    partial = destination.with_name(destination.name + ".part")
    digest = hashlib.sha256()
    try:
        with _request(opener, url) as response, partial.open("xb") as handle:
            while True:
                chunk = response.read(CHUNK)
                if not chunk:
                    break
                record["bytes"] += len(chunk)
                if record["bytes"] > maximum or (size_expected is not None and record["bytes"] > size_expected):
                    raise ValueError("download exceeds its declared size cap")
                digest.update(chunk)
                handle.write(chunk)
        record["sha256_observed"] = digest.hexdigest()
        if digest.hexdigest() != digest_expected or (size_expected is not None and record["bytes"] != size_expected):
            raise ValueError("downloaded bytes fail the size/hash check")
        if destination.exists():
            raise ValueError("refuse to replace an acquired artifact")
        partial.rename(destination)
        record["status"] = "completed"
    except BaseException:
        record["status"] = "failed"
        record["sha256_partial"] = digest.hexdigest()
        raise
    return record


def _archive_path(name, base=(), allow_parent=False):
    if not isinstance(name, str) or not name or len(name) > 4096 or "\\" in name or "\x00" in name:
        raise ValueError("invalid archive path")
    path = PurePosixPath(name)
    if path.is_absolute():
        raise ValueError("absolute archive path")
    parts = list(base)
    for part in path.parts:
        if part in ("", "."):
            continue
        if part == "..":
            if not allow_parent or not parts:
                raise ValueError("archive path escapes extraction root")
            parts.pop()
        else:
            parts.append(part)
    return PurePosixPath(*parts)


def safe_extract(archive, destination):
    """Validate all members, then write only new regular files under destination."""
    if destination.exists():
        raise ValueError("extraction destination must be new")
    with tarfile.open(archive, "r:gz") as source:
        members = {}
        for member in source:
            path = _archive_path(member.name)
            if str(path) == "." and member.isdir():
                continue
            if str(path) == "." or path in members:
                raise ValueError("duplicate or empty normalized archive path")
            if not (member.isfile() or member.isdir() or member.issym() or member.islnk()):
                raise ValueError("non-file archive member refused")
            if not 0 <= member.size <= MAX_EXTRACTED_BYTES:
                raise ValueError("invalid archive member size")
            members[path] = member
            if len(members) > MAX_MEMBERS:
                raise ValueError("too many archive members")
        for path in members:
            for parent in path.parents:
                if parent in members and not members[parent].isdir():
                    raise ValueError("archive file/link used as a parent directory")

        def resolve_file(path, trail=()):
            if path in trail or len(trail) >= 64 or path not in members:
                raise ValueError("broken or cyclic archive link")
            member = members[path]
            if member.isfile():
                return path
            if member.issym() or member.islnk():
                base = path.parent.parts if member.issym() else ()
                target = _archive_path(member.linkname, base=base, allow_parent=True)
                return resolve_file(target, trail + (path,))
            raise ValueError("archive link must resolve to a regular file")

        payloads = {path: resolve_file(path) for path, member in members.items() if not member.isdir()}
        expanded = sum(members[target].size for target in payloads.values())
        if expanded > MAX_EXTRACTED_BYTES:
            raise ValueError("expanded archive including materialized links exceeds cap")
        destination.mkdir()
        written = []
        for path, member in members.items():
            if member.isdir():
                (destination / path).mkdir(parents=True, exist_ok=True)
        for path, target in payloads.items():
            output = destination / path
            output.parent.mkdir(parents=True, exist_ok=True)
            target_member = members[target]
            digest = hashlib.sha256()
            count = 0
            stream = source.extractfile(target_member)
            if stream is None:
                raise ValueError("archive regular payload is missing")
            with stream, output.open("xb") as handle:
                while True:
                    chunk = stream.read(CHUNK)
                    if not chunk:
                        break
                    count += len(chunk)
                    if count > target_member.size:
                        raise ValueError("archive payload exceeds member size")
                    digest.update(chunk)
                    handle.write(chunk)
            if count != target_member.size:
                raise ValueError("archive payload is truncated")
            mode = 0o755 if target_member.mode & 0o111 else 0o644
            output.chmod(mode)
            written.append({"path": str(path), "bytes": count, "sha256": digest.hexdigest(),
                            "mode": oct(mode), "link_materialized": path != target})
        return {"files": written, "expanded_bytes": expanded,
                "link_policy": "internal regular-file targets copied; no links created"}


@contextlib.contextmanager
def acquisition_deadline(seconds):
    def timeout_handler(_signum, _frame):
        raise TimeoutError("bounded public acquisition exceeded its deadline")
    previous = signal.signal(signal.SIGALRM, timeout_handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "research/external/c16-public")
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args(argv)
    if not 1 <= args.timeout <= 1800:
        parser.error("timeout must be between 1 and 1800 seconds")
    destination = args.output.resolve()
    if ROOT not in destination.parents or destination.exists() or not destination.parent.is_dir():
        parser.error("output must be a new directory inside the repository, with an existing parent")
    destination.mkdir()
    started = time.monotonic()
    manifest = {"status": "running", "python": platform.python_version(), "machine": platform.machine(),
                "macOS": platform.mac_ver()[0], "runtime_tag": RUNTIME_TAG, "runtime_commit": RUNTIME_COMMIT,
                "downloads": [], "external_purchase_eur": 0, "model_execution": False,
                "authentication": "none; public endpoints only", "timeout_seconds": args.timeout,
                "started_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        with acquisition_deadline(args.timeout):
            if platform.system() != "Darwin" or platform.machine() != "arm64":
                raise ValueError("this pinned runtime targets macOS arm64 only")
            opener = _opener()
            model = pin_model(opener)
            manifest["model"] = model
            required = model["size_expected"] + MAX_ARCHIVE_BYTES + MAX_EXTRACTED_BYTES + 1024**3
            free = shutil.disk_usage(destination).free
            manifest["disk_preflight"] = {"free_bytes": free, "required_bytes": required}
            if free < required:
                raise ValueError("insufficient free disk for the bounded acquisition and reserve")
            downloads = destination / "downloads"
            downloads.mkdir()
            archive = downloads / "llama-b12359-bin-macos-arm64.tar.gz"
            download(opener, RUNTIME_URL, archive, RUNTIME_SHA256, MAX_ARCHIVE_BYTES, manifest["downloads"])
            manifest["runtime_extraction"] = safe_extract(archive, destination / "runtime")
            models = destination / "models"
            models.mkdir()
            download(opener, model["url"], models / MODEL_FILE, MODEL_SHA256,
                     MAX_MODEL_BYTES, manifest["downloads"], size_expected=model["size_expected"])
            (destination / "LOCAL_ONLY.txt").write_text(
                "Public acquisition only: no runtime/model was executed or installed.\n"
                "Use the pinned local model path; do not use runtime auto-download flags.\n"
                "Future inference must be offline, bounded, and independently recorded.\n")
            manifest["status"] = "completed"
    except BaseException as exc:
        manifest["status"] = "failed"
        manifest["error"] = type(exc).__name__ + ": " + str(exc)
        raise
    finally:
        manifest["elapsed_seconds"] = time.monotonic() - started
        (destination / "acquisition.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": manifest["status"], "output": str(destination),
                      "model_commit": manifest["model"]["commit"], "model_execution": False}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
