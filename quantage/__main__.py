"""Usage: python3 -m quantage request.json (or stdin)."""
import json
import sys
from pathlib import Path
from .core import pipeline

if __name__ == "__main__":
    content = Path(sys.argv[1]).read_text() if len(sys.argv) == 2 else sys.stdin.read()
    try:
        result = pipeline(json.loads(content))
    except (ValueError, TypeError) as exc:
        result = {"status": "abstain", "reason": "invalid JSON: "+str(exc)}
    print(json.dumps(result, indent=2, allow_nan=False))
    sys.exit(0 if result["status"] == "solved" else 2)
