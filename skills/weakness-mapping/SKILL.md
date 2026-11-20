---
name: weakness-mapping
description: "Classify an observed root cause and relevant behavior."
---

# Weakness and technique mapping

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Taxonomy lookup.

## Workflow

1. Describe the failing control before choosing a taxonomy label.
2. Select the most specific supported CWE and only observed ATT&CK behavior.
3. Keep root cause, vulnerability identifier and adversary technique as separate fields.

## Evidence required

Evidence-linked classification with uncertainty when the mapping is ambiguous.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [MITRE CWE Top 25](https://cwe.mitre.org/top25/)
- [MITRE ATT&CK](https://attack.mitre.org/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

