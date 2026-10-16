# Documentation Style Guide

This guide applies to every public repository in the QuantStrategyLab organization.

## 1. Purpose and scope

This guide defines how we write documentation in public repositories so that an outside reader can install, run, and understand a project without context from our internal work. It also defines what must not appear in public repositories.

It applies to:

| File or surface | Covered |
|---|---|
| `README.md`, `README.zh-CN.md` | Yes |
| Files under `docs/` | Yes |
| `CONTRIBUTING.md`, `CHANGELOG.md` | Yes |
| Pull request descriptions and commit messages | Yes |
| Code comments and docstrings | Yes |
| Web UI copy and locale strings | Yes |
| Inline API docs and generated reference | Yes |

The guide does not cover private repositories. Private repositories may follow it, but they are out of scope for enforcement. See section 6 for where internal notes belong.

When this guide and a repository's existing convention disagree, this guide wins for public-facing text. Open a docs PR to align the repository.

## 2. Audience and tone

Readers are outside developers and quantitative trading hobbyists. They may have never seen our internal process. Assume no shared context beyond general programming and trading knowledge.

Rules:

- Write plainly. Short sentences. One idea per sentence.
- Explain a term on first use, or link to `docs/GLOSSARY.md` or the org-level glossary. Do not assume a reader knows what a scheduler, adapter, or gateway means in our context.
- Use one disclaimer per README. State it once near the top. Do not repeat it in every section.
- State facts and behaviour. Do not narrate your process, your approval, or your history.
- Use tables when a list has more than one attribute per item.
- Avoid long nested bullet lists. Three levels is the practical maximum; prefer a table or a paragraph.

Banned words and phrases:

| Category | Do not use |
|---|---|
| Marketing adjectives | powerful, seamless, robust, cutting-edge, comprehensive, blazing, best-in-class, world-class, next-generation |
| Filler openings | It is worth noting, In summary, Let's dive in, As we all know, Needless to say |
| Process narration | this round, this task, in this PR we, I have approved, the owner approved, as agreed |
| Hedge stacking | combining several qualifiers in one sentence where one would do |
| Emoji | any emoji in headings, prose, or tables |

If a sentence needs more than one qualifier to stay true, split it into two sentences.

## 3. README skeleton

Organization metadata repositories and organization profile READMEs may use a shorter structure: purpose, contents, and contributing information. Installation, runtime configuration, and trading disclaimers are required only when relevant. Repository-root README translations still follow section 4.

All other public repository READMEs use this skeleton, in this order. Keep section headings exactly as written so tables of contents match across repositories.

Required sections: title, Status, What this is, What this is not, Quick start, Configuration, Repository layout, Contributing, Security, License.

Optional sections: Architecture, and any domain-specific section that does not duplicate the required ones. Optional sections go after Configuration and before Repository layout.

Template:

````markdown
# <Project name>

<One sentence on what the project does.>

## Status

Experimental. Use at your own risk. This project is not financial advice and
does not guarantee any trading result. Live trading can lose money; you are
responsible for your own configuration and orders.

## What this is

<Short paragraph. What the project does and who it is for.>

## What this is not

<Short paragraph. Common misunderstandings, one per sentence.>

## Quick start

Requirements, install, run the test suite, run a dry run.

## Configuration

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `EXAMPLE_VAR` | Yes | none | What it controls. |

Config files and their locations, using placeholders only.

## Architecture

See `docs/ARCHITECTURE.md` and the org-level overview. <One or two sentences
on the main components.>

## Repository layout

```
src/        source
tests/      tests
docs/       documentation
```

## Contributing

See `CONTRIBUTING.md`.

## Security

See `SECURITY.md`. Do not open a public issue for a vulnerability.

## License

<License name and a link to LICENSE.>
````

Rules for the skeleton:

- The one-sentence summary under the title must not contain a status claim.
- Status is the second section. It holds the single disclaimer.
- Configuration uses a table. Mark each variable required or optional and give a default. Use placeholders such as `<bucket>`, `<project-id>`, `<your-subdomain>`, `$PROJECTS_ROOT`. Never a real value.
- Architecture links out rather than duplicating detail in the README.
- Do not add a dated status banner. Status is a present-tense fact, not a log.

