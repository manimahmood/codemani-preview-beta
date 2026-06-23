from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from codemani_review.hosted_client import (
    RESPONSE_SCHEMA,
    normalize_materializer_url,
    read_api_token,
    request_hosted_materialization,
)
from codemani_review.packet_inspector import inspect_mani

ROOT = Path(__file__).resolve().parents[1]


class FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body
        self.headers = {"Content-Length": str(len(body))}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def read(self, _size: int = -1) -> bytes:
        return self._body


class PublicBoundaryTests(unittest.TestCase):
    def test_synthetic_packet_inspects(self) -> None:
        result = inspect_mani(ROOT / "examples" / "synthetic_package_slice.mani")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["kind"], "codemani.intent.v1")
        self.assertEqual(result["payload_count"], 1)

    def test_materialization_receipt_verifies(self) -> None:
        proc = subprocess.run(
            [sys.executable, "tools/verify_materialization_receipt.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["status"], "PASS")

    def test_inspect_packet_cli(self) -> None:
        proc = subprocess.run(
            [sys.executable, "tools/inspect_packet.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["kind"], "codemani.intent.v1")

    def test_hosted_url_defaults_to_sfiniti_api(self) -> None:
        self.assertEqual(
            normalize_materializer_url("https://api.sfiniti.ai/"),
            "https://api.sfiniti.ai/v1/materialize",
        )

    def test_hosted_url_rejects_unapproved_http_host(self) -> None:
        with self.assertRaises(ValueError):
            normalize_materializer_url("http://example.com/v1/materialize")

    def test_hosted_url_rejects_unapproved_https_host(self) -> None:
        with self.assertRaises(ValueError):
            normalize_materializer_url("https://example.com/v1/materialize")

    def test_token_env_must_be_scoped(self) -> None:
        with self.assertRaises(ValueError):
            read_api_token("AWS_SECRET_ACCESS_KEY")

    def test_token_env_reads_scoped_value(self) -> None:
        with mock.patch.dict(os.environ, {"CODEMANI_API_TOKEN": "token"}, clear=True):
            self.assertEqual(read_api_token("CODEMANI_API_TOKEN"), "token")

    def test_packet_rejects_unsafe_payload_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            import zipfile

            packet = Path(td) / "bad.mani"
            manifest = {
                "schema": "codemani.container.v1",
                "kind": "codemani.intent.v1",
                "payloads": [
                    {
                        "path": "../payload.json",
                        "bytes": 2,
                        "sha256": "0" * 64,
                        "content_type": "application/json",
                    }
                ],
            }
            with zipfile.ZipFile(packet, "w") as zf:
                zf.writestr("mani_manifest.json", json.dumps(manifest))
            with self.assertRaises(ValueError):
                inspect_mani(packet)

    def test_hosted_materialization_accepts_expected_schema(self) -> None:
        body = json.dumps({"schema": RESPONSE_SCHEMA, "status": "PASS", "artifacts": []}).encode("utf-8")
        with mock.patch("urllib.request.urlopen", return_value=FakeResponse(body)):
            result = request_hosted_materialization(
                api_url="https://api.sfiniti.ai/v1/materialize",
                mani_path=ROOT / "examples" / "synthetic_package_slice.mani",
                token_env="CODEMANI_API_TOKEN",
            )
        self.assertEqual(result["schema"], RESPONSE_SCHEMA)
        self.assertEqual(result["status"], "PASS")

    def test_hosted_materialization_rejects_bad_schema(self) -> None:
        body = json.dumps({"schema": "unexpected", "status": "PASS"}).encode("utf-8")
        with mock.patch("urllib.request.urlopen", return_value=FakeResponse(body)):
            with self.assertRaises(ValueError):
                request_hosted_materialization(
                    api_url="https://api.sfiniti.ai/v1/materialize",
                    mani_path=ROOT / "examples" / "synthetic_package_slice.mani",
                    token_env="CODEMANI_API_TOKEN",
                )

    def test_hosted_materialization_rejects_non_pass_status(self) -> None:
        body = json.dumps({"schema": RESPONSE_SCHEMA, "status": "FAIL"}).encode("utf-8")
        with mock.patch("urllib.request.urlopen", return_value=FakeResponse(body)):
            with self.assertRaises(ValueError):
                request_hosted_materialization(
                    api_url="https://api.sfiniti.ai/v1/materialize",
                    mani_path=ROOT / "examples" / "synthetic_package_slice.mani",
                    token_env="CODEMANI_API_TOKEN",
                )


if __name__ == "__main__":
    unittest.main()
