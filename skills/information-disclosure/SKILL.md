---
name: information-disclosure
description: "Review errors and public responses for unintended data exposure."
---

# Unintended information exposure

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Browser, HTTP client.

## Workflow

1. Identify diagnostic, metadata and static-resource surfaces.
2. Capture minimal evidence without collecting unrelated sensitive records.
3. Distinguish public documentation from material that violates an actual confidentiality boundary.

## Evidence required

Minimal redacted excerpt, exposure path and expected access rule.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger information disclosure](https://portswigger.net/web-security/information-disclosure)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

