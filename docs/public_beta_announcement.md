# CodeMani Public Beta Announcement Draft

CodeMani is a public-safe preview of a compact code-intent packet workflow.

Instead of treating a generated patch or prompt transcript as the durable unit
of work, CodeMani uses a `.mani` packet to carry transformation intent, source
fingerprints, target runtime, and safety boundaries. This repo lets reviewers
inspect a synthetic packet, replay precomputed JavaScript output, and evaluate
the optional hosted/private materializer boundary.

## Short Post

I opened a small beta preview for CodeMani, a code-intent packet workflow for
reproducible AI-assisted code transformation.

The public repo includes:

- a synthetic `.mani` packet;
- source hash verification;
- precomputed JavaScript output;
- a Node oracle;
- a public-safe hosted API client boundary;
- structured feedback templates.

It does not include the private materializer, repair engine, private prompts,
customer code, model code, or production signing keys.

Try:

```bash
git clone https://github.com/manimahmood/codemani-preview-beta.git
cd codemani-preview-beta
python tools/run_review.py
```

Feedback I am looking for:

1. Is the code-intent packet model understandable?
2. Would this help with migration review, agent safety, reproducible codegen,
   or internal tooling?
3. Would you prefer local materialization, hosted private materialization, or
   both?
4. What would you need before trusting this workflow on real code?

You can review it four ways: read-only, local replay with
`python tools/run_review.py`, standalone packet inspection with
`python tools/inspect_packet.py`, or hosted-boundary review using
`docs/hosted_api_contract.md`. No `pip install` or `npm install` is required.
The useful feedback is not "does this replace a developer"; it is whether this
packet-and-replay workflow would be useful in a real code review, migration, or
agent-safety process.

Please do not paste private prompts, proprietary code, API keys, customer data,
private repository names, or private paths into issues or review notes.

## Boundary

This beta does not claim arbitrary Python translation, broad COBOL
modernization, autonomous production refactoring, production sandboxing, public
package-index readiness, or market demand.

The public repo demonstrates an inspectable review boundary. The stronger
private materialization claims are tested separately and are not open-sourced in
this preview.
