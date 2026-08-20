## Problem

<!-- What governance, validation or documentation problem does this solve? -->

## What changed

<!-- Keep the scope focused and list the important files or policy behaviour changed. -->

## Registry and catalog impact

- Governance records changed:
- Catalog entries changed:
- Validator or schema behaviour changed:
- ARD version or upstream pin changed:

## Validation

<!-- Include exact commands and results. Use the immutable ARD schema pin documented in CONTRIBUTING.md. -->

- [ ] `python3 -m unittest discover -s tests -p 'test_*.py' -v`
- [ ] `python3 scripts/check_markdown_links.py`
- [ ] Downloaded the pinned ARD schema documented in `CONTRIBUTING.md`.
- [ ] `python3 scripts/validate_registry.py --ard-schema /tmp/ai-catalog.schema.json`
- [ ] Additional validation is described above when applicable.

## Safety and evidence

- [ ] Examples use fictional data only.
- [ ] No credentials, private approval evidence, customer data or internal security details are included.
- [ ] Source references are immutable.
- [ ] Permissions, risk tier, approval requirements and runtime controls agree.
- [ ] Discovery fields remain separate from organisation-specific governance policy.
- [ ] Any ARD compatibility claim is backed by the pinned schema and documentation.
- [ ] The change contains no unrelated dependency, workflow-permission or runtime changes.

Closes #
