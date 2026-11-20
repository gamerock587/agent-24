---
name: host-header-review
description: "Review application decisions based on host and forwarding headers."
---

# Host-derived trust review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: HTTP client, proxy fixture.

## Workflow

1. Identify generated links, origin checks and routing rules.
2. Compare valid hosts with controlled alternate values in a lab.
3. Trace which ingress component normalizes or trusts each value.

## Evidence required

A reproducible incorrect host-derived decision and component trace.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger Host headers](https://portswigger.net/web-security/host-header)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

