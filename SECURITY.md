# Security policy

## Reporting a vulnerability

Please do not disclose a security vulnerability through a public issue.

Report concerns privately to the repository owner through GitHub's private vulnerability reporting feature when enabled, or through the contact method listed on the maintainer's GitHub profile.

Include:

- the affected file or policy;
- the expected and actual behaviour;
- a minimal reproduction using fictional data;
- the potential impact;
- suggested mitigations where known.

Do not include real credentials, tokens, customer data, internal hostnames or private audit evidence.

## Security scope

Security-relevant areas include:

- validator bypasses;
- records incorrectly passing despite mutable source references;
- approval-expiry failures;
- catalog publication of non-approved resources;
- schema conditions that permit undeclared authority;
- unsafe GitHub Actions permissions or credential use;
- examples that could encourage secrets exposure or unrestricted execution;
- dependency or supply-chain risks introduced by this repository.

## Important limitation

This repository is a policy-as-code reference implementation. Passing validation does not prove that an agent, skill, MCP server or other resource is secure. The validator does not execute resources, inspect all source code, verify cryptographic identity, assess runtime isolation or replace a formal security review.
