---
name: static-analysis-triage
description: "Interpret scanner alerts without treating alerts as confirmed findings."
---

# Static analysis triage

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Semgrep, SARIF parser.

## Workflow

1. Record scanner version, rule set and repository revision.
2. Inspect the full data flow and guarding conditions for each relevant alert.
3. Deduplicate shared root causes and label rejected, candidate and confirmed outcomes.

## Evidence required

Rule ID, code references and evidence-supported disposition.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Semgrep documentation](https://semgrep.dev/docs/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

