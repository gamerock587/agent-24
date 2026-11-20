---
name: skill-selection
description: "Select a small relevant subset of skill instructions for a job."
---

# Skill retrieval and context budgeting

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Registry, text search.

## Workflow

1. Index skill names, descriptions, domains and prerequisites.
2. Retrieve candidate metadata first, then load only selected instructions and references.
3. Record why each skill was selected and reject unreviewed upstream packages from automatic execution.

## Evidence required

Skill IDs, loaded document hashes and task-specific selection rationale.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Agent Skills specification](https://agentskills.io/specification)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

