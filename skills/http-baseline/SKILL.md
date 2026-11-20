---
name: http-baseline
description: "Establish normal requests and responses before differential web tests."
---

# HTTP behavior baseline

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Burp, browser, HTTP client.

## Workflow

1. Capture a legitimate request using a synthetic test account.
2. Record method, path, content type, redirects, session state and relevant headers.
3. Repeat the control request to distinguish caching, timing variation and expired login from test effects.

## Evidence required

Redacted request-response pairs and stable control behavior.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Burp Suite documentation](https://portswigger.net/burp/documentation)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

