from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codemani_review import inspect_mani


def sha256_normalized_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    mani = ROOT / "examples" / "synthetic_package_slice.mani"
    source_files = {
        "motion_math.py": "1a1e274d5491c9ce3765ff45ebe2b656bcbbd4689461ec183e7b2cf88f11084f",
        "scoring.py": "133fcc24b7b1099fa8bc453d78b4a3f310d1481dd7ecfd167388e5a6f151c300",
    }
    generated = ROOT / "examples" / "materialized" / "scoring.js"
    oracle = ROOT / "examples" / "materialized" / "oracle.js"

    packet = inspect_mani(mani)
    source_checks = {
        name: sha256_normalized_text(ROOT / "examples" / "source" / name) == expected
        for name, expected in source_files.items()
    }
    node = subprocess.run(
        ["node", str(oracle)],
        cwd=ROOT / "examples" / "materialized",
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    node_status = json.loads(node.stdout.strip()).get("status") if node.stdout.strip() else "NO_OUTPUT"
    checks = {
        "packet_inspected": packet["status"] == "PASS",
        "source_hashes_match": all(source_checks.values()),
        "precomputed_js_present": generated.exists(),
        "node_oracle_passed": node.returncode == 0 and node_status == "PASS",
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "packet": {
            "kind": packet["kind"],
            "payload_count": packet["payload_count"],
            "container_bytes": packet["container_bytes"],
            "container_sha256": packet["container_sha256"],
        },
        "boundary": "Public review replay only; no private materializer is included or invoked.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