## 4. Language policy

English is the default language for public documents. Simplified Chinese is the second language for the README.

Rules:

- Every repository has both `README.md` (English) and `README.zh-CN.md` (Simplified Chinese). They mirror each other section-for-section, in the same order, with the same headings translated. Each file links to the other at the top.
- Keep the two README files in sync in the same pull request. A change to one that changes meaning requires the matching change to the other.
- Write other documents in English by default. New documents are English unless there is a clear reason to write them in Chinese.
- A Chinese-only document outside the README is allowed but discouraged. When you substantially rewrite one, consider moving it to English.
- An optional translation sibling is named `<name>.zh-CN.md` (or `<name>.md` for an English sibling of a Chinese file). A translation must not contain information missing from its source.
- Code identifiers, file names, environment variable names, and API names stay in English everywhere, including inside Chinese text.

Link line for the top of each README:

```markdown
English | [简体中文](README.zh-CN.md)
```

README headings in Simplified Chinese:

| English | Simplified Chinese |
|---|---|
| Status | 状态 |
| What this is | 简介 |
| What this is not | 不适用范围 |
| Quick start | 快速开始 |
| Configuration | 配置 |
| Architecture | 架构 |
| Repository layout | 仓库结构 |
| Contributing | 参与贡献 |
| Security | 安全 |
| License | 许可证 |

Link line for the top of `README.zh-CN.md`:

```markdown
[English](README.md) | 简体中文
```

When a translation falls behind and cannot be fixed in the same PR, mark it at the top with a one-line note and open an issue to resync. Do not leave a stale translation unmarked.

## 5. Forbidden content in public repos

The following must not appear in any public repository, including README files, `docs/`, comments, PR descriptions, and UI strings.

| Category | Examples | What to do instead |
|---|---|---|
| Internal audit logs and acceptance reports | "Console gap audit, 2026-10-15"; acceptance reports; gate reasoning | Move to the private ops repo. Public docs describe behaviour only. |
| Evidence dumps | Tables of checks, fixture results, raw command output with hashes | Summarize the outcome in the PR. Keep raw evidence in the private ops repo. |
| Gate and approval reasoning | Which draft PRs exist; what the owner approved; boundary notes | Keep in the PR or the private ops repo, not in `docs/`. |
| Task scope notes | "this round", "in this task", phase codes such as P0-P6 or T06 with no definition | Remove. If a concept is public, define it plainly in `docs/ARCHITECTURE.md`. |
| Agent or job identifiers | Job IDs, runner names, agent names, which agent ran what | Remove. Irrelevant to outside readers. |
| Owner approvals | "approved by <maintainer>" | Remove from public docs; record in the PR if needed. |
| PR-number status tables | Tables listing a PR number per phase | Describe the capability, not the PR. Link PRs only in `CHANGELOG.md`. |
| CI head SHAs | 40-character hex identifiers in prose | Do not include. CI status lives in the PR. |
| Account or broker identities | Account numbers, login names, broker account labels | Remove. Never name a specific real account. |
| Personal infrastructure | Real bucket names, cloud project IDs, `workers.dev` subdomains, home paths | Use `<bucket>`, `<project-id>`, `<your-subdomain>`, `$PROJECTS_ROOT`. |
| Private secrets or token names | Secret names tied to a private deployment, token mount paths | Use a generic placeholder such as `BROKER_API_KEY`. |
| Unqualified performance claims | Real P&L or returns without method and disclaimer | Include method, period, and the disclaimer, or omit. |
| Dated status banners | "2026-09-08 source check: merged; acceptance pending" | Replace with a present-tense status sentence or remove. |

If content is useful internally, it moves to a private location. Removing text from the current tree does not remove it from git history; see section 14.

## 6. Where internal notes go instead

Internal notes do not belong in public repositories. Put them in the private ops repository, or in a local folder outside any repository.

If a note must live in the working tree, use an ignored path. Never commit it.

Sample `.gitignore` block:

```gitignore
.local/
ops-notes/
*.local.md
*.internal.md
```

