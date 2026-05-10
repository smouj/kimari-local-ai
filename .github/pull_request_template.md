## Description

Brief description of the change and why it's needed.

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring (no functional change)
- [ ] CI / build / packaging change

## Testing

How was this tested?

- [ ] Existing tests pass (`python -m pytest tests/ -q`)
- [ ] New tests added for the change
- [ ] Manual testing performed
- [ ] `ruff check kimari/ tests/` passes
- [ ] `ruff format --check kimari/ tests/` passes

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code where needed
- [ ] I have updated the documentation accordingly
- [ ] My changes generate no new warnings
- [ ] CHANGELOG.md updated (if applicable)
- [ ] ROADMAP.md updated (if applicable)
- [ ] No GGUF model files added or tracked
- [ ] No secrets, tokens, or API keys in the code
- [ ] No false claims (Kimari-4B published, Responses API supported, etc.)
- [ ] No unsafe changes to host binding (0.0.0.0 without warning)
- [ ] `default_profile` is still `"test"`
- [ ] `python scripts/release/check-release.py` passes (if applicable)

## Related Issues

Closes #(issue number) — if applicable
