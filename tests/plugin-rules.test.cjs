'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { START, END, getDefaults } = require('../hooks/defaults.cjs');

const repository = path.resolve(__dirname, '..');

function temp(t) {
  const dir = fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()), 'power-agent 测试 '));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
}

function run(script, args, cwd) {
  return spawnSync(process.execPath, [script, ...args], { cwd, encoding: 'utf8' });
}

test('generation check detects drift without writing; generation repairs owned blocks only', t => {
  const fixture = temp(t);
  for (const relative of [
    'scripts/sync-plugin-rules.cjs', 'hooks/defaults.cjs',
    'skills/codebase-design/references/minimal-complete-change.md',
    'rules/minimal-complete-change.mdc',
  ]) {
    const target = path.join(fixture, relative);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.copyFileSync(path.join(repository, relative), target);
  }
  const script = path.join(fixture, 'scripts/sync-plugin-rules.cjs');
  const artifact = path.join(fixture, 'rules/minimal-complete-change.mdc');
  const original = fs.readFileSync(artifact, 'utf8');
  const stale = original.replace(getDefaults(), `${START}\nstale\n${END}`);
  fs.writeFileSync(artifact, stale);
  assert.notEqual(run(script, ['--check'], os.tmpdir()).status, 0);
  assert.equal(fs.readFileSync(artifact, 'utf8'), stale);
  assert.equal(run(script, [], os.tmpdir()).status, 0);
  assert.equal(fs.readFileSync(artifact, 'utf8'), original);
  fs.writeFileSync(artifact, original + 'User-owned text\n');
  assert.notEqual(run(script, [], os.tmpdir()).status, 0);
  assert.equal(fs.readFileSync(artifact, 'utf8'), original + 'User-owned text\n');
});
