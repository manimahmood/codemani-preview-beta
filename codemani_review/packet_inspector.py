from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

MAX_CONTAINER_BYTES = 2_000_000
MAX_MANIFEST_BYTES = 20_000
MAX_PAYLOAD_BYTES = 200_000
MAX_PAYLOADS = 8
MAX_ZIP_RATIO = 200.0


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_member(name: str) -> bool:
    path = Path(name)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in name


def inspect_mani(path: str | Path) -> dict[str, Any]:
    mani_path = Path(path)
    if not mani_path.exists():
        raise ValueError("missing .mani file")
    if mani_path.stat().st_size > MAX_CONTAINER_BYTES:
        raise ValueError("container too large")

    with zipfile.ZipFile(mani_path) as zf:
        members = zf.infolist()
        if not members:
            raise ValueError("empty container")
        for info in members:
            if not _safe_member(info.filename):
                raise ValueError("unsafe member path")
            if info.file_size > MAX_PAYLOAD_BYTES and info.filename != "mani_manifest.json":
                raise ValueError("payload too large")
            if info.compress_size > 0 and info.file_size / info.compress_size > MAX_ZIP_RATIO:
                raise ValueError("zip compression ratio too high")

        manifest_info = zf.getinfo("mani_manifest.json")
        if manifest_info.file_size > MAX_MANIFEST_BYTES:
            raise ValueError("manifest too large")
        manifest = json.loads(zf.read("mani_manifest.json").decode("utf-8"))
        if manifest.get("schema") != "codemani.container.v1":
            raise ValueError("unsupported container schema")
        payloads = manifest.get("payloads")
        if not isinstance(payloads, list) or not payloads:
            raise ValueError("missing payloads")
        if len(payloads) > MAX_PAYLOADS:
            raise ValueError("too many payloads")

        payload_summaries = []
        for row in payloads:
            payload_path = row.get("path")
            if not isinstance(payload_path, str) or not _safe_member(payload_path):
                raise ValueError("unsafe payload path")
            data = zf.read(payload_path)
            if len(data) != row.get("bytes"):
                raise ValueError("payload byte count mismatch")
            digest = hashlib.sha256(data).hexdigest()
            if digest != row.get("sha256"):
                raise ValueError("payload digest mismatch")
            payload_summaries.append(
                {
                    "path": payload_path,
                    "bytes": len(data),
                    "sha256": digest,
                    "content_type": row.get("content_type"),
                }
            )

    return {
        "status": "PASS",
        "kind": manifest.get("kind"),
        "payload_count": len(payload_summaries),
        "payloads": payload_summaries,
        "container_bytes": mani_path.stat().st_size,
        "container_sha256": sha256_file(mani_path),
    }