Rules:

- Public docs describe behaviour, not history.
- History goes to `CHANGELOG.md` and to pull requests.
- Dated reports, evidence tables, and approval reasoning go to the private ops repository.
- Worktree paths and absolute local paths never appear in committed files.

## 7. Docs layout and naming

Use this structure under `docs/`:

```
docs/
  ARCHITECTURE.md       system structure and components
  CONFIGURATION.md      configuration reference when it outgrows the README
  GLOSSARY.md           terms and definitions
  adr/                  architecture decision records
  guides/               task-oriented how-to documents
  <name>.zh-CN.md       optional translation sibling
```

Naming rules:

- Lowercase kebab-case file names: `order-routing.md`, not `OrderRouting.md` or `order_routing.md`. Conventional documentation names stay uppercase: `README`, `CONTRIBUTING`, `CHANGELOG`, `SECURITY`, `CODE_OF_CONDUCT`, `ARCHITECTURE`, `CONFIGURATION`, `GLOSSARY`, `STYLE_GUIDE`.
- No dates in file names, except ADRs, which use a sequence number.
- ADRs live at `docs/adr/NNNN-title.md`, for example `docs/adr/0007-config-layering.md`.
- Number ADRs sequentially. Never reuse or renumber an existing ADR.

Write an ADR when a decision is hard to reverse, affects more than one repository, or changes a public interface. Each ADR states context, decision, and consequences, and is marked with one of these statuses as the first line after the title:

```
Status: proposed
Status: accepted
Status: superseded by ADR-NNNN
```

Do not put dates of internal reviews in an ADR. Do not put approval names in an ADR. If a decision is superseded, link the replacement and stop editing the old file.

## 8. CHANGELOG format

Follow Keep a Changelog. The file is `CHANGELOG.md`. The unreleased section is at the top.

Sections, in this order, only when they have entries:

- Added
- Changed
- Fixed
- Removed
- Security

Rules:

- Write entries for users, not for maintainers. Describe the observable change.
- Link pull requests here when useful. This is the one place PR numbers are allowed in public docs.
- Use the version as a heading. Do not use dates of internal reviews.
- Keep entries one line where possible.

Example:

```markdown
## [Unreleased]

### Added

- Support for the Alpaca paper-trading endpoint in the broker adapter.

### Fixed

- Corrected position sizing when the account currency differs from the
  instrument currency ([#123](https://example.com/pull/123)).
```

## 9. Pull request description format

Write PR descriptions in English. Use this template. Fill every section; write "none" when a section does not apply.

```markdown
## Summary

<One or two sentences on what changes.>

## Why

<The problem or motivation.>

## Changes

- <Observable change.>
- <Observable change.>

## Testing

<Commands run and their result. Link to CI. No raw logs.>

## Risk and rollback

<Blast radius and how to revert.>

## Breaking changes

<What breaks and the migration. Write "none" if none.>
```

Do not paste internal job logs, agent transcripts, evidence tables, or approval notes into a PR description. A PR that changes documentation only should say so in the Summary.

Commit messages:

- Use the imperative mood: "add order preview", not "added" or "adds".
- Keep the subject at 72 characters or fewer.
- Use Conventional Commits prefixes: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
- Put a body when the change needs context. Do not reference task codes or round numbers.

## 10. Code comments and docstrings

Comments explain why, not what. If the code shows what happens, the comment is not needed.

Rules:

- No ticket, job, phase, or round references in comments. No `// P0`, no `# T06`, no `# this round`.
- No commented-out code. Delete it; git keeps it.
- TODOs use the format `TODO(<handle>): <description>` and include an issue link when one exists.

```python
# TODO(octocat): cache the token across retries; see <issue-link>
```

Python docstrings use Google style:

```python
def place_order(symbol: str, quantity: float) -> OrderId:
    """Place a market order for one symbol.

    Args:
        symbol: Instrument ticker in the venue's format.
        quantity: Signed quantity; negative sells.

    Returns:
        The venue order identifier.

    Raises:
        BrokerError: If the venue rejects the order.
    """
```

TypeScript uses TSDoc:

