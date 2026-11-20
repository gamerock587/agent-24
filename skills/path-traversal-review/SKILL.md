---
name: path-traversal-review
description: "Assess file access confinement."
---

# Filesystem path boundary review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Local fixture, HTTP client.

## Workflow

1. Identify file selectors and expected permitted directories.
2. Test canonicalization and normalization with synthetic files.
3. Verify the resolved path remains inside the allowed root for all accepted forms.

## Evidence required

A test-owned file outside the intended root accessed through the affected feature.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger path traversal](https://portswigger.net/web-security/file-path-traversal)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

