---
name: file-upload-review
description: "Assess uploaded-file validation, storage and processing."
---

# Upload processing review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Browser, metadata tools.

## Workflow

1. Map extension, content-type and file-content validation.
2. Use inert synthetic files and record names, storage location and serving headers.
3. Check whether processing or later retrieval crosses the intended trust boundary.

## Evidence required

An observed validation or serving failure with no dangerous uploaded executable.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger file upload](https://portswigger.net/web-security/file-upload)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

