# Contributing

Thanks for contributing to QuantStrategyLab repositories.

Documentation follows the [QuantStrategyLab documentation style guide](https://github.com/QuantStrategyLab/.github/blob/main/docs/STYLE_GUIDE.md).

## Workflow

1. Branch from `origin/main` using a short prefix such as `feat/`, `fix/`, `docs/`, `refactor/`, `test/`, or `chore/`.
2. Keep pull requests focused and run the local style and script checks before pushing:

```sh
python3 scripts/test_style.py
python3 scripts/check_style.py --phase 2
```

3. Use English Conventional Commits (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`) with commit headers at most 72 characters.
4. Fill in every section of `.github/PULL_REQUEST_TEMPLATE.md`.

## Security and Content Hygiene

- Never commit `.local/`, `ops-notes/`, `docs/plans/`, `docs/audits/`, `docs/handoffs/`, `docs/changes/`, `docs/acceptance-policy.md`, or real credentials, account IDs, and infrastructure identifiers.
- See [SECURITY.md](SECURITY.md) for private vulnerability reporting.
