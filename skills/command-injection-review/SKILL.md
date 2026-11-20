---
name: command-injection-review
description: "Assess separation of untrusted input from operating-system commands."
---

# Process invocation boundary review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Source viewer, sandboxed fixture.

## Workflow

1. Trace request values to process invocation or review the corresponding source.
2. Prefer a local fixture with a harmless marker and bounded runtime.
3. Confirm whether arguments remain data or influence command structure.

## Evidence required

Input-to-invocation trace and controlled observable result.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger command injection](https://portswigger.net/web-security/os-command-injection)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

