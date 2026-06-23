# CodeMani Reviewer Guide

This repo is asking for product and trust feedback, not a full source-code audit.

## The Short Ask

Please answer:

1. Is the `.mani` packet workflow understandable?
2. Would this help a real coding workflow you have seen?
3. Would you prefer a hosted materializer, a local materializer, or both?
4. What would make you trust it enough to try on real code?

Do not paste private prompts, proprietary code, API keys, customer data, private
paths, or internal repository names.

## Pick One Review Path

### Path A: 2-Minute Read-Only Review

Use this if you do not want to run code.

1. Read the README.
2. Skim `docs/workflow_flow.md`.
3. Open a "Beta feedback" issue and answer whether the workflow is clear or useful.

### Path B: 5-Minute Local Replay

Use this if you have Python 3.10+ and Node.js 18+ installed. No `pip install`
or `npm install` is required.

```bash
git clone https://github.com/manimahmood/codemani-preview-beta.git
cd codemani-preview-beta
python tools/run_review.py
```

Expected result: JSON with `"status": "PASS"`. The real output includes packet
metadata and individual check fields.

```json
{
  "status": "PASS",
  "checks": {
    "packet_inspected": true,
    "source_hashes_match": true,
    "precomputed_js_present": true,
    "node_oracle_passed": true
  }
}
```

This checks the synthetic `.mani` packet, source hashes, precomputed JavaScript,
and Node oracle. It does not call the network and does not materialize new code.

To inspect only the synthetic `.mani` packet:

```bash
python tools/inspect_packet.py
```

To verify the public source/packet/output/oracle receipt:

```bash
python tools/verify_materialization_receipt.py
```

### Path C: Hosted Boundary Review

Use this if you want to evaluate the hosted/private materializer shape.

Read `docs/hosted_api_contract.md` and answer whether this boundary is the right
trust model. The public repo includes only a thin client; the server-side
materializer is not included.

## What A Useful Answer Looks Like

Useful:

- "I do migrations and would try this for Python-to-JavaScript fixture replay if
  the hosted API returned a signed receipt."
- "I would not use hosted materialization for client code, but I would use a
  local tool in CI."
- "The packet idea is clear, but I need a second example with a harder import
  graph."

Less useful:

- "Looks cool."
- "AI code is risky."
- "I do not like zip files."

## Where To Leave Feedback

- Use GitHub Issues for quick feedback.
- Use a pull request if you want to fill out `review_notes/TEMPLATE.md`.
- Use a bug report only for replay, hash, hosted-client, or packet-inspection
  failures.

## Boundary

This preview does not claim arbitrary Python translation, autonomous production
refactoring, production sandboxing, or market demand. It demonstrates a
public-safe review surface for a compact code-intent packet workflow.
