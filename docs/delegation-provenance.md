# Delegation, human oversight and provenance

Agentic systems create a governance problem that ordinary resource approval does not fully address. Once an approved agent can call tools, create subagents or delegate work, authority may travel through several components before the final action is executed.

This project models that problem in three separate layers: delegation policy, human oversight and provenance.

## 1. Delegation policy

`delegation` answers:

- may this resource delegate authority at all?
- how many agent-to-agent hops are allowed?
- which delegates are permitted?
- must delegated authority be narrower than the parent's authority?

Example:

```json
{
  "delegation": {
    "allowed": true,
    "maxHops": 2,
    "scopeNarrowingRequired": true,
    "allowedDelegates": [
      "terraform-review-agent",
      "security-analysis-agent"
    ]
  }
}
```

The baseline policy requires `scopeNarrowingRequired: true` whenever delegation is enabled. A child agent should never gain filesystem, network, secrets, data or action authority that was unavailable to the parent.

Any resource that can delegate is at least medium risk. If it also has write, shell, secrets or other consequential authority, normal high/critical controls still apply.

## 2. Human oversight

Resource approval and runtime action approval are different decisions.

A security team may approve an operations agent for enterprise use while still requiring a human to approve every production write or IAM change. `humanOversight` describes that runtime approval boundary.

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

Supported modes are:

- `none` — no runtime human approval is required by this record;
- `session` — a human establishes authority for a bounded session;
- `per-consequential-action` — named consequential action classes require human approval;
- `always` — every action requires human approval.

The baseline requires `per-consequential-action` or `always` for high/critical or otherwise elevated authority.

For those risk levels, delegated approval is disabled by the baseline. The purpose is to prevent a human approval granted to one agent from silently becoming blanket approval for another agent or for a broader action.

## 3. Provenance

`provenance` describes the evidence that must accompany or survive an action.

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

When authority is delegated, the baseline requires evidence that:

- identifies the originating human;
- records the delegation chain;
- is tamper-evident;
- is retained in addition to runtime audit logs.

For consequential authority without delegation, the baseline still requires provenance that identifies the human approval and is tamper-evident.

## Protocol-neutral by design

The registry does not implement a delegation or provenance protocol. `provenance.mechanism` is descriptive so organisations can map the governance requirement to their architecture.

Possible mechanisms include:

- signed approval records;
- signed delegation chains;
- platform-native attestation or audit evidence;
- a reviewed cryptographic human-to-agent delegation protocol;
- another organisation-specific mechanism.

A mechanism such as Human Delegation Provenance (HDP) can be evaluated as one possible implementation of these controls, but the schema does not make HDP mandatory and does not treat any named protocol as proof of safety.

## Provenance is not authorisation

This distinction is important:

```text
Governance registry
    defines what should be allowed
            |
            v
IAM / OAuth / policy engine / tool wrapper
    enforces what is actually allowed
            |
            v
Provenance mechanism
    records or proves where authority came from
            |
            v
Audit / monitoring
    detects, investigates and retains evidence
```

A valid provenance chain should not make an otherwise unauthorised action executable. The runtime must still compare the requested action with the effective authority granted to the identity or agent.

## Example: production deployment

Assume a human asks Agent A to deploy version `v2.4.1` to production and Agent A delegates verification to Agent B.

A sound governance design should be able to answer:

1. Was Agent A approved for this use?
2. Was the human allowed to authorise the production deployment?
3. Did the approval cover this environment and action class?
4. Was Agent A allowed to delegate?
5. Was Agent B an allowed delegate?
6. Did Agent B receive no more authority than Agent A had?
7. Was the maximum delegation depth respected?
8. Can the final execution be linked to the originating human approval?
9. Would alteration of the approval or delegation evidence be detectable?
10. Could IAM or the execution wrapper still block an action outside the approved scope?

The registry captures the policy requirements. Runtime systems must implement and enforce them.

## Threats these controls reduce

These controls are intended to reduce risks such as:

- agent-created subagents receiving excessive authority;
- prompt injection causing an agent to expand delegated permissions;
- blanket human approval being reused for unrelated actions;
- losing the identity of the originating human after several agent hops;
- audit logs showing only the final service identity rather than the authority chain;
- an agent claiming that a human approved an action when no verifiable approval exists;
- inability to revoke or investigate delegated actions after an incident.

They do not remove the need for least privilege, isolation, authentication, authorisation, monitoring, secure software supply chains or human risk review.
