from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codemani_review import inspect_mani


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a public-safe CodeMani .mani packet.")
    parser.add_argument(
        "packet",
        nargs="?",
        default=str(ROOT / "examples" / "synthetic_package_slice.mani"),
        help="Path to a .mani packet. Defaults to the synthetic example.",
    )
    try:
        result = inspect_mani(parser.parse_args().packet)
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