```typescript
/**
 * Place a market order for one symbol.
 *
 * @param symbol - Instrument ticker in the venue's format.
 * @param quantity - Signed quantity; negative sells.
 * @returns The venue order identifier.
 */
```

Comments and docstrings are in English in every repository.

## 11. Web UI copy

User-facing text explains the current state and the next action a user can take. It does not explain our process.

Rules:

- Say what is true now and what the user should do next. "No strategies are enabled. Add one to begin."
- Do not put audit, gate, evidence, or approval text in the UI.
- Do not show internal status codes. Translate a code into a plain user-facing label, defined once.
- Keep all user-facing strings in locale files, not inline in components.
- Provide an English string for every key. A Chinese locale file is optional and must not contain keys missing from the English file.

## 12. Before / after examples

### Snippet A - README status section

Before:

```markdown
## P0-P6 runtime-authority status

`platform-config.json.meta.runtime_authority` is the machine-readable status
for the P0-P6 control plane. Its current `P0_CONTROL_PLANE_NOT_RUNTIME_WIRED`
status means that this repository has no active preauthorized autonomy policy
and no runtime-wired P0 execution gateway. `default_execution_mode`,
`live_configured`, strategy lifecycle labels, this repository's switch
workflow, and a green CI result are configuration or historical metadata-not
authorization for runtime, orders, funds, or a stage change. P1-P3 non-live
data acquisition needs its own precise contract; P0 does not grant it by
implication. P4-P6 remain undefined.
```

After:

```markdown
## Status

Experimental. This repository stores versioned runtime settings for the
platform repositories. It does not place orders. Settings such as
`live_configured` describe configuration; they do not authorize trading.
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for how settings reach a
runtime.
```

The stage codes are removed. If a reader needs the runtime model, it belongs in `docs/ARCHITECTURE.md` in plain language, not as a control-plane status log.

### Snippet B - internal audit document

Before:

```markdown
# Console gap audit, 2026-10-15

Scope: `QuantRuntimeSettings/web/strategy-switch-console`, inspected at
`<40-char sha>`. All browser checks used loopback and invented fixtures.

| Gap | Evidence | Status |
|---|---|---|
| Local Vite page is blank | Chrome reports `createContext` used before
initialization in `locales.ts` | Fixed in draft #654 |

The three UI PRs are independent and remain drafts.
```

After:

The audit document leaves the repository and moves to the private ops repository. What remains public:

- A bug issue for the blank page with a reproduction, if the fix is not yet released.
- A `CHANGELOG.md` line under Fixed once the fix ships:

```markdown
### Fixed

- Fixed a blank strategy console page caused by locale initialization order.
```

The dated title, the SHA, the evidence table, and the draft-PR discussion are removed.

### Snippet C - setup instructions

Before:

```markdown
- Storage location: reuse the existing shared bucket, prefix
  `gs://<real-shared-bucket>/digest-candidates/` (no new bucket).
- 2026-10-11 the owner added 3 prefix-scoped IAM bindings.
python3 python/scripts/qslctl.py check-all --projects-root /Users/<maintainer>/Projects
```

After:

````markdown
- Storage location: a GCS prefix you choose, set through
  `DIGEST_CANDIDATES_GCS_URI`, for example `gs://<bucket>/digest-candidates/`.
- The producer needs write access and the consumer read access to that prefix.

```bash
python3 python/scripts/qslctl.py check-all --projects-root "$PROJECTS_ROOT"
```
````

The process date, the approval note, the IAM binding count, and the absolute home path are removed. The bucket name becomes a placeholder.

### Snippet D - Chinese header with status banner

Before:

```markdown
# 账户新增风险门（库与平台接线已合；不授予 live）
> 2026-09-08 源码核对：库与所选平台 adapter 已合并；生产数据可用性及交易周期验收另行确认。
| 阶段 | 内容 | 接线状态 |
|---|---|---|
| D1 | `evaluate_capital_risk_envelope` 纯函数信封 | 已合 (#576) |
```

After (English canonical file):

