---
name: race-condition-review
description: "Assess concurrency-sensitive operations in an isolated lab."
---

# Concurrent state review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Controlled local concurrent client.

## Workflow

1. Identify state changes that should be atomic or single-use.
2. Define a very small concurrency budget and capture a serial control.
3. Compare synchronized lab requests and verify final persisted state.

## Evidence required

Repeatable invariant violation with request ordering and final-state evidence.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger race conditions](https://portswigger.net/web-security/race-conditions)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

