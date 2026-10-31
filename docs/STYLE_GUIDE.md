# Documentation Style Guide

This guide applies to every public repository in the QuantStrategyLab organization. It describes how we write documentation so that someone outside the organization can install, run, and understand a project without any of our internal context. It also lists what must not appear in a public repository.

## 1. Purpose and scope

Covered by this guide:

- README files in the languages a project actually uses
- files under `docs/`
- `CONTRIBUTING.md` and `CHANGELOG.md`
- pull request descriptions and commit messages
- code comments and docstrings
- web UI copy and locale files
- inline API docs and generated reference

Private repositories are out of scope. They may follow the guide, but nothing enforces it there. Section 6 says where internal notes belong instead.

Where this guide and a repository's existing conventions disagree, follow the repository's convention when it reflects a real audience or platform requirement; otherwise update the text in a focused documentation change.

## 2. Audience and tone

Readers are outside developers and people who trade as a hobby. They have not seen our internal process, so assume general programming and trading knowledge and nothing more.

Write plainly. Short sentences, one idea each. Explain a term the first time it appears, or link to `docs/GLOSSARY.md` or the organization glossary. State facts and behavior instead of narrating how we arrived at them.

Habits to avoid:

- Marketing adjectives: `seamless`, `cutting-edge`, `comprehensive`, `world-class`, `next-generation`, `state-of-the-art`, `best-in-class`. `robust` and `powerful` are not on the list: both are terms of art in statistics, and a rule that flagged them reported twelve non-defects in the research notes.
- Filler openings: `It is worth noting`, `In summary`, `Let's dive in`, `Needless to say`.
- Unnecessary process narration in reader-facing text: `this round`, `in this PR we`, `the owner approved`, `as agreed`.
- Stacked qualifiers. If a sentence needs several to stay true, split it in two.
- Emoji in headings, prose, or tables.

State the trading disclaimer once, near the top of a README, and leave it there. Use a table when each item in a list has more than one attribute. Avoid nesting bullet lists past three levels; a table or a short paragraph usually reads better.

## 3. README structure

Organization metadata repositories and the organization profile README need less. A short statement of purpose, a list of contents, and how to contribute are enough. Installation, runtime configuration, and the trading disclaimer appear only when they apply. Translated READMEs still follow section 4.

Most project READMEs read well with the following outline. Treat it as a default, not a fixed template: adapt the headings, order and length to the project and its audience, and keep only the sections that help a reader install, run or understand it. A small library and a data pipeline do not need the same headings.

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

Notes on the outline:

- The summary under the title says what the project does; it does not claim a status.
- A status or disclaimer section near the top holds the single disclaimer, when the project needs one.
- Configuration is a table. Mark each variable required or optional, give a default, and use placeholders such as `<bucket>`, `<project-id>`, `<your-subdomain>`, `$PROJECTS_ROOT`. Never a real value.
- Architecture links out instead of repeating detail in the README.
- Avoid dated status banners in a README. Status is a present-tense fact; dated history belongs in `CHANGELOG.md`, release notes or a retained evidence record.

## 4. Language

Developer documentation is normally written in English, which keeps code, commands and review discussion consistent across repositories. Language follows the actual audience and the project's existing convention, not a fixed number of files.

- A project may keep a Simplified Chinese README, guides or reference pages when its readers need them. Keep an existing translation accurate when you change the source it covers; do not invent a translation or a parallel file that no one maintains.
- Repositories are not required to mirror READMEs section for section, to use a fixed set of headings, or to ship both English and Chinese versions. Preserve an existing bilingual pair where it is useful, and let either side carry project-specific sections.
- A translation sibling is named `<name>.zh-CN.md`, or `<name>.md` for an English sibling of a Chinese file. A translation must not contain information missing from its source. Mark a translation that has fallen behind, or update it with the change, rather than leaving it silently stale.
- Code identifiers, file names, environment variable names, and API names stay in English, including inside Chinese text.
- Pull request titles and descriptions and commit messages are normally English. A repository or team that works in another language may use it consistently; do not mix languages within one PR description without a reason.

