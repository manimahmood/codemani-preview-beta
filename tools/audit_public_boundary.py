from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PARTS = [
    ("C:\\Users\\", "manim"),
    ("/home/", "lmahmood"),
    ("192", ".168."),
    ("private", "_repos"),
    ("ssh", "://"),
    ("PRIVATE", "_WORKTREE"),
    ("PRIVATE", "_REMOTE"),
    ("PRIVATE", "_ENDPOINT"),
    ("LOCAL", "_MODEL", "_CACHE"),
    ("BEGIN", " PRIVATE"),
    ("PRIVATE", " KEY"),
]

FORBIDDEN_FILENAME_PARTS = [
    ("local", "_llm_", "proposer", ".py"),
    ("proposer", ".py"),
    ("js", "_materializer", ".py"),
    ("repair", ".py"),
    ("source", "_edit", ".py"),
    ("repo", "_capsule", ".py"),
    ("build", "_receipt", ".sig", ".json"),
    ("trusted", "_release", "_keys", ".json"),
    ("private", "_operator", "_packet", ".zip"),
]


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False, timeout=60)


def scan_text() -> list[str]:
    hits: list[str] = []
    forbidden = ["".join(parts) for parts in FORBIDDEN_PARTS]
    forbidden_filenames = ["".join(parts) for parts in FORBIDDEN_FILENAME_PARTS]
    for path in sorted(ROOT.rglob("*")):
        if ".git" in path.parts or not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if any(name in rel for name in forbidden_filenames):
            hits.append(f"{rel}::forbidden_filename")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for token in forbidden:
            if token in text:
                hits.append(f"{rel}::{token}")
    return hits


def main() -> int:
    review = run([sys.executable, "tools/run_review.py"])
    compile_proc = run(
        [
            sys.executable,
            "-m",
            "py_compile",
            "codemani_review/packet_inspector.py",
            "codemani_review/hosted_client.py",
            "codemani_review/feedback_scoring.py",
            "codemani_review/issue_feedback_scoring.py",
            "tools/run_review.py",
            "tools/inspect_packet.py",
            "tools/request_hosted_materialization.py",
            "tools/score_feedback.py",
            "tools/score_github_feedback.py",
            "tools/verify_materialization_receipt.py",
            "tools/audit_public_launch_packet.py",
        ]
    )
    hits = scan_text()
    checks = {
        "review_replay_passed": review.returncode == 0,
        "python_compile_passed": compile_proc.returncode == 0,
        "private_marker_scan_clean": not hits,
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "private_marker_hits": hits,
        "boundary": "Public beta repo audit: replay, compile, and private-marker scan only.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
