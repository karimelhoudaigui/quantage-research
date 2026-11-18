"""Process one recorded proposal locally; no generation or credential access."""
import argparse
import json
from pathlib import Path
from .agent_pipeline import process_proposal
from .evaluation import load_json


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--request',type=Path,required=True)
    parser.add_argument('--proposal',type=Path,required=True)
    parser.add_argument('--schema-only',action='store_true')
    args=parser.parse_args()
    try:
        result=process_proposal(load_json(args.request),load_json(args.proposal),numerical=not args.schema_only)
    except (OSError,TypeError,ValueError) as exc:
        result={'status':'abstain','stage':'input_file','reason':str(exc)}
    print(json.dumps(result,indent=2,allow_nan=False))
    return 0 if result['status']=='accepted' else 2


if __name__=='__main__':raise SystemExit(main())
