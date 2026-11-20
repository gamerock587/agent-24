---
name: cloud-review
description: "Review authorized cloud configuration snapshots."
---

# Cloud configuration review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Provider read-only APIs.

## Workflow

1. Record account, region and the read-only audit role.
2. Evaluate identity permissions, public exposure, secrets handling and logging from configuration evidence.
3. Distinguish effective permissions from policy text and document service-specific uncertainty.

## Evidence required

Resource identifiers, policy context and read-only configuration evidence.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [AWS security best practices](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

