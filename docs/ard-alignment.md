# ARD alignment and standards boundary

## Current upstream baseline

This repository currently targets the **Agentic Resource Discovery (ARD) v0.9 draft** and the associated AI Catalog `specVersion` 1.0 data model.

The validation workflow downloads the official `ai-catalog.schema.json` from this pinned upstream commit:

```text
ards-project/ard-spec@5fa2f5aef790b478319f6a3b43adf4661b0ed0e0
```

Pinning avoids silently changing validation behaviour when the draft specification evolves. Updating the pin requires a pull request that reviews schema differences and updates examples or policy assumptions where needed.

## What ARD covers

ARD is a discovery layer. It defines how agentic resources can be advertised, indexed and searched before a client invokes them through their native protocol.

The sample `catalog/ai-catalog.json` uses the current draft's concepts:

- `specVersion: "1.0"`;
- optional host metadata;
- `entries` containing discoverable resources;
- domain-anchored identifiers such as `urn:air:example.com:devops:terraform-review`;
- artifact media types;
- exactly one of `url` or `data`;
- descriptions, tags, capabilities and representative queries;
- optional version, update and custom metadata fields.

## What this project adds

The files under `registry/resources/` are **not part of the ARD specification**. They are an example enterprise governance overlay covering:

- accountable ownership;
- immutable source references;
- filesystem, shell, network and secrets authority;
- permitted data classifications;
- risk tier and approval requirements;
- approval evidence and review expiry;
- sandbox, monitoring and audit requirements;
- retirement and revocation planning.

The custom schema is intentionally separate from the ARD catalog schema so that discovery metadata remains interoperable and organisation-specific policy can evolve independently.

## Publication model

A practical deployment can use the following flow:

```text
Publisher metadata
       |
       v
Governance record submission
       |
       v
Schema + policy validation
       |
       +---- rejected or pending review
       |
       v
Human approval and retained evidence
       |
       v
Approved ARD catalog publication
       |
       v
Discovery service / agent finder
```

Only records with `governance.status` set to `approved` should be published in the approved catalog. Discovery still must not be treated as permission to install or invoke a resource.

## Known limitations

- ARD v0.9 is a draft and may change.
- The example URLs and identities use fictional placeholder data.
- The validator does not perform cryptographic identity or attestation verification.
- The validator does not inspect source code, container images, packages or runtime traffic.
- Approval evidence is represented as text; production systems should use access-controlled evidence stores.
- This project does not implement an ARD search API, crawler or registry service.

## Upstream references

- ARD specification: `https://agenticresourcediscovery.org/spec/`
- ARD source repository: `https://github.com/ards-project/ard-spec`
- Publishing guide: `https://agenticresourcediscovery.org/how_to_publish/`
- GitHub Agent Finder announcement: `https://github.blog/changelog/2026-06-17-agent-finder-for-github-copilot-now-available/`
