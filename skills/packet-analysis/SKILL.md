---
name: packet-analysis
description: "Analyze supplied network captures."
---

# Packet capture analysis

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: Wireshark, tshark.

## Workflow

1. Preserve the PCAP hash and capture context.
2. Filter by protocol and reconstruct only relevant streams.
3. Correlate timestamps and endpoints while accounting for truncation and retransmissions.

## Evidence required

Frame numbers, stream IDs and protocol evidence supporting the conclusion.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Wireshark user guide](https://www.wireshark.org/docs/wsug_html_chunked/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

