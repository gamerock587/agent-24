---
name: ctf-osint
description: "Resolve challenge clues using publicly accessible evidence."
---

# CTF public-source research

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Web research, metadata viewer.

## Workflow

1. Separate the challenge's permitted subjects from unrelated people.
2. Track source URLs, dates and confidence for each clue.
3. Require independent corroboration for location or identity conclusions; avoid contacting subjects.

## Evidence required

Source-backed clue chain and challenge verification.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [picoCTF getting started](https://picoctf.org/get_started.html)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

