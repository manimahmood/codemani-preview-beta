from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

MAX_MANI_BYTES = 2_000_000
MAX_RESPONSE_BYTES = 16_000_000
DEFAULT_MATERIALIZER_URL = "https://api.sfiniti.ai/v1/materialize"
DEFAULT_ALLOWED_API_HOSTS = ("api.sfiniti.ai", "localhost", "127.0.0.1", "::1")
TOKEN_ENVS = ("CODEMANI_API_TOKEN", "SFINITI_API_TOKEN")
REQUEST_SCHEMA = "codemani.materializer.request.v1"
RESPONSE_SCHEMA = "codemani.materializer.response.v1"


def normalize_materializer_url(api_url: str) -> str:
    url = api_url.strip()
    if not url:
        raise ValueError("api_url is required for hosted CodeMani materialization")
    if url.endswith("/"):
        url += "v1/materialize"
    elif url.endswith("/codemani-materializer"):
        url += "/v1/materialize"
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"https", "http"} or not parsed.hostname:
        raise ValueError("api_url must be an absolute HTTP(S) materializer URL")
    if parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("hosted materializer API must use HTTPS unless it is localhost")
    allowed = set(DEFAULT_ALLOWED_API_HOSTS)
    extra_hosts = os.environ.get("CODEMANI_ALLOWED_API_HOSTS", "")
    allowed.update(host.strip().lower() for host in extra_hosts.split(",") if host.strip())
    if parsed.hostname.lower() not in allowed:
        raise ValueError(
            f"api_url host {parsed.hostname!r} is not allowed; set CODEMANI_ALLOWED_API_HOSTS to opt in"
        )
    return url


def read_api_token(token_env: str = "") -> str:
    requested = token_env.strip()
    if requested and not (requested.startswith("CODEMANI_") or requested.startswith("SFINITI_")):
        raise ValueError("token_env must name a CODEMANI_* or SFINITI_* environment variable")
    env_names = (requested,) if requested else TOKEN_ENVS
    for env_name in env_names:
        token = os.environ.get(env_name, "").strip()
        if token:
            return token
    return ""


def read_hosted_json_response(response) -> dict[str, Any]:
    length_text = response.headers.get("Content-Length")
    if length_text:
        try:
            content_length = int(length_text)
        except ValueError as exc:
            raise ValueError("hosted materializer response has invalid Content-Length") from exc
        if content_length > MAX_RESPONSE_BYTES:
            raise ValueError("hosted materializer response exceeds safety budget")
    data = response.read(MAX_RESPONSE_BYTES + 1)
    if len(data) > MAX_RESPONSE_BYTES:
        raise ValueError("hosted materializer response exceeds safety budget")
    return json.loads(data.decode("utf-8"))


def request_hosted_materialization(
    *,
    api_url: str,
    mani_path: str | Path,
    target: str = "javascript.commonjs",
    token_env: str = "CODEMANI_API_TOKEN",
    timeout_seconds: int = 60,
) -> dict[str, Any]:
    path = Path(mani_path)
    if not path.exists():
        raise ValueError("missing .mani file")
    if path.stat().st_size > MAX_MANI_BYTES:
        raise ValueError(f".mani file exceeds {MAX_MANI_BYTES} byte safety budget")
    body = json.dumps(
        {
            "schema": REQUEST_SCHEMA,
            "target": target,
            "mani_b64": base64.b64encode(path.read_bytes()).decode("ascii"),
        },
        separators=(",", ":"),
    ).encode("utf-8")
    headers = {"Content-Type": "application/json", "Content-Length": str(len(body))}
    token = read_api_token(token_env)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        normalize_materializer_url(api_url),
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=max(1, int(timeout_seconds))) as response:
            payload = read_hosted_json_response(response)
    except urllib.error.HTTPError as exc:
        try:
            error_payload = json.loads(exc.read().decode("utf-8"))
            reason = error_payload.get("reason", exc.reason)
        except Exception:
            reason = exc.reason
        raise ValueError(f"hosted materializer HTTP {exc.code}: {reason}") from exc
    except urllib.error.URLError as exc:
        raise ValueError(f"hosted materializer request failed: {exc.reason}") from exc
    if payload.get("schema") != RESPONSE_SCHEMA:
        raise ValueError("hosted materializer returned unexpected schema")
    if payload.get("status") != "PASS":
        raise ValueError(f"hosted materializer returned non-PASS status: {payload.get('status')}")
    return payload
