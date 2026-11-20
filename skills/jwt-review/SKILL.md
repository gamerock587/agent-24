---
name: jwt-review
description: "Assess token acceptance rules with test-owned signing keys."
---

# JWT verification review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Local JWT fixture, HTTP client.

## Workflow

1. Record supported algorithms, key selection and claim checks.
2. Compare valid fixtures with narrowly altered signatures or claims.
3. Verify the server rejects invalid binding, expiry, audience and issuer conditions.

## Evidence required

An acceptance matrix with synthetic tokens and server-side outcome.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger JWT](https://portswigger.net/web-security/jwt)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

