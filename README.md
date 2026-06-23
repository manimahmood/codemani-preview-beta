# CodeMani Preview Beta

**Patent Notice:** CodeMani technologies, data containers, and associated
workflows are patent pending. No patent license is granted by this beta repo
beyond the limited evaluation permission stated in [LICENSE](LICENSE).

CodeMani is a compact code-intent workflow. A `.mani` packet stores the intent,
source fingerprints, requested materialization target, and safety boundary for
a supported code transformation. A trusted materializer can expand that packet
into generated code, while unsupported profiles fail closed instead of
guessing.

This repository is a public-safe beta preview. It is intended for review before
broad public promotion.

## What I Am Asking Reviewers To Do

You are not being asked to review a full transpiler or trust hidden internals.
Please judge the public boundary:

1. Is the `.mani` code-intent packet idea understandable?
2. Does the synthetic replay make the workflow credible enough to want a hosted
   or local materializer demo?
3. Would this help a real workflow such as migration review, reproducible
   AI-codegen, agent safety, or internal code transformation?
4. What would you need before trying this on real code?

Fastest path: read this README, run `python tools/run_review.py`, then open a
"Beta feedback" issue with your answers. If you do not want to run anything,
feedback from reading the packet/docs is still useful.

For the exact reviewer flow, see [docs/reviewer_guide.md](docs/reviewer_guide.md).
For a visual overview, see [docs/workflow_flow.md](docs/workflow_flow.md).
For the materialization receipt verifier, see
[docs/materialization_proof.md](docs/materialization_proof.md).
For the optional hosted API boundary, see
[docs/hosted_api_contract.md](docs/hosted_api_contract.md).
For a short comparison against AI coding environments such as Replit, see
[docs/faq.md](docs/faq.md).

## What This Repo Includes

- `codemani_review/` - a small packet inspector for synthetic `.mani` examples
- `examples/synthetic_package_slice.mani` - a synthetic demo packet
- `examples/source/` - synthetic source files referenced by the demo packet
- `examples/materialized/` - precomputed generated JavaScript for the demo
- `examples/materialization_receipt.json` - public synthetic materialization
  receipt for source/packet/output/oracle consistency
- `examples/materialized/oracle.js` - a Node.js oracle for the precomputed output
- `tools/inspect_packet.py` - standalone synthetic `.mani` inspection
- `tools/verify_materialization_receipt.py` - verifies the public receipt
- `tools/run_review.py` - one-command review replay
- `docs/` - claims, limits, hosted materializer plan, and workflow diagram
- GitHub issue and pull-request templates for structured feedback

## What This Repo Does Not Include

- No private materializer implementation
- no private repair engine
- no LLM proposer, prompts, or model code
- no proprietary source corpus
- no customer code
- no private endpoints, API keys, hostnames, or internal evidence
- no production signing keys

The public boundary is intentionally narrow: this repo lets reviewers inspect a
synthetic `.mani` capsule shape and replay precomputed output. It does not
open-source the private engine that authors, optimizes, repairs, or broadly
materializes CodeMani packets.

## Quick Review

Requirements:

- Python 3.10 or newer
- Node.js 18 or newer for the included JavaScript oracle
- No `pip install` or `npm install` is required

Clone and run:

```bash
git clone https://github.com/manimahmood/codemani-preview-beta.git
cd codemani-preview-beta
python tools/run_review.py
```

Expected result: JSON with `"status": "PASS"`. The real output includes extra
packet/check fields, for example:

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

The review script validates the synthetic packet container, checks source
hashes, confirms the precomputed JavaScript exists, and runs the Node oracle.
It does not materialize new code.

To inspect only the synthetic `.mani` packet:

```bash
python tools/inspect_packet.py
```

To verify the public synthetic materialization receipt:

```bash
python tools/verify_materialization_receipt.py
```

## Optional Hosted Materialization

This repo also includes a thin optional client for a hosted/private
materializer API. The client sends a `.mani` packet to an allowlisted HTTPS
endpoint and validates the response schema and size budget. The server-side
materializer is not included in this repo.

## Current Public Claim

This repo demonstrates the inspectable review boundary for a compact
code-intent packet. The stronger private claim, already tested separately, is
that a trusted private materializer can expand supported `.mani` capsules and
fail closed on unsupported or tampered inputs.

## Feedback

Useful feedback answers one question: would you reach for this workflow if the
private materializer were available as a hosted API, a local tool, or both?

Please include:

1. Is the `.mani` code-intent workflow understandable?
2. Would a compact intent packet help review, reproduce, or transfer a coding
   task better than raw prompt history?
3. What would you need before trusting a hosted/private materializer path?
4. What part of the boundary is unclear or concerning?
5. Would you prefer local materialization, hosted materialization, or both?

Use GitHub Issues for quick feedback:

- "Beta feedback" for workflow, trust, and usefulness
- "Bug report" for packet inspection, hash, or replay failures

Use a pull request if you want to leave a structured review without changing
code: copy `review_notes/TEMPLATE.md` to `review_notes/<your-handle>.md`, fill
it out, and open a PR.

For a public-safe announcement draft, see
[docs/public_beta_announcement.md](docs/public_beta_announcement.md).

Maintainers can summarize review-note PRs without promoting weak demand:

```bash
python tools/score_feedback.py
```

Maintainers can also summarize GitHub feedback issues:

```bash
python tools/score_github_feedback.py --repo manimahmood/codemani-preview-beta
```

That command uses the GitHub CLI and requires an authenticated `gh` session.
For offline scoring, pass exported issue JSON with `--issues-json <path>`.
