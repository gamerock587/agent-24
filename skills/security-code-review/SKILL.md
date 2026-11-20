---
name: security-code-review
description: "Investigate code paths that cross a trust boundary."
---

# Security source-to-sink review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Source viewer, CodeQL.

## Workflow

1. Trace untrusted inputs through validation and transformations to a sensitive operation.
2. Verify the route is reachable under the real entry-point and identity constraints.
3. Look for existing guards and construct a local reproducer before promoting a candidate.

## Evidence required

File and line references, reachability argument and reproducer or explicit validation gap.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [CodeQL documentation](https://codeql.github.com/docs/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

