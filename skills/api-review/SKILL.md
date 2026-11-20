---
name: api-review
description: "Review API operations against object, property and function permissions."
---

# REST API control review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: OpenAPI parser, HTTP client.

## Workflow

1. Build an operation-role-resource matrix from the supplied API specification.
2. Use synthetic objects to check property updates, object access and privileged functions.
3. Assess resource limits within the agreed budget and verify upstream data is validated.

## Evidence required

Per-operation control results and concrete demonstrated failures.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [OWASP API Security 2023](https://api-security.owasp.org/editions/2023/en/0x11-t10/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

