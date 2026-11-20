---
name: lab-management
description: "Prepare reproducible local targets for testing agent behavior."
---

# Isolated laboratory management

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Containers or isolated VMs.

## Workflow

1. Choose a deliberately vulnerable lab and pin its version.
2. Keep lab traffic inside a dedicated network; record reset and health procedures.
3. Reset between independent attempts and verify that learner accounts contain only synthetic data.

## Evidence required

Lab version, network boundary, initial-state fingerprint and reset result.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/)
- [OWASP WebGoat](https://owasp.org/www-project-webgoat/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

