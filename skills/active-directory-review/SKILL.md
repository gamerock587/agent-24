---
name: active-directory-review
description: "Review supplied directory configuration and approved lab observations."
---

# Active Directory configuration review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Read-only directory queries.

## Workflow

1. Map test identities, privileged roles and trust relationships.
2. Compare effective permissions with the documented administrative model.
3. Use a lab to validate suspected escalation paths and document prerequisites.

## Evidence required

Objects, effective access rules and independently verified path prerequisites.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Microsoft Active Directory security](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/best-practices-for-securing-active-directory)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

