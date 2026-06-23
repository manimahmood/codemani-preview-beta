from __future__ import annotations

import unittest

from codemani_review.issue_feedback_scoring import parse_issue_form_body, score_issues


ISSUE_BODY = """### Which best describes you?

I build developer tools

### How far did you get?

Ran the review script successfully

### Could a code-intent packet help your workflow?

Yes, clearly

### What real workflow would you try this in?

I would try this for migration review where we need an auditable intent packet.

### Which delivery model would you prefer?

Hosted private materializer

### What was confusing or missing?

I wanted a larger example and a server receipt.

### What one change would make you more likely to try it again?

Show a hosted materializer receipt against a larger multi-module synthetic package.
"""


class IssueFeedbackScoringTests(unittest.TestCase):
    def test_parse_issue_form_body(self) -> None:
        parsed = parse_issue_form_body(ISSUE_BODY)
        self.assertEqual(parsed["could a code-intent packet help your workflow"], "Yes, clearly")
        self.assertEqual(parsed["which delivery model would you prefer"], "Hosted private materializer")

    def test_no_issues_is_unproven(self) -> None:
        result = score_issues([])
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["demand_status"], "UNPROVEN")
        self.assertEqual(result["valid_response_count"], 0)

    def test_valid_issues_can_only_promote_to_early_signal(self) -> None:
        issues = [{"number": idx + 1, "url": f"https://example.test/{idx}", "body": ISSUE_BODY} for idx in range(3)]
        result = score_issues(issues)
        self.assertEqual(result["valid_response_count"], 3)
        self.assertEqual(result["demand_signal_count"], 3)
        self.assertEqual(result["demand_status"], "EARLY_POSITIVE_SIGNAL")

    def test_malformed_issue_is_not_demand(self) -> None:
        result = score_issues([{"number": 1, "url": "https://example.test/1", "body": "looks cool"}])
        self.assertEqual(result["valid_response_count"], 0)
        self.assertEqual(result["template_or_invalid_count"], 1)


if __name__ == "__main__":
    unittest.main()
