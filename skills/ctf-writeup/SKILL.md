---
name: ctf-writeup
description: "Document a verified challenge solution for future retrieval."
---

# CTF solution writeup

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Markdown authoring.

## Workflow

1. Describe the challenge, environment and decisive observations.
2. Explain the successful hypothesis and preserve reproducible local steps.
3. Include failed assumptions that materially affected the approach and the actual verification result.

## Evidence required

A standalone writeup with hashes, reasoning, tools and confirmed outcome.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [pwn.college](https://pwn.college/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

