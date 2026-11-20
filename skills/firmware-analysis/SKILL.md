---
name: firmware-analysis
description: "Inspect supplied firmware images and extracted components."
---

# Firmware artifact review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Binwalk, filesystem viewers.

## Workflow

1. Hash the image and identify layout and embedded filesystems.
2. Extract only inside a bounded disposable workspace with size limits.
3. Review configurations and component versions without connecting to unrelated devices.

## Evidence required

Image offsets, extracted file hashes and version-matched observations.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Binwalk](https://github.com/ReFirmLabs/binwalk)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

