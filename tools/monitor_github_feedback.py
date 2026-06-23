from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_REPO = "manimahmood/codemani-preview-beta"


def _run_gh_api(path: str, *, fields: dict[str, str] | None = None, timeout_seconds: int = 30) -> dict[str, Any]:
    cmd = ["gh", "api", path]
    for key, value in (fields or {}).items():
        cmd += ["-f", f"{key}={value}"]
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout_seconds)
    if proc.returncode != 0:
        return {
            "status": "UNAVAILABLE",
            "reason": (proc.stderr.strip() or proc.stdout.strip())[-600:],
            "returncode": proc.returncode,
        }
    try:
        return {"status": "PASS", "payload": json.loads(proc.stdout)}
    except json.JSONDecodeError as exc:
        return {"status": "UNAVAILABLE", "reason": f"GitHub CLI returned invalid JSON: {exc}", "returncode": proc.returncode}


def _http_get_json(url: str, *, timeout_seconds: int = 30) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "codemani-feedback-monitor"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return {"status": "PASS", "payload": json.loads(response.read().decode("utf-8"))}
    except urllib.error.HTTPError as exc:
        return {"status": "UNAVAILABLE", "reason": f"GitHub HTTP {exc.code}: {exc.reason}"}
    except urllib.error.URLError as exc:
        return {"status": "UNAVAILABLE", "reason": f"GitHub request failed: {exc.reason}"}
    except json.JSONDecodeError as exc:
        return {"status": "UNAVAILABLE", "reason": f"GitHub returned invalid JSON: {exc}"}


def _github_json(path: str, *, fields: dict[str, str] | None = None, timeout_seconds: int = 30) -> dict[str, Any]:
    gh_result = _run_gh_api(path, fields=fields, timeout_seconds=timeout_seconds)
    if gh_result.get("status") == "PASS":
        return gh_result
    if fields:
        query = urllib.parse.urlencode(fields)
        url = f"https://api.github.com/{path}?{query}"
    else:
        url = f"https://api.github.com/{path}"
    http_result = _http_get_json(url, timeout_seconds=timeout_seconds)
    if http_result.get("status") == "PASS":
        http_result["fallback_from_gh"] = True
        return http_result
    http_result["gh_reason"] = gh_result.get("reason", "")
    return http_result


def _search_count(repo: str, kind: str, state: str | None, *, timeout_seconds: int) -> dict[str, Any]:
    query = f"repo:{repo} type:{kind}"
    if state:
        query += f" state:{state}"
    result = _github_json("search/issues", fields={"q": query, "per_page": "1"}, timeout_seconds=timeout_seconds)
    payload = result.get("payload") if result.get("status") == "PASS" else {}
    return {
        "status": result.get("status"),
        "count": int(payload.get("total_count", 0)) if isinstance(payload, dict) else 0,
        "reason": result.get("reason", ""),
    }


def _traffic(repo: str, metric: str, *, timeout_seconds: int) -> dict[str, Any]:
    result = _run_gh_api(f"repos/{repo}/traffic/{metric}", timeout_seconds=timeout_seconds)
    payload = result.get("payload") if result.get("status") == "PASS" else {}
    if result.get("status") != "PASS" or not isinstance(payload, dict):
        return {"status": "UNAVAILABLE", "reason": result.get("reason", "traffic API unavailable")}
    return {
        "status": "PASS",
        "count": payload.get("count"),
        "uniques": payload.get("uniques"),
        "days": len(payload.get(metric, [])) if isinstance(payload.get(metric), list) else 0,
    }


def monitor(repo: str, *, include_traffic: bool, timeout_seconds: int) -> dict[str, Any]:
    repo_result = _github_json(f"repos/{repo}", timeout_seconds=timeout_seconds)
    repo_payload = repo_result.get("payload") if repo_result.get("status") == "PASS" else {}
    issue_counts = {
        "all": _search_count(repo, "issue", None, timeout_seconds=timeout_seconds),
        "open": _search_count(repo, "issue", "open", timeout_seconds=timeout_seconds),
        "closed": _search_count(repo, "issue", "closed", timeout_seconds=timeout_seconds),
    }
    pr_counts = {
        "all": _search_count(repo, "pr", None, timeout_seconds=timeout_seconds),
        "open": _search_count(repo, "pr", "open", timeout_seconds=timeout_seconds),
        "closed": _search_count(repo, "pr", "closed", timeout_seconds=timeout_seconds),
    }
    traffic = {
        "clones": _traffic(repo, "clones", timeout_seconds=timeout_seconds) if include_traffic else {"status": "SKIPPED"},
        "views": _traffic(repo, "views", timeout_seconds=timeout_seconds) if include_traffic else {"status": "SKIPPED"},
    }
    checks = {
        "repo_loaded": repo_result.get("status") == "PASS",
        "stars_loaded": isinstance(repo_payload, dict) and "stargazers_count" in repo_payload,
        "issue_counts_loaded": all(row["status"] == "PASS" for row in issue_counts.values()),
        "pr_counts_loaded": all(row["status"] == "PASS" for row in pr_counts.values()),
        "traffic_attempted": include_traffic,
        "clones_loaded": traffic["clones"].get("status") == "PASS" if include_traffic else False,
        "views_loaded": traffic["views"].get("status") == "PASS" if include_traffic else False,
    }
    return {
        "schema": "codemani.github_public_feedback_monitor.v1",
        "repo": repo,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "PASS" if checks["repo_loaded"] and checks["stars_loaded"] and checks["issue_counts_loaded"] and checks["pr_counts_loaded"] else "FAIL",
        "checks": checks,
        "metrics": {
            "stars": repo_payload.get("stargazers_count") if isinstance(repo_payload, dict) else None,
            "watchers": repo_payload.get("subscribers_count") if isinstance(repo_payload, dict) else None,
            "forks": repo_payload.get("forks_count") if isinstance(repo_payload, dict) else None,
            "open_issues_including_prs": repo_payload.get("open_issues_count") if isinstance(repo_payload, dict) else None,
            "issues": {key: value["count"] for key, value in issue_counts.items()},
            "pull_requests": {key: value["count"] for key, value in pr_counts.items()},
            "traffic": traffic,
        },
        "boundary": (
            "Public GitHub feedback monitor only. It records aggregate issue, pull request, "
            "star, clone, and view metrics and never emits credentials or raw reviewer content."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor public CodeMani GitHub feedback metrics.")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--include-traffic", action="store_true", help="Attempt GitHub traffic clones/views via gh auth.")
    parser.add_argument("--timeout-seconds", type=int, default=30)
    args = parser.parse_args()
    result = monitor(args.repo, include_traffic=args.include_traffic, timeout_seconds=args.timeout_seconds)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        return 1
    if args.include_traffic and not (result["checks"]["clones_loaded"] and result["checks"]["views_loaded"]):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
