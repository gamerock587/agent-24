---
name: business-logic-review
description: "Test application rules across multi-step workflows."
---

# Business workflow invariants

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Browser, HTTP client.

## Workflow

1. Write explicit invariants for the supplied synthetic workflow.
2. Compare legitimate paths with omitted, repeated or reordered steps.
3. Restore state after each reversible test and separate logic faults from UI-only inconsistencies.

## Evidence required

State transitions and a reproducible violation of the declared business rule.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger business logic](https://portswigger.net/web-security/logic-flaws)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

