---
name: oauth-review
description: "Assess delegated identity flows using a test identity provider."
---

# OAuth and delegated identity

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Test IdP, browser.

## Workflow

1. Map client, provider, redirect endpoints and account-linking steps.
2. Verify state, redirect matching and intended identity bindings.
3. Compare controlled account flows and confirm the final application identity.

## Evidence required

Redacted protocol trace and demonstrated identity or redirect-binding error.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger OAuth](https://portswigger.net/web-security/oauth)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

