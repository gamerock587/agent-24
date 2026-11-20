---
name: severity-assessment
description: "Assess a confirmed finding using explicit CVSS assumptions."
---

# Evidence-based severity assessment

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: CVSS calculator.

## Workflow

1. Record observed prerequisites, affected privileges and demonstrated impact.
2. Calculate a version-labelled vector and justify each metric.
3. Report business context separately and avoid speculative impact inflation.

## Evidence required

CVSS vector, metric rationale and evidence for prerequisites and consequences.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [FIRST CVSS v4 specification](https://www.first.org/cvss/v4.0/specification-document)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

