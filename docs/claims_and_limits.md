# Claims And Limits

## Current Public Claims

- `.mani` can store a compact code-intent packet.
- The synthetic packet in this repo is inspectable and hash-verified.
- The included precomputed JavaScript passes a Node oracle.
- The optional hosted client can send `.mani` packets to a configured private
  materializer API.
- The public repo includes no private materializer implementation.

## Private Preview Claims Not Proven By This Repo Alone

- A trusted private materializer can expand supported `.mani` capsules.
- Unsupported syntax fails closed instead of guessing.
- Tampered source fails closed.
- A signed private operator packet can replay outside the development checkout.

Those claims require the private preview packet and private evidence gates.

## What Not To Claim

- Do not claim arbitrary Python translation.
- Do not claim broad COBOL modernization.
- Do not claim autonomous production refactoring.
- Do not claim production sandboxing.
- Do not claim public package-index readiness.
- Do not claim market demand.
- Do not claim this repo contains the private materializer.

## Public Boundary

This repository exposes a public-safe review surface: synthetic `.mani`
inspection, precomputed replay, and a thin hosted-client boundary. It does not
expose proprietary authoring, repair, routing, materialization, LLM proposal, or
private evidence systems.
