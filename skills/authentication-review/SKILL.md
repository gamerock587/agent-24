---
name: authentication-review
description: "Assess identity verification using designated test accounts."
---

# Authentication controls

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Browser, HTTP client.

## Workflow

1. Map login, registration, recovery and multi-factor flows.
2. Check consistent identity binding, response handling and lifecycle behavior.
3. Use a bounded test matrix; do not turn a recovery check into unbounded credential guessing.

## Evidence required

Flow matrix with controls and reproducible identity-verification failures.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger authentication](https://portswigger.net/web-security/authentication)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

