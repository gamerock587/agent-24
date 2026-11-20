---
name: session-review
description: "Check session invalidation and state transitions."
---

# Session lifecycle review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Browser, HTTP client.

## Workflow

1. Record session creation, rotation, logout and credential-change behavior.
2. Compare pre-transition and post-transition sessions with designated accounts.
3. Verify expiry and server-side invalidation separately from browser cookie removal.

## Evidence required

A transition matrix and redacted evidence of accepted or rejected stale sessions.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [OWASP ASVS](https://owasp.org/projects/asvs)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

