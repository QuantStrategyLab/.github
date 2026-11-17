# QuantStrategyLab .github

English | [简体中文](README.zh-CN.md)

Organization-wide baseline files, style guide, and reusable workflow templates for QuantStrategyLab repositories. Reusable PR governance actions live in [Pigbibi/PrGovernance](https://github.com/Pigbibi/PrGovernance).

## Contents

| Path | Purpose |
|---|---|
| `docs/STYLE_GUIDE.md` | Documentation style guide for all public repositories. |
| `docs/advisory-research-boundary.md` | Boundary between advisory research and trading projects. |
| [Architecture](docs/architecture.md) | Repository responsibilities, dependency directions and compatibility tooling. |
| [Architecture conventions](docs/architecture-conventions.md) | Guidance for configuration, interfaces, tests and documentation ownership. |
| [Incremental architecture proposal](docs/adr/0001-incremental-architecture-boundaries.md) | Approach to compatible refactoring and rollback. |
| [Secret scanning](docs/secret-scanning.md) | Publication guard, PR check and weekly all-branch scan templates. |
| [Reusable container release](docs/deployment-workflows.md) | OIDC image releases and zero-traffic staging templates. |
| `profile/README.md` | Text shown on the organization's GitHub profile page. |
| `.github/PULL_REQUEST_TEMPLATE.md` | Default pull request template for organization repositories. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution workflow and commit conventions. |
| [SECURITY.md](SECURITY.md) | Organization security reporting policy. |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community code of conduct. |
| `AGENTS.md` | AI contribution and maintenance rules for this repository. |

## Contributing

Open a pull request describing the problem, change, verification, and impact on downstream repositories. Follow [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md).

## License

Released under the [MIT License](LICENSE).
