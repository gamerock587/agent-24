---
name: dom-dataflow
description: "Review browser-side source-to-sink flows."
---

# DOM data-flow assessment

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Browser developer tools.

## Workflow

1. Trace URL, message and storage inputs through client scripts.
2. Identify parsing, transformation and dangerous DOM operations.
3. Build the smallest benign case that reaches the sink and verify the result in the affected browser.

## Evidence required

Source, transformation chain, sink and observed DOM outcome.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger DOM vulnerabilities](https://portswigger.net/web-security/dom-based)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

