# CodeMani FAQ

## How is this different from Replit or an AI coding agent?

Replit-style tools are interactive coding environments. They help you write,
run, deploy, and iterate on code in a workspace.

CodeMani is narrower. It is a verifiable code-intent packet workflow. A `.mani`
packet carries a bounded transformation request, source fingerprints, fixtures,
and policy metadata so a trusted materializer can either produce a checked
artifact or fail closed.

In plain terms:

- Replit is where you build and run software.
- CodeMani is a receipt-backed way to package and replay a specific supported
  code transformation.

## Is CodeMani a general transpiler?

No. The public preview demonstrates a narrow synthetic path. The private
materializer only promotes supported profiles and rejects unsupported syntax
instead of guessing.

## Is CodeMani an autonomous coding agent?

No. The important boundary is the harness, not an unbounded agent loop. The
packet records intent, constraints, fixtures, and expected materialization
behavior so a transformation can be reviewed and replayed.

## Why use a `.mani` packet instead of a prompt?

Prompts are easy to lose, edit accidentally, or interpret differently across
tools. A `.mani` packet is meant to preserve the task boundary: what source was
referenced, what target was requested, what checks matter, and what safety
policy applies.

## What should reviewers judge in this public repo?

Judge whether the review boundary is understandable and useful:

1. Can you inspect the synthetic packet?
2. Does `python tools/run_review.py` make the workflow clear?
3. Would a hosted or local materializer be useful for migration review,
   reproducible AI-codegen, internal code transformation, or agent safety?

Do not treat this public repo as a claim of arbitrary-code translation.
