---
name: scope-and-rules
description: "Define an executable scope for an authorized assessment before any testing."
---

# Assessment scope and rules

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Policy validator.

## Workflow

1. Translate the supplied target list into exact origins, CIDRs, repositories, accounts and exclusions.
2. Record permitted methods, request rate, concurrency, time window, test identities and stop conditions.
3. Reject a job whose target or action cannot be matched to these rules; do not infer scope from a redirect or discovered hostname.

## Evidence required

A scope record with an authorization reference, expiry and explicit action limits.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

