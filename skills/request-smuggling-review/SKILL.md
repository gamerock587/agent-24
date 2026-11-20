---
name: request-smuggling-review
description: "Review request framing disagreements between controlled HTTP components."
---

# HTTP parser consistency

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Dedicated proxy-backend lab.

## Workflow

1. Document the proxy-to-backend chain and protocol versions.
2. Prefer a dedicated lab so malformed requests cannot affect other users.
3. Compare component parsing and connection behavior using bounded cases.

## Evidence required

Correlated proxy and backend traces demonstrating different request boundaries.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger HTTP request smuggling](https://portswigger.net/web-security/request-smuggling)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

