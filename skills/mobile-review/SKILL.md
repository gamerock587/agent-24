---
name: mobile-review
description: "Review a test-owned mobile application against mobile security controls."
---

# Mobile application review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Emulator, mobile test tooling.

## Workflow

1. Record app build, OS, test identity and permitted instrumentation.
2. Map local storage, platform interfaces, networking and authentication.
3. Apply relevant MASTG tests and separate device configuration from application behavior.

## Evidence required

MASVS control mapping, build-specific evidence and reproducible test results.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [OWASP MASTG](https://mas.owasp.org/MASTG/)
- [OWASP MASVS](https://mas.owasp.org/MASVS/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

