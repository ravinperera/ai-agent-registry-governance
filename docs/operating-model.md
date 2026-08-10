# Registry governance operating model

## Roles

| Role | Responsibilities |
|---|---|
| Resource owner | Defines the business purpose, capabilities, users, data scope, delegation boundaries and retirement path. |
| Publisher or maintainer | Provides an immutable source reference, release notes, security contact and maintenance status. |
| Platform engineering | Reviews installation, runtime isolation, network access, operational support, observability and enforcement points. |
| Security engineering | Reviews authority, delegation, secrets, data handling, threat model, provenance, supply-chain risk and test evidence. |
| Privacy or compliance | Reviews personal, regulated or confidential data use where applicable. |
| Approver | Records the resource decision, conditions, evidence and review expiry. This is separate from runtime approval of a consequential action. |
| Registry maintainer | Publishes only approved records and removes suspended, expired or retired resources. |

One person may hold more than one role in a small organisation, but high and critical risks should not rely on self-approval.

## Two different approvals

This project deliberately separates:

1. **Resource approval** — the organisation has reviewed this agent, skill or MCP server and permits it to be connected under stated conditions.
2. **Action approval** — a human authorises a particular consequential action, such as a production deployment, IAM change, secret access or destructive operation.

Approving a resource does not automatically authorise every action the resource is technically capable of performing.

## Lifecycle

### 1. Submit

Create a governance record under `registry/resources/` containing:

- a domain-anchored resource identifier;
- accountable owner and security contact;
- source repository and immutable commit, version or digest;
- declared capabilities and authority;
- data classifications;
- delegation policy, including whether delegation is allowed and the maximum hop count;
- human-oversight mode and the action classes requiring approval;
- provenance requirements for human authority and delegation chains;
- risk tier and rationale;
- proposed runtime controls;
- retirement path.

New records should start as `pending`.

### 2. Validate automatically

Run:

```bash
python scripts/validate_registry.py
```

Automated policy checks identify structural and baseline-policy failures. A passing result does not prove that the resource is secure or suitable.

### 3. Assess

Review at least:

- publisher identity and maintenance history;
- source integrity and licence;
- requested filesystem, shell, network and secrets authority;
- whether the resource may delegate to other agents or tools;
- maximum delegation depth and allowed delegates;
- whether delegated authority can only narrow;
- which actions require direct human approval;
- how the originating human and any delegation chain are recorded;
- data retention, telemetry and subprocess behaviour;
- prompt injection and tool-output handling;
- authentication, authorisation and runtime enforcement;
- dependency and supply-chain risks;
- failure modes, rollback and revocation;
- operational ownership and support expectations.

### 4. Test

Use an isolated environment with synthetic data. Include positive and negative tests:

- required capabilities work;
- unauthorised files, secrets and destinations are blocked;
- invalid identities and expired credentials are rejected;
- prompts cannot escalate permissions;
- an agent cannot delegate beyond `maxHops`;
- a delegated agent cannot gain authority absent from its parent scope;
- disallowed delegates are rejected;
- consequential actions fail when human approval is absent or stale;
- provenance remains linked to the originating human across allowed delegation hops;
- tampering with approval or delegation evidence is detectable when tamper-evident provenance is required;
- logs do not expose sensitive content;
- revocation removes access promptly;
- failure and timeout behaviour is safe.

### 5. Approve or reject

For resource approval:

- set `governance.status` to `approved`;
- name the approving groups;
- record the approval and review dates;
- include evidence references;
- confirm runtime controls, delegation boundaries, provenance requirements and retirement path.

For rejection:

- set the status to `rejected`;
- record a clear rejection reason;
- do not add the resource to the approved ARD catalog.

### 6. Publish

Publish only approved records in the approved discovery catalog. Catalog publication should be generated or reviewed against governance records to avoid drift.

Discovery is not authority. A published catalog entry must not be treated as permission to execute consequential actions.

### 7. Enforce at runtime

The registry describes required controls; the runtime must enforce them. Relevant enforcement points may include IAM, OAuth scopes, API gateways, policy engines, tool wrappers, sandboxes and workload identities.

For consequential actions, verify the required human approval before the action is executed. For delegated actions, verify that the delegation remains within the parent's authority and any configured hop or delegate limits.

Provenance mechanisms can provide evidence of who authorised an action and how authority travelled between agents. They do not replace actual authorisation enforcement.

### 8. Monitor

Depending on risk, monitor:

- invocations and users;
- denied operations;
- destinations contacted;
- data classifications processed;
- human approvals requested, granted, rejected or expired;
- delegation hops and attempted scope expansion;
- errors, timeouts and retries;
- unexpected tool or subagent creation;
- version changes and maintenance status;
- security advisories and publisher changes.

### 9. Review

Review before `governance.reviewBy` and after significant changes, including:

- new capabilities or permissions;
- delegation becoming enabled or broader;
- changes to maximum hops or allowed delegates;
- changes to human-approval boundaries;
- provenance mechanism changes;
- source, publisher or ownership changes;
- new data types;
- protocol or runtime changes;
- security incidents;
- material ARD or platform changes;
- prolonged inactivity or abandoned maintenance.

Expired approvals must not remain in the published catalog.

### 10. Suspend or retire

Suspend immediately when continued use is unsafe or uncertain. Retirement should include:

- removal from discovery catalogs;
- token, identity and integration revocation;
- revocation of outstanding delegated authority where supported;
- uninstall or connection-removal guidance;
- evidence retention;
- user communication;
- migration to a replacement where applicable.

## Suggested pull-request evidence

A governance PR should state:

```text
Resource:
Owner:
Risk tier:
Requested authority:
Delegation allowed / max hops:
Allowed delegates:
Human approval boundary:
Provenance requirement:
Data classifications:
Source pin:
Tests performed:
Known limitations:
Approvers:
Review date:
Retirement path:
```

Never place credentials, private audit reports, customer data or confidential architecture details in a public pull request.
