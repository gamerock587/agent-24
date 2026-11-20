---
name: remediation-planning
description: "Prepare implementation-ready corrections for validated findings."
---

# Root-cause remediation planning

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Source viewer, report templates.

## Workflow

1. Identify the narrow failing control and affected owners.
2. Describe a correction at the actual trust boundary and any compatibility effects.
3. Define regression checks and verification evidence before marking the issue resolved.

## Evidence required

Fix plan with affected code or configuration and observable acceptance criteria.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [OWASP ASVS](https://owasp.org/projects/asvs)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

