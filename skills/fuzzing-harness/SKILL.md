---
name: fuzzing-harness
description: "Create a bounded local harness for a test-owned parser or library."
---

# Fuzzing harness design

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Compiler sanitizers, fuzzer.

## Workflow

1. Select a deterministic entry point and small representative seed corpus.
2. Use relevant sanitizers and track coverage rather than only execution count.
3. Minimize crashes and reproduce them outside the fuzzer before interpreting impact.

## Evidence required

Harness, corpus hash, coverage context and minimized reproducible failure.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Trail of Bits testing handbook](https://appsec.guide/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

