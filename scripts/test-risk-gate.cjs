const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const workflow = fs.readFileSync(process.env.RISK_WORKFLOW || path.join(__dirname, '../.github/workflows/risk-gate.yml'), 'utf8');
const script = workflow.split('          script: |\n').at(-1).split('\n').map(x => x.slice(12)).join('\n');
// Substitute only the legacy identity literal so fixtures contain no real owner.
const testScript = script.replace(/(latest\.actor\?\.login === ')[^']+(')/, '$1<PROJECT_ID>-owner$2');
assert.notEqual(testScript, script, 'Legacy owner predicate must remain present');
const execute = new (Object.getPrototypeOf(async function(){}).constructor)('github', 'context', 'core', 'process', testScript);
const discoveryScript = workflow.split('          script: |\n')[1].split('\n\n  evaluate:')[0].split('\n').map(x => x.slice(12)).join('\n');
const discover = new (Object.getPrototypeOf(async function(){}).constructor)('github', 'context', 'core', 'process', discoveryScript);
const H = 'a'.repeat(40), B = 'b'.repeat(40);
const body = '## AI assistance\nCodex, configured model.\n## What changed\nChange ordinary risk logic.\n## How verified\nRun offline regression tests.';
function fixture() {
  return {pr: {number: 1, state: 'open', body, changed_files: 1, labels: [],
    head: {sha: H}, base: {sha: B, ref: 'main', repo: {full_name: '<PROJECT_ID>/sample'}}},
    files: [{filename: 'src/runtime/model.js', status: 'modified'}],
    comments: [{id: 1, user: {type: 'Bot'}, performed_via_github_app: {id: 12345},
      updated_at: new Date(Date.now() - 60000).toISOString(), body: marker()}],
    checks: [{id: 1, name: 'Unit tests', head_sha: H, app: {id: 23456}, status: 'completed', conclusion: 'success'}],
    statuses: [], rules: [], policy: {codex_app_ids: [12345]},
    required: [{context: 'risk-gate', app: null},
      {context: 'pr-template', app: null}, {context: 'Unit tests', app: {databaseId: 23456}}]};
}
function marker(changes = {}) {
  return `<!-- codex-review-state:v1 ${JSON.stringify({code_review: {commit_sha: H,
    status: 'completed', has_any_findings: false, has_unresolved_findings: false, ...changes}})} -->`;
}
async function run(f = fixture()) {
  const out = {statuses: [], errors: [], reads: {}, failures: []};
  const clone = x => structuredClone(x);
  const read = key => {
    out.reads[key] = (out.reads[key] || 0) + 1;
    if (f.apiError === key) throw new Error('private diagnostic <PROJECT_ID>');
    return clone(out.reads[key] > 1 && f.changed?.[key] || f[key]);
  };
  const github = {rest: {pulls: {get: async () => ({data: read('pr')}), listFiles: 'files'},
    issues: {listComments: 'comments', listEvents: 'events'},
    checks: {listForRef: 'checks'}, repos: {listCommitStatusesForRef: 'statuses',
      getBranchRules: 'rules', listPullRequestsAssociatedWithCommit: 'associated',
      getContent: async () => ({data: {encoding: 'base64', content: Buffer.from(JSON.stringify(read('policy'))).toString('base64')}}),
      createCommitStatus: async params => {if (f.apiError === 'publish') throw new Error('private diagnostic <PROJECT_ID>'); out.statuses.push(params);}}},
    paginate: async method => read(method),
    graphql: async () => {const checks = read('required'); return {repository: {pullRequest: {baseRef: {
      branchProtectionRule: f.noClassic ? null : {requiredStatusChecks: checks, requiredStatusCheckContexts: checks.map(x => x.context)}}}}};}};
  const context = {repo: {owner: '<PROJECT_ID>', repo: 'sample'}, serverUrl: 'https://example.invalid', runId: 1,
    payload: f.payload || {pull_request: {number: 1}}};
  const core = {setFailed: text => out.failures.push(text), setOutput: (name, value) => {out[name] = value;}};
  try {
    if (f.eventOnly) await discover(github, context, core, {env: {PR_NUMBER: ''}});
    const numbers = f.eventOnly ? JSON.parse(out.prs || '[]') : [1];
    for (const number of numbers) await execute(github, context, core, {env: {PR_NUMBER: String(number)}});
  } catch (e) {out.errors.push(e.message);}
  out.risk = out.statuses.filter(x => x.context === 'risk-gate').at(-1)?.state;
  return out;
}
test('Ordinary high-risk paths pass only with exact-head clean review and required checks', async () => {
  assert.equal((await run()).risk, 'success');
});
for (const mutation of ['stale', 'running', 'unresolved', 'malformed', 'duplicate', 'untrusted', 'human', 'timestamp', 'missing', 'boolean', 'newer']) {
  test(`Reject invalid review: ${mutation}`, async () => {
    const f = fixture(), c = f.comments[0];
    if (mutation === 'stale') c.body = marker({commit_sha: B});
    if (mutation === 'running') c.body = marker({status: 'running'});
    if (mutation === 'unresolved') c.body = marker({has_unresolved_findings: true});
    if (mutation === 'malformed') c.body = '<!-- codex-review-state:v1 {bad} -->';
    if (mutation === 'duplicate') c.body += marker({has_unresolved_findings: true});
    if (mutation === 'untrusted') c.performed_via_github_app.id = 54321;
    if (mutation === 'human') c.user.type = 'User';
    if (mutation === 'timestamp') c.updated_at = 'invalid';
    if (mutation === 'missing') f.comments = [];
    if (mutation === 'boolean') c.body = marker({has_unresolved_findings: 'false'});
    if (mutation === 'newer') f.comments.push({...c, id: 2, body: marker({status: 'running'})});
    assert.notEqual((await run(f)).risk, 'success');
  });
}
test('Findings already resolved do not require another owner label', async () => {
  const f = fixture(); f.comments[0].body = marker({has_any_findings: true});
  assert.equal((await run(f)).risk, 'success');
});
for (const filename of ['docs/secrets.md', 'tests/deploy/test.js', 'src/iam/policy.json',
  'src/broker_credentials.json', '.env.local', 'infra/main.tf', '.github/workflows/deploy.yml',
  'src/liveTrading.js', 'src/stop_loss.js', 'src/kelly.py', 'src/orders/run.js',
  '.github/governance/policy.json', '.github/workflows/risk-gate.yml']) {
  test(`Owner-only path cannot use automatic approval: ${filename}`, async () => {
    const f = fixture(); f.files[0].filename = filename;
    assert.notEqual((await run(f)).risk, 'success');
  });
}
test('Renaming an owner-only file to ordinary code keeps owner approval', async () => {
  const f = fixture(); f.files[0].status = 'renamed'; f.files[0].previous_filename = 'src/secrets.js';
  assert.notEqual((await run(f)).risk, 'success');
});
for (const mutation of ['failure', 'skipped', 'neutral', 'pending', 'missing', 'wrong-app', 'stale', 'newer-failure', 'status-pending']) {
  test(`Reject incomplete required checks: ${mutation}`, async () => {
    const f = fixture(), c = f.checks[0];
    if (['failure', 'skipped', 'neutral'].includes(mutation)) c.conclusion = mutation;
    if (mutation === 'pending') c.status = 'in_progress';
    if (mutation === 'missing') f.checks = [];
    if (mutation === 'wrong-app') c.app.id = 54321;
    if (mutation === 'stale') c.head_sha = B;
    if (mutation === 'newer-failure') f.checks.push({...c, id: 2, conclusion: 'failure'});
    if (mutation === 'status-pending') {f.required[2].app = null; f.statuses = [{id: 2, context: c.name, state: 'pending', sha: H}];}
    assert.notEqual((await run(f)).risk, 'success');
  });
}
test('Required status contexts also need an exact-head success', async () => {
  const f = fixture(); f.checks = []; f.required[2].app = null;
  f.statuses = [{id: 1, context: 'Unit tests', sha: H, state: 'success'}];
  assert.equal((await run(f)).risk, 'success');
});
test('Ruleset checks are enforced alongside classic protection', async () => {
  const f = fixture(); f.rules = [{type: 'required_status_checks', parameters: {required_status_checks: [{context: 'Security', integration_id: 23456}]}}];
  assert.notEqual((await run(f)).risk, 'success');
});
test('No discoverable required checks cannot authorize automatic approval', async () => {
  const f = fixture(); f.noClassic = true;
  assert.notEqual((await run(f)).risk, 'success');
});
test('Bad PR template cannot pass through the self-dependency exclusion', async () => {
  const f = fixture(); f.pr.body = 'TODO'; assert.notEqual((await run(f)).risk, 'success');
});
for (const key of ['comments', 'checks', 'statuses', 'rules', 'required', 'policy', 'files', 'pr']) {
  test(`API failure is closed and redacted: ${key}`, async () => {
    const f = fixture(); f.apiError = key;
    const out = await run(f);
    assert.notEqual(out.risk, 'success');
    assert.ok(!JSON.stringify(out).includes('private diagnostic'));
  });
}
for (const key of ['pr', 'comments', 'checks', 'rules', 'required', 'files', 'statuses']) {
  test(`Evidence drift between reads fails closed: ${key}`, async () => {
    const f = fixture(); f.changed = {[key]: structuredClone(f[key])};
    if (key === 'pr') f.changed.pr.base.sha = 'c'.repeat(40);
    if (key === 'comments') f.changed.comments[0].body = marker({has_unresolved_findings: true});
    if (key === 'checks') f.changed.checks[0].conclusion = 'failure';
    if (key === 'rules') f.changed.rules.push({type: 'required_status_checks', parameters: {required_status_checks: [{context: 'New gate'}]}});
    if (key === 'required') f.changed.required.push({context: 'New gate', app: null});
    if (key === 'files') f.changed.files[0].filename = 'src/secrets.js';
    if (key === 'statuses') f.changed.statuses.push({id: 2, context: 'Unit tests', state: 'pending', sha: H});
    assert.notEqual((await run(f)).risk, 'success');
  });
}
test('Low-risk prose keeps existing behavior', async () => {
  const f = fixture(); f.files[0].filename = 'docs/example.md'; assert.equal((await run(f)).risk, 'success');
});
test('Concurrent evaluations do not share decisions', async () => {
  const f = fixture(); f.comments = [];
  const [good, bad] = await Promise.all([run(), run(f)]);
  assert.equal(good.risk, 'success'); assert.notEqual(bad.risk, 'success');
});
test('Workflow refreshes on review and check events without new write permissions', () => {
  for (const event of ['issue_comment:', 'check_run:', 'check_suite:', 'status:']) assert.ok(workflow.includes(event));
  assert.doesNotMatch(workflow, /checkout|secrets:|issues: write|pull-requests: write|actions: write/);
});
test('A low-risk result cannot survive base drift', async () => {
  const f = fixture(); f.files[0].filename = 'docs/example.md'; f.changed = {pr: structuredClone(f.pr)};
  f.changed.pr.base.sha = 'c'.repeat(40);
  assert.notEqual((await run(f)).risk, 'success');
});
test('Status publication errors never expose API diagnostics', async () => {
  const f = fixture(); f.apiError = 'publish'; const out = await run(f);
  assert.notEqual(out.risk, 'success'); assert.ok(!JSON.stringify(out).includes('private diagnostic'));
  assert.ok(out.failures.length);
});
test('Owner globs escape literal dots', async () => {
  const f = fixture(); f.files[0].filename = 'src/notXkey';
  assert.equal((await run(f)).risk, 'success');
});
test('Future review timestamps cannot authorize approval', async () => {
  const f = fixture(); f.comments[0].updated_at = '2999-01-01T00:00:00Z';
  assert.notEqual((await run(f)).risk, 'success');
});
for (const event of ['check_run', 'check_suite', 'status']) {
  test(`Check event looks up only open PRs with the current event head: ${event}`, async () => {
    const f = fixture(); f.eventOnly = true; f.payload = event === 'status' ? {sha: H} : {[event]: {head_sha: H}};
    f.associated = [{number: 1, state: 'open', head: {sha: H}}, {number: 2, state: 'closed', head: {sha: H}},
      {number: 3, state: 'open', head: {sha: B}}];
    const out = await run(f); assert.equal(out.risk, 'success'); assert.equal(out.reads.pr, 2);
  });
}
test('Review comment event reads the associated PR', async () => {
  const f = fixture(); f.eventOnly = true; f.payload = {issue: {number: 1}};
  assert.equal((await run(f)).risk, 'success');
});
test('Check event lookup failure is redacted and closed', async () => {
  const f = fixture(); f.eventOnly = true; f.payload = {sha: H}; f.apiError = 'associated';
  const out = await run(f); assert.ok(out.failures.length); assert.ok(!JSON.stringify(out).includes('private diagnostic'));
});
test('The two self-produced contexts cannot claim a different App identity', async () => {
  const f = fixture(); f.required[0].app = {databaseId: 54321};
  assert.notEqual((await run(f)).risk, 'success');
});
test('A ruleset without classic protection can authorize when every check is green', async () => {
  const f = fixture(); f.noClassic = true; f.rules = [{type: 'required_status_checks', parameters: {
    required_status_checks: [{context: 'Unit tests', integration_id: 23456}]}}];
  assert.equal((await run(f)).risk, 'success');
});
test('Owner-only paths retain the existing owner-label event predicate', async () => {
  const f = fixture(); f.files[0].filename = 'src/secrets.js'; f.pr.labels = [{name: 'owner-approved'}];
  f.events = [{id: 1, event: 'labeled', label: {name: 'owner-approved'}, actor: {login: '<PROJECT_ID>-owner'}}];
  assert.equal((await run(f)).risk, 'success');
  f.events.push({id: 2, event: 'unlabeled', label: {name: 'owner-approved'}, actor: {login: '<PROJECT_ID>-owner'}});
  assert.notEqual((await run(f)).risk, 'success');
});
test('Owner-label event revocation during evaluation blocks the old approval', async () => {
  const f = fixture(); f.files[0].filename = 'src/secrets.js'; f.pr.labels = [{name: 'owner-approved'}];
  f.events = [{id: 1, event: 'labeled', label: {name: 'owner-approved'}, actor: {login: '<PROJECT_ID>-owner'}}];
  f.changed = {events: [...f.events, {id: 2, event: 'unlabeled', label: {name: 'owner-approved'}}]};
  assert.notEqual((await run(f)).risk, 'success');
});
test('Ordinary high-risk paths cannot use a legacy owner label to bypass review', async () => {
  const f = fixture(); f.pr.labels = [{name: 'owner-approved'}]; f.comments = [];
  f.events = [{id: 1, event: 'labeled', label: {name: 'owner-approved'}, actor: {login: '<PROJECT_ID>-owner'}}];
  assert.notEqual((await run(f)).risk, 'success');
});
test('Native workflow events resolve to the same PR writer', async () => {
  const f = fixture(); f.eventOnly = true; f.payload = {workflow_run: {head_sha: H}};
  f.associated = [{number: 1, state: 'open', head: {sha: H}}];
  assert.equal((await run(f)).risk, 'success');
  assert.match(workflow, /group: risk-gate-\$\{\{ github.repository \}\}-\$\{\{ matrix.pr \}\}/);
  assert.match(workflow, /cancel-in-progress: false/);
  assert.match(workflow, /PR_NUMBER: \$\{\{ matrix.pr \}\}/);
});
for (const mutation of ['missing', 'duplicate', 'rename', 'count']) {
  test(`Incomplete file evidence blocks evaluation: ${mutation}`, async () => {
    const f = fixture();
    if (mutation === 'missing') f.files = [];
    if (mutation === 'duplicate') {f.files.push(f.files[0]); f.pr.changed_files = 2;}
    if (mutation === 'rename') f.files[0].status = 'renamed';
    if (mutation === 'count') f.pr.changed_files = 2;
    assert.notEqual((await run(f)).risk, 'success');
  });
}
