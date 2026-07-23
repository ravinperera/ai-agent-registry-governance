# Agentic resource risk tiers

Risk tier should reflect both the resource's intended capability and the maximum authority available at runtime. Use the highest applicable tier.

## Low

Typical characteristics:

- instructions, prompts or skills with no executable tool authority;
- read-only access to public or approved internal content;
- no shell, write, secrets or network access;
- no autonomous decisions affecting people, money, access or production;
- simple removal and rollback.

Minimum controls:

- accountable owner;
- immutable source reference;
- basic source and content review;
- approval evidence and review date;
- audit trail showing which version was approved.

## Medium

Typical characteristics:

- read-only tools or MCP servers;
- restricted network access to named services;
- internal or confidential data processing;
- access to metadata about secrets or identities without secret values;
- recommendations that could influence engineering or operational decisions;
- no direct production changes.

Minimum controls:

- low-tier controls;
- threat model;
- explicit destination allowlist;
- data-retention and logging review;
- isolated testing with negative permission cases;
- monitoring and audit logging where the resource is invoked;
- named human approval.

## High

Typical characteristics:

- filesystem write access;
- shell execution;
- secrets read access;
- production or shared-environment access;
- deployment, IAM, DNS, database, networking or security-control changes;
- processing restricted data;
- autonomous actions with material operational impact.

Minimum controls:

- medium-tier controls;
- at least two independent approving groups;
- sandboxing and least-privilege identities;
- mandatory monitoring and audit logging;
- explicit human approval before consequential actions;
- tested rollback, revocation and incident-response procedures;
- short approval lifetime and event-driven reassessment.

## Critical

Typical characteristics:

- unrestricted or cross-environment administrative authority;
- broad secrets or credential access;
- ability to change identity, security, payment or safety-critical controls;
- autonomous destructive actions;
- access that cannot be reliably isolated, monitored or revoked;
- high-impact decisions affecting regulated, financial, employment, healthcare or safety contexts.

Default decision:

- **Do not approve** until authority is reduced and enforceable controls exist.

Where use remains necessary, require senior security and business-risk acceptance, independent testing, dedicated isolation, continuous monitoring, strict action approval and a time-limited exception.

## Automatic escalation rules in this repository

The example validator escalates records containing any of the following to at least `high`:

- `filesystem: write`;
- `shell: execute`;
- `secrets: read`;
- `network.egress: unrestricted`.

For elevated authority it also requires:

- `humanApprovalRequired: true`;
- sandboxing;
- monitoring;
- audit logging.

The baseline policy refuses to approve unrestricted network egress. Organisations may adopt stricter rules.