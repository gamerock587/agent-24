---
name: ctf-cryptography
description: "Investigate cryptographic challenge assumptions."
---

# CTF cryptography analysis

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Python, SageMath when available.

## Workflow

1. Identify encoding, primitive, parameters and what the challenge reveals.
2. Write a small algebraic or probabilistic hypothesis before choosing a solver.
3. Check recovered values by re-encryption or another independent challenge relation.

## Evidence required

Reproducible local calculation and a verified relation or flag submission.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [CryptoHack](https://cryptohack.org/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

