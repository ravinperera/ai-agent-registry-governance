# AI Agent Registry Governance

Policy-as-code starter for cataloguing, approving and validating AI agents, skills, MCP servers and other agentic resources.

> Discover broadly. Approve deliberately. Delegate narrowly. Prove human authority.

## Why this exists

Agentic Resource Discovery (ARD) gives AI clients a standard discovery layer for finding agents, MCP servers, skills, APIs and workflows. Discovery alone does not answer an organisation's governance questions: who owns the resource, which source version was reviewed, what permissions it needs, whether network or secrets access is allowed, when approval expires, whether it may delegate authority, which actions need direct human approval, and how the resulting authority chain is audited.

This project keeps those concerns separate:

- **Discovery layer:** an ARD-aligned `ai-catalog.json` advertises approved capabilities.
- **Governance layer:** separate records capture ownership, source pinning, requested access, delegation boundaries, human-oversight requirements, provenance, risk, approval evidence and review expiry.
- **Policy layer:** a validator rejects records that do not meet the baseline controls.
- **Runtime layer:** IAM, OAuth scopes, policy engines, tool wrappers and other controls remain responsible for enforcing actual authority.

ARD remains responsible for discovery. This project does not redefine ARD and does not execute the resources it governs.

## The governance problem

There are two different questions that should not be confused:

1. **Is this agent approved for enterprise use?**
2. **Did a human authorise this particular consequential action?**

An organisation may approve an operations agent without authorising every production, IAM, database or destructive action that the agent could technically perform.

Agent-to-agent delegation introduces another question: if Agent A gives work to Agent B, can the organisation prove where that authority originated and ensure Agent B did not receive broader authority than Agent A had?

