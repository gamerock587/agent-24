---
name: finding-report
description: "Produce a self-contained evidence-based vulnerability report."
---

# Vulnerability finding report

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Report templates.

## Workflow

1. State affected asset, root cause, prerequisites and the observed consequence.
2. Include minimal redacted reproduction evidence and remediation tied to the root cause.
3. Label candidates separately; do not claim a completed test when execution failed.

## Evidence required

A reviewer can reproduce the finding from the stated environment and evidence.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

