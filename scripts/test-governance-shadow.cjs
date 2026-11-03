const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const workflowPath = process.env.SHADOW_WORKFLOW || path.join(__dirname, '../.github/workflows/governance-acceptance.yml');
const workflow = fs.readFileSync(workflowPath, 'utf8');
const script = workflow.split('          script: |\n')[1]?.split('\n').map(x => x.slice(12)).join('\n');
assert.ok(script, 'Reusable engine must contain executable observer');
const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
const execute = new AsyncFunction('github', 'context', 'core', 'require', 'process', script);
const H = 'a'.repeat(40), B = 'b'.repeat(40), R = 'c'.repeat(40);
const policy = JSON.parse(fs.readFileSync(path.join(__dirname, '../.github/governance/policy.json')));
function fixture() {
  return {pr: {id: 1, state: 'open', head: {sha: H, repo: {id: 2}},
    base: {sha: B, ref: 'main', repo: {id: 2, full_name: '<PROJECT_ID>/sample'}},
    user: {login: '<PROJECT_ID>-author'}, changed_files: 1, additions: 1, deletions: 0},
    files: [{filename: 'docs/example.md', status: 'added', additions: 1, deletions: 0, patch: '@@ -0,0 +1 @@\n+Plain explanatory prose.'}],
    evidence: {reviews: [], comments: []}, policy: structuredClone(policy)};
}
async function observe(f = fixture()) {
  const state = {failed: false, summary: '', calls: 0};
  const clone = x => structuredClone(x);
  const github = {rest: {repos: {getContent: async () => {
    if (f.apiError) throw new Error('private token <PROJECT_ID>');
    return {data: {encoding: 'base64', content: Buffer.from(JSON.stringify(f.policy)).toString('base64')}};
  }}, pulls: {get: async () => ({data: clone(++state.calls > 1 && f.current || f.pr)}),
    listFiles: 'files', listReviews: 'reviews'}, issues: {listComments: 'comments'}},
    paginate: async method => clone(method === 'files' ? f.files : f.evidence[method])};
  const core = {setFailed: () => {state.failed = true;}, setOutput: () => {}, summary: {
    addHeading() {return this;}, addCodeBlock(s) {state.summary = s; return this;}, async write() {}}};
  const report = await execute(github, {repo: {owner: '<PROJECT_ID>', repo: 'sample'}}, core, require,
    {env: {MODE: f.mode || 'SHADOW', POLICY_REVISION: R, PR_NUMBER: '1'}});
  assert.equal(report.merge_authorized, false);
  assert.ok(!state.summary.includes('private token'));
  return {report, state};
}
test('Narrow added prose produces an observation, never merge authorization', async () => {
  const {report} = await observe(); assert.equal(report.tier, 'R0'); assert.equal(report.observation, 'PROSE_CANDIDATE');
});
test('Ordinary code needs independent review', async () => {
  const f = fixture(); f.files[0].filename = 'src/example.js';
  assert.equal((await observe(f)).report.observation, 'PENDING_REVIEW');
});
function codexFixture() {
  const f = fixture(); f.files[0].filename = 'src/example.js'; f.policy.codex_app_ids = [12345];
  const record = {code_review: {commit_sha: H, status: 'completed',
    has_any_findings: false, has_unresolved_findings: false}};
  const entry = {id: 11, user: {type: 'Bot'}, performed_via_github_app: {id: 12345},
    updated_at: new Date().toISOString(), body: `<!-- codex-review-state:v1 ${JSON.stringify(record)} -->`};
  f.evidence.comments = [entry];
  return {f, entry, record};
}
test('Codex current-head receipt is observation only, never approval', async () => {
  const {f} = codexFixture(); const {report} = await observe(f);
  assert.equal(report.codex_observation, 'NO_REPORTED_FINDINGS');
  assert.equal(report.observation, 'PENDING_REVIEW');
  assert.equal(report.independent_review, false);
});
for (const [mutation, expected] of [['stale', 'STALE_OR_UNKNOWN'], ['running', 'IN_PROGRESS'],
  ['unresolved', 'UNRESOLVED_FINDINGS'], ['resolved', 'FINDINGS_REPORTED'],
  ['malformed', 'UNKNOWN'], ['untrusted', 'NOT_FOUND'], ['user', 'NOT_FOUND'], ['timestamp', 'UNKNOWN']]) {
  test(`Codex receipt preserves untrusted or incomplete state: ${mutation}`, async () => {
    const {f, entry, record} = codexFixture();
    if (mutation === 'stale') record.code_review.commit_sha = 'd'.repeat(40);
    if (mutation === 'running') record.code_review.status = 'running';
    if (mutation === 'unresolved') record.code_review.has_unresolved_findings = true;
    if (mutation === 'resolved') record.code_review.has_any_findings = true;
    if (mutation === 'untrusted') entry.performed_via_github_app.id = 54321;
    if (mutation === 'user') entry.user.type = 'User';
    if (mutation === 'timestamp') entry.updated_at = 'invalid';
    entry.body = mutation === 'malformed' ? '<!-- codex-review-state:v1 {bad} -->'
      : `<!-- codex-review-state:v1 ${JSON.stringify(record)} -->`;
    const {report} = await observe(f);
    assert.equal(report.codex_observation, expected);
    assert.equal(report.observation, 'PENDING_REVIEW');
  });
}
test('Unconfigured Codex observer never trusts arbitrary receipts', async () => {
  const {f} = codexFixture(); f.policy.codex_app_ids = [];
  assert.equal((await observe(f)).report.codex_observation, 'NOT_CONFIGURED');
});
test('A malformed newer native receipt cannot revive an older clean receipt', async () => {
  const {f, entry} = codexFixture();
  f.evidence.comments.push({...entry, id: 12, updated_at: 'invalid'});
  assert.equal((await observe(f)).report.codex_observation, 'UNKNOWN');
});
for (const duplicate of ['unresolved', 'malformed']) {
  test(`Duplicate Codex receipt blocks an ambiguous observation: ${duplicate}`, async () => {
    const {f, entry, record} = codexFixture();
    record.code_review.has_unresolved_findings = true;
    entry.body += duplicate === 'unresolved'
      ? `\n<!-- codex-review-state:v1 ${JSON.stringify(record)} -->`
      : '\n<!-- codex-review-state:v1 {bad} -->';
    assert.equal((await observe(f)).report.codex_observation, 'UNKNOWN');
  });
}
for (const filename of ['.github/workflows/example.yml', 'tests/example.js', 'docs/acceptance-policy.md', 'AGENTS.md']) {
  test(`Sensitive scope is R2: ${filename}`, async () => {
    const f = fixture(); f.files[0].filename = filename;
    assert.equal((await observe(f)).report.tier, 'R2');
  });
}
test('Authority-changing Markdown is R2', async () => {
  const f = fixture(); f.files[0].patch = '@@ -0,0 +1 @@\n+Approval is optional.';
  assert.equal((await observe(f)).report.tier, 'R2');
});
for (const mutation of ['missing', 'truncated', 'count', 'binary', 'duplicate', 'rename', 'api', 'mode', 'policy']) {
  test(`Unknown integrity never becomes valid: ${mutation}`, async () => {
    const f = fixture();
    if (mutation === 'missing') f.files = [];
    if (mutation === 'truncated') f.files[0].patch = '@@ -0,0 +1,2 @@\n+Only one line';
    if (mutation === 'count') f.pr.additions = 2;
    if (mutation === 'binary') delete f.files[0].patch;
    if (mutation === 'duplicate') {f.files.push(f.files[0]); f.pr.changed_files = 2;}
    if (mutation === 'rename') f.files[0].status = 'renamed';
    if (mutation === 'api') f.apiError = true;
    if (mutation === 'mode') f.mode = 'ENFORCE';
    if (mutation === 'policy') f.policy.merge_authorized = true;
    const {report, state} = await observe(f);
    assert.equal(report.observation, 'UNKNOWN'); assert.equal(state.failed, true);
  });
}
for (const drift of ['head', 'base', 'ref', 'files', 'author']) {
  test(`Re-read rejects snapshot drift: ${drift}`, async () => {
    const f = fixture(); f.current = structuredClone(f.pr);
    if (drift === 'head') f.current.head.sha = 'd'.repeat(40);
    if (drift === 'base') f.current.base.sha = 'e'.repeat(40);
    if (drift === 'ref') f.current.base.ref = 'other';
    if (drift === 'files') f.current.changed_files = 2;
    if (drift === 'author') f.current.user.login = '<PROJECT_ID>-other';
    assert.equal((await observe(f)).report.observation, 'UNKNOWN');
  });
}
async function recordFixture() {
  const f = fixture(); f.files[0].filename = '.github/example.yml';
  f.policy.reviewers = ['<PROJECT_ID>-reviewer', '<PROJECT_ID>-other']; f.policy.owners = ['<PROJECT_ID>-owner'];
  const {report} = await observe(f);
  const record = {schema_version: 1, kind: 'review', repository: '<PROJECT_ID>/sample', pr: 1,
    head: H, base: B, scope: report.scope, policy: report.policy, decision: 'approve', findings: [],
    expires_at: new Date(Date.now() + 3600000).toISOString()};
  const created_at = new Date(Date.now() - 60000).toISOString();
  f.evidence.reviews = [{id: 1, user: {login: '<PROJECT_ID>-reviewer', type: 'User'}, state: 'APPROVED', commit_id: H,
    submitted_at: created_at, body: JSON.stringify(record)}];
  return {f, record, created_at};
}
test('Configured independent review still requires distinct owner evidence for R2', async () => {
  const {f} = await recordFixture(); assert.equal((await observe(f)).report.observation, 'PENDING_OWNER');
});
for (const invalid of ['expired', 'base', 'scope', 'policy', 'author', 'bot', 'dismissed', 'defect', 'revoked']) {
  test(`Reject invalid independent review: ${invalid}`, async () => {
    const {f, record} = await recordFixture();
    if (invalid === 'expired') record.expires_at = new Date(Date.now() - 1000).toISOString();
    if (['base', 'scope', 'policy'].includes(invalid)) record[invalid] = 'f'.repeat(40);
    if (invalid === 'author') {f.policy.reviewers.push(f.pr.user.login); f.evidence.reviews[0].user.login = f.pr.user.login;}
    if (invalid === 'bot') f.evidence.reviews[0].user.type = 'Bot';
    if (invalid === 'dismissed') f.evidence.reviews[0].state = 'DISMISSED';
    if (invalid === 'defect') record.findings = [{severity: 'defect'}];
    if (invalid === 'revoked') record.decision = 'revoke';
    f.evidence.reviews[0].body = JSON.stringify(record);
    assert.equal((await observe(f)).report.observation, 'PENDING_REVIEW');
  });
}
test('Edited owner comment cannot authorize; subsequent revoke dominates approval', async () => {
  const {f, record, created_at} = await recordFixture(); record.kind = 'owner';
  f.evidence.comments = [{id: 2, user: {login: '<PROJECT_ID>-owner', type: 'User'}, created_at, updated_at: created_at,
    body: JSON.stringify(record)}];
  assert.equal((await observe(f)).report.observation, 'EVIDENCE_PRESENT');
  f.evidence.comments[0].updated_at = new Date().toISOString();
  assert.equal((await observe(f)).report.observation, 'PENDING_OWNER');
  f.evidence.comments[0].updated_at = created_at;
  f.evidence.comments.push({...f.evidence.comments[0], id: 3, body: JSON.stringify({...record, decision: 'revoke'})});
  assert.equal((await observe(f)).report.observation, 'PENDING_OWNER');
});
test('Workflow has no checkout, secret inheritance, write permission or legacy status publisher', () => {
  assert.doesNotMatch(workflow, /checkout|secrets:|: write|createCommitStatus|checks\.create|pull_request_target/);
  assert.match(workflow, /timeout-minutes: 5/);
});

