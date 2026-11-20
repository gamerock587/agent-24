---
name: authorization-review
description: "Verify role, tenant and object authorization boundaries."
---

# Authorization and object access

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: HTTP client, browser.

## Workflow

1. Create a matrix of resources, operations and two supplied test identities.
2. Compare authorized and unauthorized requests using only test-owned objects.
3. Verify server-side enforcement across alternate methods and workflow steps.

## Evidence required

A demonstrated unauthorized operation or disclosure between controlled identities.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger access control](https://portswigger.net/web-security/access-control)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

