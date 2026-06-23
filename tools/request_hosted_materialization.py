from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codemani_review.hosted_client import DEFAULT_MATERIALIZER_URL, request_hosted_materialization


def main() -> int:
    parser = argparse.ArgumentParser(description="Request hosted CodeMani materialization for a .mani packet.")
    parser.add_argument("--api-url", default=DEFAULT_MATERIALIZER_URL)
    parser.add_argument("--mani", default=str(ROOT / "examples" / "synthetic_package_slice.mani"))
    parser.add_argument("--target", default="javascript.commonjs")
    parser.add_argument("--token-env", default="CODEMANI_API_TOKEN")
    parser.add_argument("--timeout-seconds", type=int, default=60)
    args = parser.parse_args()
    try:
        response = request_hosted_materialization(
            api_url=args.api_url,
            mani_path=args.mani,
            target=args.target,
            token_env=args.token_env,
            timeout_seconds=args.timeout_seconds,
        )
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(response, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
