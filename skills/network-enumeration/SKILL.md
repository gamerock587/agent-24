---
name: network-enumeration
description: "Identify services on an explicit authorized host list."
---

# Network service enumeration

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Nmap.

## Workflow

1. Start with a narrow port set and agreed rate; record tool version and options.
2. Treat port state and service guesses as separate observations.
3. Confirm a suspected service using its protocol before selecting a vulnerability check.

## Evidence required

Host, port, state, protocol response and timestamp; no vulnerability claim from a banner alone.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Nmap reference guide](https://nmap.org/book/man.html)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

