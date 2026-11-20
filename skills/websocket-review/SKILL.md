---
name: websocket-review
description: "Assess identity, origin and authorization in WebSocket workflows."
---

# WebSocket connection and message controls

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: WebSocket client, browser.

## Workflow

1. Record connection handshake and session lifecycle.
2. Compare messages under two controlled identities.
3. Verify per-message resource permissions and behavior after logout or expiry.

## Evidence required

Handshake and message transcript with controlled unauthorized outcome.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [PortSwigger WebSockets](https://portswigger.net/web-security/websockets)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

