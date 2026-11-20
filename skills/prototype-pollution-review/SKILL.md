---
name: prototype-pollution-review
description: "Assess untrusted object merging and property assignment."
---

# JavaScript prototype integrity

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Node.js sandbox, source viewer.

## Workflow

1. Trace parsing and merge paths using source or local fixtures.
2. Use harmless synthetic properties to detect changes to inherited state.
3. Identify a reachable consumer before claiming a security consequence.

## Evidence required

Pollution source, affected object state and observed downstream consumer.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger prototype pollution](https://portswigger.net/web-security/prototype-pollution)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

