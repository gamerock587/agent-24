---
name: variant-analysis
description: "Search for other instances of a validated root cause."
---

# Root-cause variant analysis

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Code search, CodeQL.

## Workflow

1. Express the failure as a specific structural or data-flow pattern.
2. Search comparable code paths and inspect each candidate's guards and reachability.
3. Keep variants separate unless their fix and affected behavior are demonstrably shared.

## Evidence required

Candidate inventory with individual evidence and disposition.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [CodeQL documentation](https://codeql.github.com/docs/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

