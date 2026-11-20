---
name: dependency-advisories
description: "Match dependency inventories with advisories and supply-chain evidence."
---

# Dependency vulnerability matching

Status: authored integration draft; format-checked, not yet tested with Qwen/d1.

Read [the execution contract](../../EXECUTION_CONTRACT.md) before performing tool actions. This file defines a workflow; it does not grant target access or install its listed tools.

## Inputs

The supplied task, relevant artifacts, exact target scope and current evidence. Check prerequisites: OSV client, dependency inventory.

## Workflow

1. Build an inventory from lockfiles and image manifests.
2. Match exact ecosystem, package and version before considering an advisory applicable.
3. Check reachability and vendor fixes; never equate a package-name match with exploitability.

## Evidence required

Lockfile evidence, advisory URL, affected-range match and reachability status.

Return observations, attempted actions, verification status, evidence IDs, remaining uncertainty and a proposed next action. If a prerequisite fails, return a blocked task result with the concrete reason. Do not report an inferred outcome as observed.

## References

- [OSV documentation](https://google.github.io/osv.dev/)
- [OpenSSF Scorecard](https://github.com/ossf/scorecard)

References checked on 2026-10-12; retrieval status is recorded in [sources.json](../../research/sources.json). The operational instructions above are original Agent 24 drafts, not copied upstream skill text.

