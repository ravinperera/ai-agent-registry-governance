# Registry governance operating model

## Roles

| Role | Responsibilities |
|---|---|
| Resource owner | Defines the business purpose, capabilities, users, data scope and retirement path. |
| Publisher or maintainer | Provides an immutable source reference, release notes, security contact and maintenance status. |
| Platform engineering | Reviews installation, runtime isolation, network access, operational support and observability. |
| Security engineering | Reviews authority, secrets, data handling, threat model, supply-chain risk and test evidence. |
| Privacy or compliance | Reviews personal, regulated or confidential data use where applicable. |
| Approver | Records the decision, conditions, evidence and review expiry. |
| Registry maintainer | Publishes only approved records and removes suspended, expired or retired resources. |

One person may hold more than one role in a small organisation, but high and critical risks should not rely on self-approval.

## Lifecycle

### 1. Submit

Create a governance record under `registry/resources/` containing:

- a domain-anchored resource identifier;
- accountable owner and security contact;
- source repository and immutable commit, version or digest;
- declared capabilities and authority;
- data classifications;
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
- data retention, telemetry and subprocess behaviour;
- prompt injection and tool-output handling;
- authentication and authorisation;
- dependency and supply-chain risks;
- failure modes, rollback and revocation;
- operational ownership and support expectations.

### 4. Test

Use an isolated environment with synthetic data. Include positive and negative tests:

- required capabilities work;
- unauthorised files, secrets and destinations are blocked;
- invalid identities and expired credentials are rejected;
- prompts cannot escalate permissions;
- logs do not expose sensitive content;
- revocation removes access promptly;
- failure and timeout behaviour is safe.

### 5. Approve or reject

For approval:

- set `governance.status` to `approved`;
- name the approving groups;
- record the approval and review dates;
- include evidence references;
- confirm runtime controls and retirement path.

For rejection:

- set the status to `rejected`;
- record a clear rejection reason;
- do not add the resource to the approved ARD catalog.

### 6. Publish

Publish only approved records in the approved discovery catalog. Catalog publication should be generated or reviewed against governance records to avoid drift.

### 7. Monitor

Depending on risk, monitor:

- invocations and users;
- denied operations;
- destinations contacted;
- data classifications processed;
- errors, timeouts and retries;
- unexpected tool or subagent creation;
- version changes and maintenance status;
- security advisories and publisher changes.

### 8. Review

Review before `governance.reviewBy` and after significant changes, including:

- new capabilities or permissions;
- source, publisher or ownership changes;
- new data types;
- protocol or runtime changes;
- security incidents;
- material ARD or platform changes;
- prolonged inactivity or abandoned maintenance.

Expired approvals must not remain in the published catalog.

### 9. Suspend or retire

Suspend immediately when continued use is unsafe or uncertain. Retirement should include:

- removal from discovery catalogs;
- token, identity and integration revocation;
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
Data classifications:
Source pin:
Tests performed:
Known limitations:
Approvers:
Review date:
Retirement path:
```

Never place credentials, private audit reports, customer data or confidential architecture details in a public pull request.