---
name: cors-review
description: "Assess cross-origin response access."
---

# CORS policy review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Browser, HTTP client.

## Workflow

1. Record allowed origins, credential handling and preflight responses.
2. Use a controlled origin with synthetic accounts to test browser enforcement.
3. Separate server header mistakes from an actual cross-origin readable sensitive response.

## Evidence required

Browser-observed response access with affected origin and credential context.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger CORS](https://portswigger.net/web-security/cors)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

