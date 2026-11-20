---
name: encoding-and-steganography
description: "Investigate encoding and hidden-data challenges."
---

# CTF encoding and hidden data

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: CyberChef, local Python.

## Workflow

1. Identify magic bytes, metadata and candidate encodings.
2. Record a reversible transformation recipe rather than guessing a chain indefinitely.
3. Validate extracted content against expected structure or challenge submission.

## Evidence required

Original hash, transformation recipe and verified output.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [CyberChef](https://github.com/gchq/CyberChef)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

