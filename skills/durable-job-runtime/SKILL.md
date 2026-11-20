---
name: durable-job-runtime
description: "Design persistent jobs that survive failures and avoid endless repetition."
---

# Durable 24-hour job design

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Scheduler, persistent database.

## Workflow

1. Persist state transitions, leases, attempt counts and next scheduled time.
2. Bound each job and retry only actions whose replay semantics are known.
3. Recover by re-observing external state; idle when no work remains and break recurring failures.

## Evidence required

Crash-recovery test results, duplicate-action checks and bounded resource metrics.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [OWASP GenAI security project](https://genai.owasp.org/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

