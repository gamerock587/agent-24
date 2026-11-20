---
name: nosql-injection
description: "Investigate unsafe document-database query construction."
---

# NoSQL query assessment

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: HTTP client, local database fixture.

## Workflow

1. Identify query filters and accepted structured input types.
2. Compare valid input with controlled type or operator changes in a lab.
3. Check whether server-side validation and query construction preserve the intended predicate.

## Evidence required

Minimal test cases demonstrating unintended predicate behavior, not just a parser error.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger NoSQL](https://portswigger.net/web-security/nosql-injection)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