```markdown
# Account new-risk gate

`quant_platform_kit.risk.account_new_risk_gate` decides whether an account may
add new risk. It returns `NEW_RISK_PROHIBITED` when the injected reconciliation
snapshot is unhealthy, equity is missing, or the capital envelope forbids new
risk. It complements the order-level `RiskEngine` and does not replace it.

The gate reads only data the caller injects. It does not call a broker and
does not enable live trading.
```

The zh-CN sibling, `account-new-risk-gate.zh-CN.md`, mirrors the English file section-for-section with the same headings translated, links to the English file at the top, and carries no information the English file lacks:

```markdown
[English](account-new-risk-gate.md) | 简体中文

# 账户新增风险门

`quant_platform_kit.risk.account_new_risk_gate` 判断账户是否可以新增风险。
它只读取调用方注入的数据，不调用券商，也不开启实盘交易。
```

The date banner, the merge status, and the PR number are removed. Status is a present-tense fact.

## 13. Reviewer checklist

Apply to any documentation PR.

- [ ] README follows the section 3 structure for its repository type.
- [ ] Where relevant, one disclaimer appears near the top, not repeated.
- [ ] No banned marketing words or filler phrases.
- [ ] No emoji in headings, prose, or tables.
- [ ] No dated status banners or audit or acceptance titles.
- [ ] No evidence tables, gate reasoning, approvals, or task-scope notes.
- [ ] No PR-number status tables and no CI head SHAs in prose.
- [ ] No real bucket, project, domain, account, or home-path identifiers; placeholders used.
- [ ] No secret names tied to a private deployment.
- [ ] Where relevant, configuration is presented as a table with required and default columns.
- [ ] `README.md` and `README.zh-CN.md` both exist and are updated together in the same PR.
- [ ] New documents are in English unless there is a clear reason otherwise.
- [ ] Links resolve and point to files that exist.
- [ ] Code comments avoid ticket, job, and round references.
- [ ] UI strings are in locale files and describe state and next action.

Quick grep list to run before review. Treat a match as a prompt to check, not a certain failure:

- Absolute home paths: `rg '/Users/|/home/'`
- Non-placeholder buckets: `rg 'gs://'`
- Personal subdomains: `rg 'workers\.dev'`
- 40-character hex strings in prose: `rg '\b[0-9a-f]{40}\b'`
- Status tables: `rg '\|\s*(PR|#\d+)'`
- Dated audit titles: `rg -i '(audit|acceptance).*20[0-9]{2}-[0-9]{2}-[0-9]{2}'`
- Process narration: `rg -i 'this round|the owner approved'`

## 14. Applying the guide to an existing repository

Apply the guide one repository at a time, as one documentation-only PR per repository. Private content is moved to a private location, not only deleted, so nothing is lost.

Removing text from the current tree does not remove it from git history. Rewriting history is out of scope and requires separate, explicit authorization.

Steps for one repository:

1. Move private content out of the public tree to a private location.
2. Align `README.md` and `README.zh-CN.md` to the skeleton in section 3.
3. Move stray docs into `docs/` with kebab-case names.
4. Remove banned content per section 5.
5. Replace real identifiers with placeholders or a config reference.
6. Add `CHANGELOG.md` entries if relevant.
7. Run the section 13 grep list.
8. Open one documentation-only PR.

## 15. Adoption

The guide is enforced in four light ways.

- The org-wide `PULL_REQUEST_TEMPLATE.md` in this repository applies to every repository that has no template of its own. It contains the style-guide checkbox: a checked box is the author's statement, not proof.
- Each repository's `CONTRIBUTING.md` links to this guide in one line:

  ```markdown
  Documentation follows the [QuantStrategyLab documentation style guide](https://github.com/QuantStrategyLab/.github/blob/main/docs/STYLE_GUIDE.md).
  ```

- Reviewers apply the section 13 checklist to documentation PRs.
- A CI step may run the grep list from section 13 and warn on matches. No specific tool is required; a simple script is enough. Treat warnings as prompts, not hard failures, so the check does not block legitimate content such as a real placeholder in an example.

This guide lives in the organization-level `.github` repository so every repository can link to one copy. Changes go through a pull request to that repository. State the problem, the change, and the effect on existing repositories in the PR description.
