---
name: evidence-management
description: "Preserve observations and prevent summaries from replacing evidence."
---

# Evidence and provenance management

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Local evidence store.

## Workflow

1. Assign stable IDs to raw observations, actions, artifacts and findings.
2. Hash artifacts, redact secrets in reports and keep originals under controlled access.
3. Require every promoted finding to cite actual successful tool outcomes.

## Evidence required

An evidence graph linking claims to raw observations and artifact hashes.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [OWASP GenAI security project](https://genai.owasp.org/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

