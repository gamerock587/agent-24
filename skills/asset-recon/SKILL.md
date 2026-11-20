---
name: asset-recon
description: "Map approved assets and observed entry points without expanding target scope."
---

# Asset and attack surface mapping

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Browser, HTTP client.

## Workflow

1. Build an inventory from user-supplied hosts and application documentation.
2. Record observed endpoints, parameters, identities and technologies with their evidence.
3. Separate first-party assets from third-party dependencies and prioritize reachable trust boundaries.

## Evidence required

An asset inventory that distinguishes observed, inferred and excluded entries.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [OWASP WSTG v4.2](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