test('An unresolved concrete defect cannot be erased by another reviewer approval', async () => {
  const {f, record} = await recordFixture();
  f.evidence.reviews.push({...f.evidence.reviews[0], id: 2, state: 'CHANGES_REQUESTED',
    body: JSON.stringify({...record, findings: [{severity: 'defect'}]})});
  f.evidence.reviews.push({...f.evidence.reviews[0], id: 3, user: {login: '<PROJECT_ID>-other', type: 'User'}});
  assert.equal((await observe(f)).report.observation, 'PENDING_REVIEW');
});
test('A comment-only review does not clear a prior change request', async () => {
  const {f, record} = await recordFixture();
  f.evidence.reviews.push({...f.evidence.reviews[0], id: 2, state: 'CHANGES_REQUESTED'});
  f.evidence.reviews.push({...f.evidence.reviews[0], id: 3, state: 'COMMENTED', body: 'Follow-up comment'});
  f.evidence.reviews.push({...f.evidence.reviews[0], id: 4, user: {login: '<PROJECT_ID>-other', type: 'User'},
    body: JSON.stringify(record)});
  const {report} = await observe(f);
  assert.equal(report.independent_review, false);
  assert.equal(report.observation, 'PENDING_REVIEW');
});
test('A valid later approval by the requesting reviewer clears the request', async () => {
  const {f} = await recordFixture();
  f.evidence.reviews.push({...f.evidence.reviews[0], id: 2, state: 'CHANGES_REQUESTED'});
  f.evidence.reviews.push({...f.evidence.reviews[0], id: 3, state: 'COMMENTED', body: 'Follow-up'});
  f.evidence.reviews.push({...f.evidence.reviews[0], id: 4});
  const {report} = await observe(f);
  assert.equal(report.independent_review, true);
  assert.equal(report.observation, 'PENDING_OWNER');
});
test('A dismissed change request no longer blocks an independent approval', async () => {
  const {f} = await recordFixture();
  f.evidence.reviews.push({...f.evidence.reviews[0], id: 2, state: 'DISMISSED'});
  f.evidence.reviews.push({...f.evidence.reviews[0], id: 3,
    user: {login: '<PROJECT_ID>-other', type: 'User'}});
  assert.equal((await observe(f)).report.observation, 'PENDING_OWNER');
});
test('An expired approval cannot clear a prior change request', async () => {
  const {f, record} = await recordFixture();
  f.evidence.reviews.push({...f.evidence.reviews[0], id: 2, state: 'CHANGES_REQUESTED'});
  record.expires_at = new Date(Date.now() - 1000).toISOString();
  f.evidence.reviews.push({...f.evidence.reviews[0], id: 3, body: JSON.stringify(record)});
  f.evidence.reviews.push({...f.evidence.reviews[0], id: 4,
    user: {login: '<PROJECT_ID>-other', type: 'User'}});
  assert.equal((await observe(f)).report.observation, 'PENDING_REVIEW');
});
test('Parallel observations do not share mutable decisions', async () => {
  const f = fixture(); f.apiError = true;
  const [bad, good] = await Promise.all([observe(f), observe()]);
  assert.equal(bad.report.observation, 'UNKNOWN');
  assert.equal(good.report.observation, 'PROSE_CANDIDATE');
});

test('Optional style advice does not require repair', async () => {
  const {f, record} = await recordFixture();
  record.findings = [{kind: 'advisory'}]; f.evidence.reviews[0].body = JSON.stringify(record);
  assert.equal((await observe(f)).report.observation, 'PENDING_OWNER');
});
