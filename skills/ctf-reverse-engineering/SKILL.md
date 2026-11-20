---
name: ctf-reverse-engineering
description: "Recover relevant behavior from a challenge binary."
---

# CTF reverse engineering

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Ghidra, debugger.

## Workflow

1. Record format, architecture, imports and artifact hash.
2. Trace the input-validation path and annotate only relevant functions.
3. Test reconstructed behavior against the original binary in an isolated environment.

## Evidence required

Annotated control flow and an input independently accepted by the challenge.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Ghidra project](https://github.com/NationalSecurityAgency/ghidra)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

