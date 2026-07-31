# Contributing

Contributions are welcome when they improve the usefulness, safety or portability of the reference implementation.

## Before opening a pull request

1. Open or reference an issue explaining the governance problem.
2. Keep ARD discovery fields separate from organisation-specific governance fields.
3. Use fictional data in public examples.
4. Never commit credentials, real approval evidence, private audit reports, customer information or internal security details.
5. Run the validator and regression tests locally.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -p 'test_*.py' -v
python scripts/validate_registry.py
```

## Adding a resource example

For a valid resource:

1. Copy an existing record under `registry/resources/`.
2. Use a unique `urn:air:` identifier.
3. Pin the source with a full commit SHA, semantic version or SHA-256 digest.
4. Declare all permissions and data classifications.
5. Set new submissions to `pending` unless the example includes complete fictional approval evidence.
6. Add approved resources to `catalog/ai-catalog.json`.

For a deliberately invalid example, place it under `examples/rejected/` and explain which policy controls it is expected to violate.

## Pull-request checklist

- [ ] No real secrets, private evidence or confidential data are included.
- [ ] JSON files parse successfully.
- [ ] The validator and regression tests pass.
- [ ] Approved catalog entries have approved governance records.
- [ ] Source references are immutable.
- [ ] Permissions and risk tier agree.
- [ ] Approval and review dates are explicit.
- [ ] Documentation distinguishes this project's policy from the ARD specification.
- [ ] New policy rules include a positive and negative example where practical.

## Updating the ARD version

The workflow pins an upstream ARD schema commit. A version update should:

1. compare the old and new schemas;
2. document breaking or ambiguous changes;
3. update the pin;
4. revalidate the sample catalog;
5. update `docs/ard-alignment.md`;
6. avoid claiming compatibility until CI passes and the changes are reviewed.

## Style

- Prefer clear JSON and Markdown over framework-heavy implementation.
- Keep the validator deterministic and credential-free.
- Add dependencies only when they provide clear validation value.
- Make policy failures actionable by naming the field and expected correction.