Top of a README that has a translation:

```markdown
English | [简体中文](README.zh-CN.md)
```

Top of `README.zh-CN.md`:

```markdown
[English](README.md) | 简体中文
```

When a Chinese README uses translated headings, these are the usual equivalents:

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

## 5. Content that stays out of public repositories

The following belongs outside public repositories, whether it would appear in README files, `docs/`, comments, pull request descriptions, or UI strings. Keep it in the private ops repository, approved protected storage, or a local ignored path.

| Category | Examples | Instead |
|---|---|---|
| Disposable internal task reports | Progress snapshots, handoffs, per-round task reports, acceptance reports that only track internal work | Keep in the private ops repository or an ignored local path. Versioned research baselines, decisions, contracts and required evidence are different; see below. |
| Raw evidence dumps and private data | Account exports, raw command output with secrets, credential material | Keep raw and private material in approved protected storage. Commit only sanitized evidence that a project requirement calls for. |
| Private approval reasoning and draft-PR status | Which draft PRs exist, who approved what internally, boundary notes | Keep in the PR or the private ops repository. A decision record may state the decision and its rationale without exposing private approval detail. |
| Task scope notes | `this round`, `in this task`, undefined phase codes such as P0-P6 or T06 | Remove. If a concept is public, define it plainly in `docs/ARCHITECTURE.md`. |
| Agent or job identifiers | Job IDs, runner names, agent names, which agent ran what | Remove. Irrelevant to outside readers. |
| Owner approvals | `approved by <maintainer>` | Remove from public docs; record in the PR if needed. |
| PR-number status tables | Tables listing a PR number per phase | Describe the capability, not the PR. Link PRs only in `CHANGELOG.md`. |
| CI head SHAs | 40-character hex identifiers in prose | Leave out. CI status lives in the PR. |
| Account or broker identities | Account numbers, login names, broker account labels | Remove. Never name a real account. |
| Personal infrastructure | Real bucket names, cloud project IDs, `workers.dev` subdomains, home paths | Use `<bucket>`, `<project-id>`, `<your-subdomain>`, `$PROJECTS_ROOT`. |
| Private secrets or token names | Secret names tied to a private deployment, token mount paths | Use a generic placeholder such as `BROKER_API_KEY`. |
| Unqualified performance claims | Real P&L or returns without method and disclaimer | Include method, period, and the disclaimer, or omit. |
| Dated status banners in a README | "2026-09-08 source check: merged; acceptance pending" | Replace with a present-tense status sentence, or remove. Dated evidence records are separate. |

Some records are evidence rather than disposable process output. When a project requirement calls for them, sanitized versions may be versioned in the repository:

- research baselines and frozen result sets
- architecture and design decisions, including ADRs
- financial and accounting contracts; runtime financial records stay in approved protected storage
- data provenance, point-in-time and license evidence
- security and incident records the project must retain

Version these deliberately, with the context a future reader needs. Do not delete a file because its name contains a date or a word such as `report`; review its content and consumers first. Runtime financial records, raw private data, credentials and account-identifying exports stay in approved protected storage, not Git.

If the content is useful internally, move it to a private location. Removing it from the current tree does not remove it from git history; see section 14.

## 6. Where internal notes go

Disposable internal notes do not belong in a public repository. Keep them in the private ops repository, in approved protected storage, or in a local folder outside any repository. If a note has to live in the working tree, put it in an ignored path and never commit it.

```gitignore
.local/
ops-notes/
*.local.md
*.internal.md
```

Reader-facing docs describe behavior, not the history of internal work. History goes to `CHANGELOG.md`, release notes and pull requests. Dated reports, raw evidence tables and approval reasoning go to the private ops repository. Sanitized evidence and decisions that a project requirement says to retain may be versioned; see section 5. Worktree and absolute local paths never appear in committed files.

## 7. docs/ layout and naming

Under `docs/`:

