# CodeMani Beta Review - <your handle>

**Patent Notice:** CodeMani technologies, data containers, and associated
workflows are patent pending. No patent license is granted by this beta repo
beyond the limited evaluation permission stated in `LICENSE`.

Please copy this file to `review_notes/<your-handle>.md`, fill it out, and open
a pull request. Remove anything you do not want public.

The main thing I need to learn is whether this compact code-intent packet would
help you review, reproduce, or transfer AI-assisted coding work better than raw
prompt history or a generated patch.

Do not include private prompts, proprietary code, API keys, customer data,
private repository names, or private paths.

## Reviewer Context

- I build developer tools: [yes/no]
- I use AI coding tools regularly: [yes/no]
- I work on code migration/transpilation: [yes/no]
- My rough use case: [review, migration, agent safety, internal tooling, other]

## What I Tried

- Ran `python tools/run_review.py`: [yes/no]
- Inspected the `.mani` packet: [yes/no]
- Tried the hosted API client: [yes/no/not applicable]
- OS/runtime, if relevant: [for example: Windows + Python 3.12 + Node 24]

## Core Question

Would a compact code-intent packet help review, reproduce, or transfer a coding
task better than raw prompt history or a generated patch?

- Answer: [yes/maybe/no]
- Why: [what specific workflow would it help, or why would it not help?]

## Local vs Hosted

Which would you prefer?

- Preferred shape: [local materializer / hosted private materializer / both / review packet only]
- Why: [security, reproducibility, install friction, speed, auditability, other]

## Most Valuable Part

Pick one, then explain:

- Choice: [intent packet / hash-source verification / fail-closed unsupported profiles / hosted private materializer boundary / precomputed replay packet / not useful yet]

Explain: [what made this useful or not useful?]

## Confusing Or Missing

What made this hard to understand or trust?

[your answer]

## One Change That Would Make Me Try Again

What should be improved first?

[your answer]

## Would I Use This Again?

- Answer: [yes/maybe/no]
- What would need to be true: [hosted demo, more examples, real migration case, clearer docs, production security review, other]
