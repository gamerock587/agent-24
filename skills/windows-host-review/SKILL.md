---
name: windows-host-review
description: "Review a supplied Windows lab host and service permissions."
---

# Windows host security review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Read-only PowerShell inventory.

## Workflow

1. Map service identities, executable paths and filesystem ACLs.
2. Distinguish administrative access already granted from newly reachable privilege.
3. Validate suspected configuration faults on a disposable test VM.

## Evidence required

Service configuration, effective ACLs and reproducible test-owned result.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Microsoft Active Directory security](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/best-practices-for-securing-active-directory)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

