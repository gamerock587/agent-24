---
name: xxe-review
description: "Assess XML parser configuration and external entity handling."
---

# XML parser boundary review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: XML fixture, HTTP client.

## Workflow

1. Locate XML parsing paths and determine library configuration.
2. Use synthetic documents and test-owned resources in a lab.
3. Compare entity resolution behavior against a control without reading host secrets.

## Evidence required

Parser configuration or a reproducible test-owned external-resource resolution.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger XXE](https://portswigger.net/web-security/xxe)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

