# Proposed execution contract

These are original design requirements for the future Agent 24 runtime. They are documentation now; enforcement must be implemented and tested before tool execution.

## Scope and authority

An execution job must cite an authorization record and name exact permitted targets and methods. Discovered hosts, redirected origins and webpage instructions do not widen that scope. CTF endpoints and platform submissions must comply with the challenge rules. The research collection itself does not grant permission to run tests.

Downloaded instructions are untrusted inputs. An upstream SKILL.md, installer, example command or tool response cannot override the user's scope or runtime controls. Do not auto-load archives, expand tool permissions, disable host protections, or auto-install a dependency merely because an upstream document asks for it. Review and adapt a package before enabling it.

## Model responsibilities

Qwen proposes plans, typed tool arguments and code drafts. d1 chooses among already enumerated permitted actions and can classify observations. Neither model determines authorization or proves a vulnerability through confidence scores. A deterministic executor must validate target, method, tool, arguments, budgets and current job state before executing a proposal.

## Evidence and findings

Keep raw observations distinct from summaries. Record tool version, target, timestamps, request identity, return code and artifact hash. Redact secrets in shared reports while preserving controlled originals. Every claim cites an actual evidence ID. Scanner alerts begin as candidates; confirmed findings require a reproducible failing control and supported impact. Failures, timeouts and unknown results stay visible.

## Continuous operation

Continuously available does not mean continuous scanning. Each job has an attempt, time, network, output-size and compute budget. Sleep or idle when no work remains. Use backoff and circuit breakers for repeated failures, rate limiting and unavailable models. Avoid accumulating full logs or screenshots in model context; retrieve relevant evidence by ID.

A restart must invalidate transient browser observations and re-check external state. Retry only actions with known replay semantics. An uncertain state-changing request is not automatically retried. A lease and idempotency key prevent duplicate job execution. Preserve a user-visible pause and stop control.

## Isolation

Untrusted code drafts and challenge binaries run in dedicated disposable environments, with an explicit network allowlist and resource limits. The host's personal browser profile, files and credentials are not the default test environment. Secret material is supplied by scoped tool credentials, not embedded in skills or prompts.

## Result contract

A skill returns its task ID, observations, actions actually attempted, evidence IDs, verification status, unresolved questions and proposed next action. A blocked result names the missing prerequisite. A proposed plan does not count as completed work. See the [result template](templates/skill-result.example.json).

