---
name: deserialization-review
description: "Review processing of untrusted serialized objects."
---

# Deserialization boundary review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Source viewer, local fixture.

## Workflow

1. Identify formats, entry points and accepted types.
2. Inspect allowlists and validation before object reconstruction.
3. Use inert local fixtures to demonstrate unexpected type or behavior selection.

## Evidence required

A minimal object-processing deviation and affected parser configuration.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger deserialization](https://portswigger.net/web-security/deserialization)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

