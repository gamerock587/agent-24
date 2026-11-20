---
name: sql-injection
description: "Investigate whether untrusted input changes SQL query structure."
---

# SQL injection assessment

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: HTTP client, database test fixture.

## Workflow

1. Locate inputs plausibly used in database queries and capture a valid control.
2. Use small lab-safe differential cases while keeping other variables unchanged.
3. Compare response content, errors and timing against repeated controls; confirm the input-to-query boundary if source is available.

## Evidence required

Repeatable query-behavior difference tied to one input, with plausible alternate causes ruled out.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger SQL injection](https://portswigger.net/web-security/sql-injection)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

