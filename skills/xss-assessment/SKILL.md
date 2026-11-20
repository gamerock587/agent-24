---
name: xss-assessment
description: "Trace untrusted input into browser execution contexts."
---

# Cross-site scripting assessment

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Browser, Burp.

## Workflow

1. Identify reflection, stored rendering and client-side sinks.
2. Determine the HTML, attribute, URL or script context and existing encoding.
3. Use a harmless visible marker in an isolated test session; preserve the rendered DOM and console evidence.

## Evidence required

A controlled browser execution result attributed to the input and affected origin.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger XSS](https://portswigger.net/web-security/cross-site-scripting)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

