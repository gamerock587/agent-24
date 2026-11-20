---
name: smart-contract-review
description: "Review test-owned contract code and local-chain invariants."
---

# Smart contract security review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Local chain, contract test framework.

## Workflow

1. Pin compiler, dependencies, deployment parameters and chain assumptions.
2. Identify state-changing entry points and authorization invariants.
3. Use local tests to check arithmetic, external calls, accounting and upgrade assumptions.

## Evidence required

Code references, local tests and demonstrated invariant violations.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [OWASP Smart Contract Security](https://scs.owasp.org/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

