# Hosted Materializer Plan

This repo ships a public-safe inspector and replay packet, plus an opt-in
hosted client for private-preview materializer APIs.

The hosted path mirrors the ManiMotion pattern:

```text
review script or client -> HTTPS API -> private CodeMani materializer -> artifact response
```

The public client contains:

- `.mani` size checks
- HTTPS and allowlisted-host checks
- bearer token lookup from environment variables
- request/response schema checks
- response size limits
- no private materializer logic

The private server would contain:

- proprietary materializer implementation
- decryption and signing policy
- authentication and rate limits
- sandboxed workers
- artifact TTL cleanup
- non-payload telemetry

## Endpoint

The default preview endpoint is:

```text
https://api.sfiniti.ai/v1/materialize
```

Set `CODEMANI_API_TOKEN` in your shell if the endpoint requires a bearer token.
Do not paste live tokens into GitHub Issues, workflow files, screenshots, or
review notes.

## Boundary

The hosted path is for beta hardening. Do not add private materializer internals
to this public candidate repository.

The API URL must be an exact machine-callable endpoint. A normal website URL
may sit behind browser-focused security controls and is not automatically a
valid materializer endpoint.
