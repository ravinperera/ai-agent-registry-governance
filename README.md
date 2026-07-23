# AI Agent Registry Governance

Policy-as-code starter for cataloguing, approving and validating AI agents, skills, MCP servers and other agentic resources.

> Discover broadly. Approve deliberately. Connect with least privilege.

## Why this exists

Agentic Resource Discovery (ARD) gives AI clients a standard discovery layer for finding agents, MCP servers, skills, APIs and workflows. Discovery alone does not answer an organisation's governance questions: who owns the resource, which source version was reviewed, what permissions it needs, whether network or secrets access is allowed, when approval expires, and how the resource is retired.

This project keeps those concerns separate:

- **Discovery layer:** an ARD-aligned `ai-catalog.json` advertises approved capabilities.
- **Governance layer:** separate records capture ownership, source pinning, requested access, risk, approval evidence and review expiry.
- **Policy layer:** a validator rejects records that do not meet the baseline controls.

ARD remains responsible for discovery. This project does not redefine ARD and does not execute the resources it governs.

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
- risk-tier and human-approval requirements;
- the sample ARD catalog when an official schema is supplied.

The GitHub Actions workflow downloads the ARD v0.9 JSON Schema from a pinned upstream commit and performs both governance and catalog validation without cloud credentials.

## Repository structure

```text
.
├── catalog/
│   └── ai-catalog.json
├── registry/resources/
│   ├── approved-terraform-review-skill.json
│   └── pending-ci-triage-mcp.json
├── examples/rejected/
│   └── unrestricted-shell-agent.json
├── schemas/
│   └── governance-resource.schema.json
├── scripts/
│   └── validate_registry.py
├── docs/
│   ├── ard-alignment.md
│   ├── operating-model.md
│   └── risk-tiers.md
├── .github/workflows/
│   └── validate.yml
├── CONTRIBUTING.md
├── SECURITY.md
└── requirements-dev.txt
```

## Example governance decision

An approved, read-only Terraform review skill should have:

- an accountable platform-engineering owner;
- an immutable commit SHA or digest;
- no shell, secrets or unrestricted network access;
- a documented risk tier and rationale;
- named approvers and evidence;
- a future review date;
- sandboxing, monitoring and audit requirements appropriate to its risk.

A resource using an unpinned branch, unrestricted egress, shell execution and secrets access will be rejected by the example policy unless the record is corrected and the required high-risk approvals are supplied.

## Operating principles

1. **Discovery is not approval.** A resource may be discoverable without being authorised for enterprise use.
2. **Pin what was reviewed.** Branch names such as `main` and tags such as `latest` are not approval evidence.
3. **Declare authority before connection.** Filesystem, shell, network, secrets and data access must be explicit.
4. **Approvals expire.** Every approved record needs a review date and retirement path.
5. **Higher authority requires stronger evidence.** Shell execution, write access, secrets access and unrestricted egress raise the risk tier.
6. **Runtime controls still matter.** Registry approval does not replace sandboxing, authentication, authorisation, monitoring or human oversight.

## ARD alignment

The sample catalog follows the current ARD v0.9 draft structure: `specVersion`, host metadata, domain-anchored `urn:air:` identifiers, media types, representative queries, and exactly one of `url` or `data` per entry.

See [ARD alignment](docs/ard-alignment.md) for the standards boundary, upstream version pin and known limitations.

## Non-goals

This project will not:

- install, connect to or execute agents or MCP servers;
- host credentials, API tokens or private trust evidence;
- replace vendor due diligence, security testing or legal review;
- treat a catalog entry as proof that a resource is safe;
- claim compatibility with future ARD drafts without revalidation.

## Status

Early-stage public reference implementation. All organisations should adapt the schema, thresholds and approval model to their own risk profile.

## License

MIT