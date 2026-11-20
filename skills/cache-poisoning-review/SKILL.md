---
name: cache-poisoning-review
description: "Assess shared-cache behavior for test-owned responses."
---

# Cache key and input consistency

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: HTTP client, local cache lab.

## Workflow

1. Determine which request inputs affect content and which form the cache key.
2. Use a unique test resource to separate cache effects from application variation.
3. Verify whether a response influenced by one input is reused for a different request.

## Evidence required

Cache hit evidence and controlled cross-request response influence.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger cache poisoning](https://portswigger.net/web-security/web-cache-poisoning)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

