---
name: kubernetes-review
description: "Assess a supplied cluster configuration and authorized read-only observations."
---

# Kubernetes configuration review

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: kubectl read-only, manifest parser.

## Workflow

1. Inventory workloads, RBAC, admission settings and network boundaries.
2. Review service-account permissions and pod isolation against expected requirements.
3. Avoid live mutation; reproduce uncertain behavior in an isolated cluster.

## Evidence required

Manifest paths, effective permissions and cluster-specific control results.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [Kubernetes security checklist](https://kubernetes.io/docs/concepts/security/security-checklist/)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

