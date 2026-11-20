---
name: ctf-forensics
description: "Analyze challenge disk, memory or file artifacts."
---

# CTF artifact forensics

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Volatility, file metadata tools.

## Workflow

1. Hash originals and analyze working copies.
2. Select tools by artifact type and record parsing assumptions.
3. Correlate at least two independent indicators before drawing a timeline or flag conclusion.

## Evidence required

Artifact offsets, tool versions, extracted indicators and reproducible transformations.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Volatility 3 documentation](https://volatility3.readthedocs.io/en/latest/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

