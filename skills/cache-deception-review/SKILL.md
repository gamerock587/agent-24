---
name: cache-deception-review
description: "Assess whether sensitive responses are incorrectly shared or cached."
---

# Sensitive response caching

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: HTTP client, dedicated cache lab.

## Workflow

1. Map route interpretation and cache rules for test-account pages.
2. Use unique synthetic data and dedicated paths.
3. Verify cache reuse under a separate test identity and remove the test artifact.

## Evidence required

Evidence that account-specific content is served from an unintended cache context.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger cache deception](https://portswigger.net/web-security/web-cache-deception)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

