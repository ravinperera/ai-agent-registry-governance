# Governance documentation

Use this directory as the entry point for the repository's operating guidance. The JSON Schema and validators define the machine-checked baseline; these documents explain how to apply that baseline through review, approval, publication, monitoring and retirement.

## Guide map

| Guide | Start here when you need to answer |
|---|---|
| [Operating model](operating-model.md) | Who owns each decision, what evidence is reviewed, and how a resource moves from submission to retirement? |
| [Risk tiers](risk-tiers.md) | How should authority, data access and operational impact affect the resource's risk tier and controls? |
| [Delegation and provenance](delegation-provenance.md) | How should delegated authority be narrowed, approved and traced back to the originating human? |
| [ARD alignment](ard-alignment.md) | Which concerns belong to discovery/catalog metadata and which belong to this governance layer? |

For the public entry point, examples and validation commands, return to the [repository README](../README.md).

## Lifecycle states

The schema supports five governance states. Treat the status as a decision about whether the resource may be published and used under the recorded conditions, not as a substitute for runtime authorisation.

| Status | Meaning | Catalog consequence |
|---|---|---|
| `pending` | Assessment or evidence collection is incomplete. | Do not publish. |
| `approved` | Required review is complete and the approval remains within its review window. | May be published when the catalog entry matches the approved governance record. |
| `rejected` | The proposed resource or authority was not accepted. | Do not publish; retain the rejection rationale as governance evidence. |
| `suspended` | Previously acceptable use is temporarily unsafe or uncertain. | Remove from discovery until reassessment supports a new approval decision. |
| `retired` | The resource is no longer approved for ongoing use. | Remove from discovery and follow the recorded retirement path. |

Only `approved` records belong in the approved catalog. Discovery must never be treated as permission for a consequential runtime action.

## Recommended transitions

The following transitions are conservative operational guidance. They are **not all enforced by the current JSON Schema**; organisations may add stricter policy checks for their own workflow.

```text
pending ──► approved
   │
   └──────► rejected

approved ──► suspended ──► approved
   │             │
   └─────────────┴──────► retired

rejected ──► pending   (new or materially changed evidence)
```

Use these transition rules:

- `pending → approved`: complete the required assessment, tests, ownership, approval evidence and future review date before publication.
- `pending → rejected`: record a clear rejection reason and keep the resource out of the catalog.
- `approved → suspended`: act when continued use becomes unsafe or uncertain; remove the resource from discovery and restrict runtime access as appropriate.
- `suspended → approved`: perform a fresh reassessment, confirm that the triggering concern is resolved, refresh evidence and set a valid review date before republishing.
- `approved` or `suspended → retired`: remove the resource from discovery and follow the retirement path, including identity/integration revocation where applicable.
- `rejected → pending`: use this only when a materially changed proposal or new evidence justifies reassessment. Do not relabel the previous rejection as an approval.
- Treat `retired` as terminal for the governed version. A replacement should normally have its own immutable source pin and review evidence.

## Evidence before publication or republication

Before an entry appears in the approved catalog, confirm at minimum:

- the source is pinned to the reviewed immutable version;
- ownership and security contacts are current;
- requested filesystem, shell, network, secrets and data authority is still accurate;
- delegation and human-approval boundaries remain appropriate;
- required sandboxing, monitoring, audit logging and provenance controls are available;
- test evidence covers both allowed behaviour and important denial paths;
- approval evidence is retained and the review date is in the future;
- the catalog identifier and governance-record reference match the approved record.

For the full lifecycle and reassessment triggers, use the [operating model](operating-model.md).
