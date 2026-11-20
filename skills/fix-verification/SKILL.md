---
name: fix-verification
description: "Verify a supplied fix against a demonstrated failure."
---

# Security fix verification

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Local test runner.

## Workflow

1. Pin the vulnerable and fixed revisions and reproduce the original failure locally.
2. Run the same reproducer against the fix and test nearby valid behavior.
3. Check adjacent variants and explicitly record any untested deployment assumptions.

## Evidence required

Before-after result, preserved reproducer and regression evidence.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Trail of Bits testing handbook](https://appsec.guide/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

