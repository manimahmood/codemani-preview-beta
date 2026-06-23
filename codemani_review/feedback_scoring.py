from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PLACEHOLDER_FRAGMENTS = (
    "<your handle>",
    "[yes/no]",
    "[yes/maybe/no]",
    "[your answer]",
    "[what specific workflow",
    "[security, reproducibility",
    "[intent packet]",
    "[local materializer / hosted private materializer / both / review packet only]",
    "[hosted demo, more examples",
)


@dataclass(frozen=True)
class ReviewNote:
    path: str
    valid: bool
    reasons: tuple[str, ...]
    core_answer: str
    would_use_answer: str
    preferred_shape: str
    most_valuable_part: str


def _line_value(text: str, prefix: str, *, occurrence: int = 0) -> str:
    values: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith(prefix.lower()):
            values.append(stripped[len(prefix) :].strip())
    return values[occurrence] if occurrence < len(values) else ""


def _section_body(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        return ""
    rest = text[start + len(marker) :]
    next_heading = rest.find("\n## ")
    return rest if next_heading < 0 else rest[:next_heading]


def _is_placeholder(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return True
    lowered = stripped.lower()
    return any(fragment.lower() in lowered for fragment in PLACEHOLDER_FRAGMENTS)


def parse_review_note(path: Path, *, root: Path) -> ReviewNote:
    text = path.read_text(encoding="utf-8", errors="ignore")
    core = _section_body(text, "Core Question")
    would_use = _section_body(text, "Would I Use This Again?")
    most_valuable = _section_body(text, "Most Valuable Part")
    change = _section_body(text, "One Change That Would Make Me Try Again")

    core_answer = _line_value(core, "- Answer:")
    would_use_answer = _line_value(would_use, "- Answer:")
    preferred_shape = _line_value(text, "- Preferred shape:")
    most_valuable_part = _line_value(most_valuable, "- Choice:")
    if not most_valuable_part:
        # Backward-compatible with the first template version.
        for line in most_valuable.splitlines():
            stripped = line.strip()
            if stripped.startswith("- [") and stripped.endswith("]"):
                most_valuable_part = stripped[3:-1]
                break

    reasons: list[str] = []
    if _is_placeholder(core_answer):
        reasons.append("missing_core_answer")
    if _is_placeholder(would_use_answer):
        reasons.append("missing_would_use_answer")
    if _is_placeholder(preferred_shape):
        reasons.append("missing_preferred_shape")
    if _is_placeholder(most_valuable_part):
        reasons.append("missing_most_valuable_part")
    if len(change.strip()) < 30 or _is_placeholder(change.strip()):
        reasons.append("missing_specific_next_step")
    if any(fragment.lower() in text.lower() for fragment in PLACEHOLDER_FRAGMENTS):
        reasons.append("template_placeholder_present")

    return ReviewNote(
        path=path.relative_to(root).as_posix(),
        valid=not reasons,
        reasons=tuple(reasons),
        core_answer=core_answer,
        would_use_answer=would_use_answer,
        preferred_shape=preferred_shape,
        most_valuable_part=most_valuable_part,
    )


def score_review_notes(review_dir: Path) -> dict[str, Any]:
    root = review_dir.parent
    files = sorted(path for path in review_dir.glob("*.md") if path.name.lower() != "template.md")
    notes = [parse_review_note(path, root=root) for path in files]
    valid_notes = [note for note in notes if note.valid]
    demand_notes = [
        note
        for note in valid_notes
        if note.core_answer.lower().startswith("yes") and note.would_use_answer.lower().startswith("yes")
    ]
    interest_notes = [
        note
        for note in valid_notes
        if note.core_answer.lower().startswith(("yes", "maybe"))
        or note.would_use_answer.lower().startswith(("yes", "maybe"))
    ]
    demand_status = "UNPROVEN"
    if len(valid_notes) >= 3 and len(demand_notes) >= 2:
        demand_status = "EARLY_POSITIVE_SIGNAL"
    elif valid_notes:
        demand_status = "RESPONSES_PRESENT_NO_DEMAND_PROMOTION"

    return {
        "schema": "codemani.feedback_intake.v1",
        "status": "PASS",
        "review_file_count": len(files),
        "valid_response_count": len(valid_notes),
        "template_or_invalid_count": len(notes) - len(valid_notes),
        "interest_signal_count": len(interest_notes),
        "demand_signal_count": len(demand_notes),
        "demand_status": demand_status,
        "responses": [
            {
                "path": note.path,
                "valid": note.valid,
                "reasons": list(note.reasons),
                "core_answer": note.core_answer if note.valid else "",
                "would_use_answer": note.would_use_answer if note.valid else "",
                "preferred_shape": note.preferred_shape if note.valid else "",
                "most_valuable_part": note.most_valuable_part if note.valid else "",
            }
            for note in notes
        ],
        "boundary": (
            "This scorer summarizes public review-note files only. It does not "
            "prove market demand from empty, template-default, duplicate, or "
            "unqualified responses."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Score CodeMani beta review notes without promoting weak demand.")
    parser.add_argument("--review-dir", default=str(Path(__file__).resolve().parents[1] / "review_notes"))
    args = parser.parse_args(argv)
    result = score_review_notes(Path(args.review_dir))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
