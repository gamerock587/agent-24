---
name: ctf-triage
description: "Classify a CTF challenge and route it to a specialist workflow."
---

# CTF challenge triage

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: file, strings, local Python.

## Workflow

1. Preserve the challenge text and hash attachments before analysis.
2. Identify artifact type, architecture or protocol; distinguish supplied clues from guesses.
3. Choose one falsifiable hypothesis and the matching skill; record attempts and avoid reading an answer key during evaluation.

## Evidence required

Challenge ID, artifact hashes, category, hypothesis and verified submission result.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [picoCTF getting started](https://picoctf.org/get_started.html)
- [pwn.college](https://pwn.college/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

