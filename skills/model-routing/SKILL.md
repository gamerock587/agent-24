---
name: model-routing
description: "Route generation and decision tasks to the installed model pair."
---

# Qwen and d1 model routing

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Local model HTTP APIs.

## Workflow

1. Use Qwen for plans, code drafts and explanations; use d1 for choices among enumerated actions.
2. Validate structured output before execution and reject invented action IDs.
3. Benchmark tool calls, structured responses and long-context behavior on pinned model settings.

## Evidence required

Model IDs, settings, parse results and measured task outcomes.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Qwen3.5 9B model card](https://huggingface.co/Qwen/Qwen3.5-9B)
- [Liquid d1 model card](https://huggingface.co/LiquidAI/d1-3B)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

