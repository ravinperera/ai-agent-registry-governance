# AI Agent Registry Governance

Policy-as-code starter for cataloguing, approving and validating AI agents, skills, MCP servers and other agentic resources.

## Purpose

This project will provide a practical governance layer for organisations that need to decide which agentic resources may be discovered, installed or used. The initial focus is a reviewable registry format, validation rules and CI checks rather than a hosted marketplace.

## Initial governance scope

Each registered resource should declare and validate:

- accountable owner and security contact;
- publisher, source repository and pinned version or commit;
- requested filesystem, shell, network and secrets access;
- allowed network destinations and data classifications;
- risk tier and required human approval;
- approval status, evidence and approving team;
- review expiry, maintenance status and retirement path.

## Non-goals

This project will not install or execute agents, host credentials or secrets, or treat registry approval as a replacement for security review, runtime controls, monitoring or human oversight.

## Status

Early-stage public reference project. Schemas, example registry entries, policy checks and validation workflows will be added incrementally.
