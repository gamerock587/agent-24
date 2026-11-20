---
name: tls-review
description: "Review transport security for approved service endpoints."
---

# TLS and certificate review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: TLS client, Burp.

## Workflow

1. Record the certificate chain, hostname validation and negotiated protocol.
2. Compare results across the actual ingress endpoints and client settings.
3. Distinguish transport configuration weaknesses from application authorization flaws.

## Evidence required

Endpoint, client configuration, certificate evidence and reproducible negotiation results.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Burp Suite documentation](https://portswigger.net/burp/documentation)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

