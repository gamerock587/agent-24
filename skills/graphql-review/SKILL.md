---
name: graphql-review
description: "Assess GraphQL object and operation boundaries."
---

# GraphQL authorization and exposure

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: GraphQL client.

## Workflow

1. Inventory documented operations and designated test identities.
2. Compare authorization on nested fields and mutations with the equivalent resource rules.
3. Keep query complexity bounded and treat schema exposure separately from data access.

## Evidence required

Operation, identity, variables and affected resolver behavior.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger GraphQL](https://portswigger.net/web-security/graphql)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

