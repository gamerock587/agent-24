---
name: csrf-review
description: "Assess origin and token enforcement on state-changing requests."
---

# CSRF protection review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Two local origins, browser.

## Workflow

1. Identify a reversible state change in a test account.
2. Examine token binding, origin checks and cookie behavior.
3. Compare same-origin and controlled cross-origin requests, then restore test state.

## Evidence required

A confirmed change from the controlled foreign origin or documented rejection.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger CSRF](https://portswigger.net/web-security/csrf)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

