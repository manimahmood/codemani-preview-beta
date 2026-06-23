from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANNOUNCEMENT = ROOT / "docs" / "public_beta_announcement.md"

REQUIRED_PHRASES = [
    "compact code-intent packet workflow",
    "python tools/run_review.py",
    "It does not include the private materializer",
    "Please do not paste private prompts",
    "does not claim arbitrary Python translation",
    "does not claim",
    "market demand",
]

FORBIDDEN_PARTS = [
    ("private", "_repos"),
    ("ssh", "://"),
    ("192", ".168."),
    ("C:\\Users\\", "manim"),
    ("/home/", "lmahmood"),
    ("PRIVATE", "_WORKTREE"),
    ("PRIVATE", "_REMOTE"),
    ("PRIVATE", "_ENDPOINT"),
    ("LOCAL", "_MODEL", "_CACHE"),
]


def main() -> int:
    text = ANNOUNCEMENT.read_text(encoding="utf-8") if ANNOUNCEMENT.exists() else ""
    missing = [phrase for phrase in REQUIRED_PHRASES if phrase not in text]
    forbidden_phrases = ["".join(parts) for parts in FORBIDDEN_PARTS]
    forbidden = [phrase for phrase in forbidden_phrases if phrase in text]
    checks = {
        "announcement_exists": ANNOUNCEMENT.exists(),
        "required_phrases_present": not missing,
        "forbidden_phrases_absent": not forbidden,
        "mentions_review_command": "python tools/run_review.py" in text,
        "mentions_private_materializer_excluded": "private materializer" in text,
        "keeps_market_demand_unclaimed": "market demand" in text,
    }
    result = {
        "schema": "codemani.public_launch_audit.v1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "missing_required_phrases": missing,
        "forbidden_phrase_hits": forbidden,
        "boundary": "Announcement audit only; does not publish the repo or prove demand.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
