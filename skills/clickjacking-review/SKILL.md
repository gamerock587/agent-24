---
name: clickjacking-review
description: "Assess whether sensitive controls can be framed by an unintended origin."
---

# UI framing review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Browser, local test page.

## Workflow

1. Identify reversible test actions and inspect framing protections.
2. Build a local framing test without real purchases or account changes.
3. Confirm frame rendering and interaction requirements in a browser.

## Evidence required

Framing outcome, response policies and required user interactions.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger clickjacking](https://portswigger.net/web-security/clickjacking)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

