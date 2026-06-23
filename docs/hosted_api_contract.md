# Hosted API Contract

The hosted materializer path is optional. It lets a reviewer send a `.mani`
packet to a trusted private server without shipping the private materializer in
this repository.

Default endpoint:

```text
https://api.sfiniti.ai/v1/materialize
```

## Request

```json
{
  "schema": "codemani.materializer.request.v1",
  "target": "javascript.commonjs",
  "mani_b64": "<base64 .mani bytes>"
}
```

Authorization, when enabled, uses a bearer token from `CODEMANI_API_TOKEN` or
another explicitly selected `CODEMANI_*` / `SFINITI_*` environment variable.

## Response

```json
{
  "schema": "codemani.materializer.response.v1",
  "status": "PASS",
  "artifacts": []
}
```

The public client rejects unexpected schemas, non-`PASS` status values,
oversized `.mani` files, oversized responses, unapproved hosts, and non-HTTPS
remote URLs.

## Boundary

This contract is the public API boundary only. The private server-side
materializer, sandbox policy, signing policy, and repair engine are not part of
this repository.
