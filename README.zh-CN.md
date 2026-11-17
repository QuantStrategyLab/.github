# QuantStrategyLab .github

[English](README.md) | 简体中文

QuantStrategyLab 各仓库共用的组织级文档规范、流程模板与安全基线仓库；可复用 PR 治理动作统一维护在 [Pigbibi/PrGovernance](https://github.com/Pigbibi/PrGovernance)。

## 内容

| 路径 | 用途 |
|---|---|
| `docs/STYLE_GUIDE.md` | 所有公开仓库的文档规范。 |
| `docs/advisory-research-boundary.md` | 投顾研究项目与交易项目之间的边界。 |
| [架构说明](docs/architecture.md) | 仓库职责、依赖方向与现有兼容性工具。 |
| [架构规范](docs/architecture-conventions.md) | 配置、接口、测试和文档归属的实施建议。 |
| [渐进架构提案](docs/adr/0001-incremental-architecture-boundaries.md) | 保持兼容的重构与回滚方案。 |
| [密钥扫描](docs/secret-scanning.md) | 发布前扫描、PR 检查和每周全分支扫描模板。 |
| [共用容器发布](docs/deployment-workflows.md) | 使用 OIDC 发布容器作业和内网服务的复用模板。 |
| `profile/README.md` | 组织 GitHub 主页上显示的介绍。 |
| `.github/PULL_REQUEST_TEMPLATE.md` | 组织默认使用的 pull request 模板。 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献流程与提交规范。 |
| [SECURITY.md](SECURITY.md) | 组织安全漏洞披露说明。 |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | 社区行为准则。 |
| `AGENTS.md` | 本仓库的 AI 参与与维护规则。 |

## 参与贡献

提交 pull request，说明要解决的问题、改动、验证结果及对现有仓库的影响。AI 助手与维护者请遵守 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [AGENTS.md](AGENTS.md)。

## 许可证

基于 [MIT License](LICENSE) 发布。