Schema version `1.1` adds explicit controls for these boundaries.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python scripts/validate_registry.py
```

The validation command checks:

- governance records against the local JSON Schema;
- source pinning and mutable-reference risks;
- accountable ownership and security contacts;
- approval evidence and review expiry;
- shell, secrets and network-egress controls;
- risk-tier requirements;
- delegation hop limits, explicit delegate allowlists and mandatory scope narrowing;
- provenance requirements for delegated authority;
- action-level human oversight for consequential authority;
- sandboxing, monitoring and audit requirements;
- the sample ARD catalog when an official schema is supplied.

The GitHub Actions workflow downloads the ARD v0.9 JSON Schema from a pinned upstream commit and performs both governance and catalog validation without cloud credentials.

## Repository structure

```text
.
├── catalog/
│   └── ai-catalog.json
├── registry/resources/
│   ├── approved-terraform-review-skill.json
│   ├── pending-ci-triage-mcp.json
│   └── pending-production-deployment-agent.json
├── examples/rejected/
│   └── unrestricted-shell-agent.json
├── schemas/
│   └── governance-resource.schema.json
├── scripts/
│   └── validate_registry.py
├── tests/
│   ├── test_schema_delegation.py
│   └── test_validate_registry.py
├── docs/
│   ├── ard-alignment.md
│   ├── delegation-provenance.md
│   ├── operating-model.md
│   └── risk-tiers.md
├── .github/workflows/
│   └── validate.yml
├── CONTRIBUTING.md
├── SECURITY.md
└── requirements-dev.txt
```

## Governance record model

A record now covers four different control surfaces.

### 1. Resource authority

`permissions` declares the maximum technical authority requested by the resource: filesystem, shell, network, secrets and data classifications.

### 2. Delegation

`delegation` describes whether the resource may pass authority to another agent or subagent.

```json
{
  "delegation": {
    "allowed": true,
    "maxHops": 2,
    "scopeNarrowingRequired": true,
    "allowedDelegates": ["terraform-review-agent", "security-analysis-agent"]
  }
}
```

The baseline requires delegated authority to narrow rather than expand, requires an explicit delegate allowlist, and treats any delegation capability as at least medium risk.

### 3. Human oversight

`humanOversight` separates resource approval from runtime action approval.

```json
{
  "humanOversight": {
    "mode": "per-consequential-action",
    "approvalRequiredFor": [
      "production-write",
      "deployment",
      "iam-change",
      "secret-access",
      "destructive-action"
    ],
    "delegatedApprovalAllowed": false,
    "approvalProvenanceRequired": true
  }
}
```

For high or critical authority, the baseline requires action-level approval rather than a one-time blanket approval.

### 4. Provenance

`provenance` states what evidence must survive execution and delegation.

```json
{
  "provenance": {
    "required": true,
    "mechanism": "signed-delegation-chain",
    "tamperEvident": true,
    "recordsOriginatingHuman": true,
    "recordsDelegationChain": true
  }
}
```

The project is intentionally protocol-neutral. A deployment could satisfy these requirements using a reviewed cryptographic delegation protocol, signed approval records, platform-native evidence or another mechanism that meets the organisation's controls.

Provenance proves or records authority history; it does **not** replace runtime authorisation enforcement.

See [Delegation, human oversight and provenance](docs/delegation-provenance.md).

## Examples

The approved Terraform review skill demonstrates a low-risk resource with no delegation authority.

The pending CI triage MCP server demonstrates medium-risk read-only access to internal and confidential CI data.

The pending production deployment agent demonstrates the new high-risk model: bounded agent-to-agent delegation, explicit approved delegates, per-consequential-action human approval and tamper-evident provenance linked to the originating human.

The rejected unrestricted shell agent deliberately violates source, authority, delegation, provenance, oversight and runtime controls to prove that unsafe records fail validation.

## Example governance decision

An approved, read-only Terraform review skill should have:

- an accountable platform-engineering owner;
- an immutable commit SHA or digest;
- no shell, secrets or unrestricted network access;
- no authority delegation unless it is actually required;
- a documented risk tier and rationale;
- named approvers and evidence;
- a future review date;
- sandboxing, monitoring and audit requirements appropriate to its risk.

A resource using an unpinned branch, unrestricted egress, shell execution, secrets access, broad delegation and untraceable human authority will be rejected by the example policy unless the record is corrected and the required controls are supplied.

## Operating principles

1. **Discovery is not approval.** A resource may be discoverable without being authorised for enterprise use.
2. **Resource approval is not action approval.** Approving an agent does not authorise every consequential action it can technically perform.
3. **Pin what was reviewed.** Branch names such as `main` and tags such as `latest` are not approval evidence.
4. **Declare authority before connection.** Filesystem, shell, network, secrets and data access must be explicit.
5. **Delegate narrowly.** Delegated authority must not exceed the authority that was received, and delegates must be explicitly permitted.
6. **Keep the human in the authority chain.** High-impact actions require traceable human approval under the baseline policy.
7. **Approvals expire.** Every approved record needs a review date and retirement path.
8. **Higher authority requires stronger evidence.** Shell execution, write access, secrets access, unrestricted egress and delegation increase governance requirements.
9. **Provenance is evidence, not enforcement.** IAM and runtime policy controls must still block unauthorised actions.
10. **Runtime controls still matter.** Registry approval does not replace sandboxing, authentication, authorisation, monitoring or human oversight.

## ARD alignment

The sample catalog follows the current ARD v0.9 draft structure used by this repository: `specVersion`, host metadata, domain-anchored `urn:air:` identifiers, media types, representative queries, and exactly one of `url` or `data` per entry.

See [ARD alignment](docs/ard-alignment.md) for the standards boundary, upstream version pin and known limitations.

## Non-goals

This project will not:

- install, connect to or execute agents or MCP servers;
- implement an agent-to-agent delegation protocol;
- replace IAM, OAuth, capability enforcement or application authorisation;
- host credentials, API tokens or private trust evidence;
- replace vendor due diligence, security testing or legal review;
- treat a catalog entry as proof that a resource is safe;
- claim compatibility with future ARD drafts without revalidation.

## Status

Early-stage public reference implementation. All organisations should adapt the schema, thresholds, approval boundaries and provenance model to their own risk profile.

## License

MIT
