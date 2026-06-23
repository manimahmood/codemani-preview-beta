# Public Materialization Proof

This repo does not include the private CodeMani materializer. It does include a
public synthetic receipt so reviewers can verify the sample chain end to end:

```text
source files -> .mani packet -> materialized JavaScript -> Node oracle
```

Run:

```bash
python tools/verify_materialization_receipt.py
```

Expected result: JSON with `"status": "PASS"`.

The verifier checks:

- the `.mani` packet opens and its container hash matches the receipt;
- source-file normalized hashes match the receipt;
- source hashes inside the packet intent match the shipped source files;
- materialized JavaScript hashes match the receipt;
- the Node oracle exits successfully and returns the recorded JSON.

## Boundary

This proof verifies consistency for the public synthetic sample. It does not
open-source the private materializer, prove arbitrary Python translation, or
prove market demand. It is meant to answer a narrower reviewer question:
"Do the public packet, source files, generated JavaScript, and oracle actually
line up?"
