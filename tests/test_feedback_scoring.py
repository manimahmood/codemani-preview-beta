from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codemani_review.feedback_scoring import score_review_notes


VALID_NOTE = """# CodeMani Beta Review - reviewer

## Core Question

- Answer: yes
- Why: I would use this to preserve code migration intent across review and replay steps.

## Local vs Hosted

- Preferred shape: both
- Why: local replay is useful for audit, hosted materialization is useful for teams.

## Most Valuable Part

- Choice: fail-closed unsupported profiles

Explain: The boundary makes it easier to trust that unsupported syntax will not be guessed.

## Confusing Or Missing

I need to see a hosted materializer response receipt before trusting the API path.

## One Change That Would Make Me Try Again

Ship a larger synthetic migration sample with a signed receipt and a replayable oracle.

## Would I Use This Again?

- Answer: yes
- What would need to be true: More examples and a hosted demo would be enough for another pass.
"""


class FeedbackScoringTests(unittest.TestCase):
    def test_empty_feedback_is_unproven(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            review_dir = Path(td) / "review_notes"
            review_dir.mkdir()
            (review_dir / "TEMPLATE.md").write_text("template", encoding="utf-8")
            result = score_review_notes(review_dir)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["valid_response_count"], 0)
        self.assertEqual(result["demand_status"], "UNPROVEN")

    def test_placeholder_note_is_not_valid_demand(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            review_dir = Path(td) / "review_notes"
            review_dir.mkdir()
            (review_dir / "alice.md").write_text("- Answer: [yes/maybe/no]\n", encoding="utf-8")
            result = score_review_notes(review_dir)
        self.assertEqual(result["review_file_count"], 1)
        self.assertEqual(result["valid_response_count"], 0)
        self.assertEqual(result["template_or_invalid_count"], 1)

    def test_three_valid_two_yes_promotes_only_early_signal(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            review_dir = Path(td) / "review_notes"
            review_dir.mkdir()
            for idx in range(3):
                text = VALID_NOTE
                if idx == 2:
                    text = text.replace("- Answer: yes", "- Answer: maybe", 1)
                (review_dir / f"reviewer_{idx}.md").write_text(text, encoding="utf-8")
            result = score_review_notes(review_dir)
        self.assertEqual(result["valid_response_count"], 3)
        self.assertEqual(result["demand_signal_count"], 2)
        self.assertEqual(result["demand_status"], "EARLY_POSITIVE_SIGNAL")


if __name__ == "__main__":
    unittest.main()
