---
name: llm-application-review
description: "Assess trust boundaries in applications that consume model output."
---

# AI-integrated application review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Isolated agent test harness.

## Workflow

1. Map retrieved content, tool permissions and downstream consumers.
2. Use harmless controlled instructions embedded in test-owned content.
3. Check whether external text can alter task scope or trigger an unintended permitted-tool request.

## Evidence required

A trace from untrusted content to an observed boundary failure.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger web LLM attacks](https://portswigger.net/web-security/llm-attacks)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

