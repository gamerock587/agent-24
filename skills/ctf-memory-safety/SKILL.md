---
name: ctf-memory-safety
description: "Investigate a local memory-safety challenge."
---

# CTF memory safety

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Debugger, Pwntools.

## Workflow

1. Record architecture, mitigations and provided libraries.
2. Reproduce a bounded crash and identify the input-dependent memory operation.
3. Use the challenge environment to validate the hypothesis and retain a deterministic reproducer.

## Evidence required

Crash trace, input, exact binary version and challenge-defined success evidence.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Pwntools documentation](https://docs.pwntools.com/en/stable/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

