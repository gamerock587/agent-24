---
name: linux-host-review
description: "Review test-owned Linux host permissions and security mechanisms."
---

# Linux host security review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Read-only host inventory.

## Workflow

1. Record OS, service identities and relevant filesystem permissions.
2. Compare intended access with effective privilege and service configuration.
3. Reproduce suspected local privilege boundaries in a disposable lab before reporting.

## Evidence required

Configuration evidence, effective identity and controlled boundary test.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Linux kernel security](https://docs.kernel.org/security/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

