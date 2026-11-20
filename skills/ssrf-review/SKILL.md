---
name: ssrf-review
description: "Assess server-side URL fetching within explicitly permitted destinations."
---

# Server outbound request review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Controlled callback service, HTTP client.

## Workflow

1. Identify URL-consuming features and redirects.
2. Use an approved callback endpoint containing no secrets.
3. Confirm which component made the request and whether destination checks survive parsing and redirects.

## Evidence required

Correlated request ID, approved callback evidence and demonstrated boundary behavior.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger SSRF](https://portswigger.net/web-security/ssrf)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

