---
name: ssti-review
description: "Assess whether user data becomes template instructions."
---

# Template evaluation review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: HTTP client, source viewer.

## Workflow

1. Identify dynamic template creation paths.
2. Compare harmless expression-like inputs with literal controls in a lab.
3. Confirm evaluation occurs server-side and locate the template engine boundary.

## Evidence required

A benign computed result or source trace proving unintended template evaluation.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger template injection](https://portswigger.net/web-security/server-side-template-injection)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