```
docs/
  ARCHITECTURE.md       system structure and components
  CONFIGURATION.md      configuration reference when it outgrows the README
  GLOSSARY.md           terms and definitions
  adr/                  architecture decision records
  guides/               task-oriented how-to documents
  research/             dated research and evidence records
  <name>.zh-CN.md       optional translation sibling
```

- Lowercase kebab-case file names: `order-routing.md`, not `OrderRouting.md` or `order_routing.md`. Conventional documentation names stay uppercase: `README`, `CONTRIBUTING`, `CHANGELOG`, `SECURITY`, `CODE_OF_CONDUCT`, `ARCHITECTURE`, `CONFIGURATION`, `GLOSSARY`, `STYLE_GUIDE`.
- No dates in file names, except under `docs/research/`. A date goes stale when it names something that keeps changing, which is why it is banned elsewhere. A research record does not keep changing: it is a snapshot of one date, and two analyses of the same subject from different months are different documents. Dropping the date leaves them competing for one name.
- ADRs live at `docs/adr/NNNN-title.md`, for example `docs/adr/0007-config-layering.md`. Number them sequentially; never reuse or renumber one. They are the other kind of record, and a sequence number identifies them better than a date.

Write an ADR when a decision is hard to reverse, affects more than one repository, or changes a public interface. Each ADR states context, decision, and consequences, and carries a status on the first line after the title:

```
Status: proposed
Status: accepted
Status: superseded by ADR-NNNN
```

Leave internal review dates and approval names out of an ADR. When a decision is superseded, link the replacement and stop editing the old file.

## 8. CHANGELOG format

When a repository keeps a changelog, follow Keep a Changelog. The file is `CHANGELOG.md`, with the unreleased section at the top. A changelog is useful for released software but is not mandatory for every repository. Use these sections, in this order, only when they have entries: Added, Changed, Fixed, Removed, Security.

- Write entries for users, not maintainers. Describe the observable change.
- Link pull requests here when useful. This is the only place PR numbers belong in public docs.
- Use the version as a heading, not a date from an internal review.
- Keep entries to one line where possible.

```markdown
## [Unreleased]

### Added

- Support for the Alpaca paper-trading endpoint in the broker adapter.

### Fixed

- Corrected position sizing when the account currency differs from the
  instrument currency ([#123](https://example.com/pull/123)).
```

## 9. Pull request descriptions and commits

Write PR descriptions in English. Use the repository's template and keep the sections that apply; write "none" where a section of the template does not apply.

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

Do not paste internal job logs, agent transcripts, evidence tables, or approval notes into a PR description. A documentation-only PR should say so in the Summary.

Commit messages:

- Imperative mood: "add order preview", not "added" or "adds".
- Subject of 72 characters or fewer.
- Conventional Commits prefix: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
- A body when the change needs context. No task codes or round numbers.

## 10. Code comments and docstrings

Comments explain why, not what. If the code already shows what happens, drop the comment.

- No ticket, job, phase, or round references. No `// P0`, no `# T06`, no `# this round`.
- No commented-out code. Delete it; git keeps it.
- TODOs read `TODO(<handle>): <description>` and link an issue when one exists.

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

Comments and docstrings are English in every repository.

## 11. Web UI copy

User-facing text explains the current state and the next action a user can take. It does not explain our process.

- Say what is true now and what the user should do next: "No strategies are enabled. Add one to begin."
- Keep audit, gate, evidence, and approval text out of the UI.
- Do not show internal status codes. Translate each code into a plain label, defined once.
- Keep user-facing strings in locale files, not inline in components.
- Provide an English string for every key. A Chinese locale file is optional and must not contain keys missing from the English one.

## 12. Before and after

### README status section

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

The stage codes are gone. If a reader needs the runtime model, it belongs in `docs/ARCHITECTURE.md` in plain language, not here.

### Internal audit document

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

The dated title, the SHA, the evidence table, and the draft-PR discussion are gone.

### Setup instructions

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

The process date, the approval note, the IAM binding count, and the absolute home path are gone. The bucket name becomes a placeholder.

