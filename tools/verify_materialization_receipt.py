from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codemani_review import inspect_mani


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_normalized_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_intent(packet_path: Path) -> dict:
    with zipfile.ZipFile(packet_path, "r") as archive:
        return json.loads(archive.read("payload/intent.json").decode("utf-8"))


def verify(receipt_path: Path) -> dict:
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {
        "receipt_schema": receipt.get("schema") == "codemani.materialization_receipt.v1",
        "receipt_status": receipt.get("status") == "PASS",
    }
    packet_info = receipt.get("packet") if isinstance(receipt.get("packet"), dict) else {}
    packet_path = ROOT / str(packet_info.get("path", ""))
    packet = inspect_mani(packet_path)
    checks["packet_inspects"] = packet["status"] == "PASS"
    checks["packet_sha256"] = packet["container_sha256"] == packet_info.get("sha256")
    checks["packet_bytes"] = packet["container_bytes"] == packet_info.get("bytes")

    intent = load_intent(packet_path)
    intent_sources = {
        row.get("path"): row.get("sha256")
        for row in intent.get("sources", [])
        if isinstance(row, dict)
    }
    for idx, row in enumerate(receipt.get("sources", [])):
        path = ROOT / str(row.get("path", ""))
        expected = row.get("sha256_normalized")
        actual = sha256_normalized_text(path)
        checks[f"source_{idx}_hash"] = actual == expected
        checks[f"source_{idx}_intent_hash"] = intent_sources.get(row.get("path")) == expected

    for idx, row in enumerate(receipt.get("outputs", [])):
        path = ROOT / str(row.get("path", ""))
        expected = row.get("sha256_normalized")
        checks[f"output_{idx}_hash"] = sha256_normalized_text(path) == expected

    oracle = receipt.get("oracle") if isinstance(receipt.get("oracle"), dict) else {}
    command = oracle.get("command")
    if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
        checks["oracle_command_valid"] = False
        oracle_payload = {}
    else:
        proc = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
        checks["oracle_returncode"] = proc.returncode == oracle.get("returncode") == 0
        try:
            oracle_payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            oracle_payload = {}
        checks["oracle_stdout_json"] = oracle_payload == oracle.get("stdout_json")
        checks["oracle_status"] = oracle_payload.get("status") == "PASS"

    result = {
        "schema": "codemani.materialization_receipt_verification.v1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "receipt": str(receipt_path.relative_to(ROOT)),
        "boundary": (
            "Verifies public packet/source/output/oracle consistency. It does not "
            "expose or prove the private materializer implementation."
        ),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the public CodeMani materialization receipt.")
    parser.add_argument(
        "receipt",
        nargs="?",
        default=str(ROOT / "examples" / "materialization_receipt.json"),
    )
    result = verify(Path(parser.parse_args().receipt))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
