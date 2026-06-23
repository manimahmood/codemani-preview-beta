# Security Policy

## Reporting

Please open a private security report or contact the maintainer before publicly
posting exploit details.

Do not include secrets, private prompts, proprietary source code, API keys, or
customer data in issues.

## Scope

In scope:

- malformed `.mani` packet handling
- unsafe archive extraction behavior
- denial-of-service risks from oversized packets
- incorrect payload hash or byte-count validation
- review-script failures

Out of scope:

- arbitrary code translation quality
- private materializer behavior
- hosted API availability
- unsupported language profiles

## Current Safety Controls

The packet inspector verifies:

- ZIP container size
- payload count
- payload byte count
- payload SHA-256
- manifest schema
- manifest size
- payload path safety
- zip compression ratio
- source hash agreement for the synthetic demo

The public review script does not execute generated Python, does not call a
network service, and does not materialize new code. It only inspects the
synthetic packet and runs the included JavaScript oracle.