### Chinese header with status banner

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

The zh-CN sibling, `account-new-risk-gate.zh-CN.md`, mirrors the English file section for section with the same headings translated, links to the English file at the top, and carries no information the English file lacks:

```markdown
[English](account-new-risk-gate.md) | 简体中文

# 账户新增风险门

`quant_platform_kit.risk.account_new_risk_gate` 判断账户是否可以新增风险。
它只读取调用方注入的数据，不调用券商，也不开启实盘交易。
```

The date banner, the merge status, and the PR number are gone. Status is a present-tense fact.

## 13. Review checklist

Apply this to any documentation PR.

- [ ] README covers what a reader needs; the section 3 outline is a default, not a required template.
- [ ] Where relevant, one disclaimer appears near the top, not repeated.
- [ ] No banned marketing words or filler phrases.
- [ ] No emoji in headings, prose, or tables.
- [ ] No dated status banners in reader-facing docs; dated evidence lives in its own retained record.
- [ ] No disposable task reports, raw evidence dumps, private approvals or task-scope notes in reader-facing docs. Sanitized required evidence is versioned separately.
- [ ] No PR-number status tables and no CI head SHAs in prose.
- [ ] No real bucket, project, domain, account, or home-path identifiers; placeholders used.
- [ ] No secret names tied to a private deployment.
- [ ] Where relevant, configuration is presented as a table with required and default columns.
- [ ] Existing translations are updated with the source, or marked as behind.
- [ ] New documents follow the project's audience and language convention; developer docs default to English.
- [ ] Links resolve and point to files that exist.
- [ ] Code comments avoid ticket, job, and round references.
- [ ] UI strings are in locale files and describe state and next action.

Grep list to run before review. Treat a match as a prompt to check, not a certain failure:

- Absolute home paths: `rg '/Users/|/home/'`
- Non-placeholder buckets: `rg 'gs://'`
- Personal subdomains: `rg 'workers\.dev'`
- 40-character hex strings in prose: `rg '\b[0-9a-f]{40}\b'`
- Status tables: `rg '\|\s*(PR|#\d+)'`
- Dated titles in reader-facing docs (a prompt only; dated evidence records are legitimate): `rg -i '(audit|acceptance).*20[0-9]{2}-[0-9]{2}-[0-9]{2}'`
- Process narration: `rg -i 'this round|the owner approved'`

## 14. Applying the guide to an existing repository

Apply the guide one repository at a time, as a single documentation-only PR. Move private content to a private location rather than deleting it, so nothing is lost. Removing text from the current tree does not remove it from git history; rewriting history is out of scope and needs separate, explicit authorization.

1. Move private content out of the public tree to a private location.
2. Review the README against section 3 and adapt it where that helps the reader; do not rewrite a working README only to match headings.
3. Move stray docs into `docs/` with kebab-case names.
4. Move disposable internal content out per section 5, and keep sanitized evidence the project requires.
5. Replace real identifiers with placeholders or a config reference.
6. Add `CHANGELOG.md` entries if relevant.
7. Run the section 13 grep list.
8. Open one documentation-only PR.

## 15. Adoption

The guide is enforced in four light ways.

- The org-wide `PULL_REQUEST_TEMPLATE.md` in this repository applies to every repository without a template of its own. It carries the style-guide checkbox; a checked box is the author's statement, not proof.
- Each repository's `CONTRIBUTING.md` links to this guide in one line:

  ```markdown
  Documentation follows the [QuantStrategyLab documentation style guide](https://github.com/QuantStrategyLab/.github/blob/main/docs/STYLE_GUIDE.md).
  ```

- Reviewers apply the section 13 checklist to documentation PRs.
- A CI step may run the section 13 grep list and warn on matches. No specific tool is required; a simple script is enough. Treat warnings as prompts, not hard failures, so the check does not block legitimate content such as a real placeholder in an example.

This guide lives in the organization-level `.github` repository so every repository can link to one copy. Changes go through a pull request to that repository. State the problem, the change, and the effect on existing repositories.
