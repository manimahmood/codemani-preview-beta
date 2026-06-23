from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PLACEHOLDER_VALUES = {"", "_no response_", "none", "n/a", "not applicable"}


@dataclass(frozen=True)
class IssueFeedback:
    number: int
    url: str
    valid: bool
    reasons: tuple[str, ...]
    useful_packet: str
    preferred_delivery: str
    real_workflow: str
    next_useful_step: str


def _normalize_heading(text: str) -> str:
    return " ".join(text.lower().replace("?", "").split())


def parse_issue_form_body(body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if line.startswith("### "):
            current = _normalize_heading(line[4:])
            sections[current] = []
        elif current is not None:
            sections[current].append(line)

    parsed: dict[str, str] = {}
    for heading, lines in sections.items():
        value = "\n".join(lines).strip()
        # GitHub issue forms often include blank separator lines after headings.
        value = "\n".join(part for part in value.splitlines() if part.strip()).strip()
        parsed[heading] = value
    return parsed


def _field(parsed: dict[str, str], *headings: str) -> str:
    normalized = {_normalize_heading(heading) for heading in headings}
    for key, value in parsed.items():
        if key in normalized:
            return value.strip()
    return ""


def _is_empty_or_placeholder(value: str) -> bool:
    stripped = value.strip()
    if stripped.lower() in PLACEHOLDER_VALUES:
        return True
    return "[" in stripped and "]" in stripped


def classify_issue(issue: dict[str, Any]) -> IssueFeedback:
    parsed = parse_issue_form_body(str(issue.get("body", "")))
    useful = _field(parsed, "Could a code-intent packet help your workflow")
    preferred = _field(parsed, "Which delivery model would you prefer")
    workflow = _field(parsed, "What real workflow would you try this in")
    next_step = _field(parsed, "What one change would make you more likely to try it again")

    reasons: list[str] = []
    if _is_empty_or_placeholder(useful):
        reasons.append("missing_usefulness_answer")
    if _is_empty_or_placeholder(preferred):
        reasons.append("missing_delivery_preference")
    if len(workflow) < 20 or _is_empty_or_placeholder(workflow):
        reasons.append("missing_real_workflow")
    if len(next_step) < 20 or _is_empty_or_placeholder(next_step):
        reasons.append("missing_next_step")

    return IssueFeedback(
        number=int(issue.get("number", 0) or 0),
        url=str(issue.get("url", "")),
        valid=not reasons,
        reasons=tuple(reasons),
        useful_packet=useful,
        preferred_delivery=preferred,
        real_workflow=workflow,
        next_useful_step=next_step,
    )


def score_issues(issues: list[dict[str, Any]]) -> dict[str, Any]:
    feedback_rows = [classify_issue(issue) for issue in issues]
    valid_rows = [row for row in feedback_rows if row.valid]
    demand_rows = [
        row
        for row in valid_rows
        if row.useful_packet.lower().startswith("yes")
        and row.preferred_delivery.lower() not in {"none of these", "review packet only"}
    ]
    interest_rows = [
        row
        for row in valid_rows
        if row.useful_packet.lower().startswith(("yes", "maybe"))
    ]
    demand_status = "UNPROVEN"
    if len(valid_rows) >= 3 and len(demand_rows) >= 2:
        demand_status = "EARLY_POSITIVE_SIGNAL"
    elif valid_rows:
        demand_status = "RESPONSES_PRESENT_NO_DEMAND_PROMOTION"

    return {
        "schema": "codemani.github_feedback_intake.v1",
        "status": "PASS",
        "issue_count": len(issues),
        "valid_response_count": len(valid_rows),
        "template_or_invalid_count": len(feedback_rows) - len(valid_rows),
        "interest_signal_count": len(interest_rows),
        "demand_signal_count": len(demand_rows),
        "demand_status": demand_status,
        "responses": [
            {
                "number": row.number,
                "url": row.url,
                "valid": row.valid,
                "reasons": list(row.reasons),
                "useful_packet": row.useful_packet if row.valid else "",
                "preferred_delivery": row.preferred_delivery if row.valid else "",
            }
            for row in feedback_rows
        ],
        "boundary": (
            "This scorer summarizes GitHub feedback issues only. It does not "
            "promote empty, malformed, template-default, or low-commitment "
            "responses into market demand."
        ),
    }


def load_github_issues(repo: str) -> list[dict[str, Any]]:
    proc = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "all",
            "--label",
            "feedback",
            "--json",
            "number,title,body,labels,author,createdAt,url",
        ],
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "gh issue list failed")
    return json.loads(proc.stdout)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Score CodeMani GitHub issue feedback.")
    parser.add_argument("--repo", default="manimahmood/codemani-preview-beta")
    parser.add_argument("--issues-json", default="")
    args = parser.parse_args(argv)
    if args.issues_json:
        issues = json.loads(Path(args.issues_json).read_text(encoding="utf-8"))
    else:
        issues = load_github_issues(args.repo)
    print(json.dumps(score_issues(issues), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
