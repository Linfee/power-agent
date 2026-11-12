'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');

const repo = path.resolve(__dirname, '..');
const hosts = [
  { name: 'claude', root: 'CLAUDE_PLUGIN_ROOT', configs: { SessionStart: 'hooks/hooks.json', SubagentStart: 'hooks/claude.json' } },
  { name: 'codex', root: 'PLUGIN_ROOT', configs: { SessionStart: 'hooks/codex.json', SubagentStart: 'hooks/codex.json' } },
  { name: 'factory', root: 'CLAUDE_PLUGIN_ROOT', configs: { SessionStart: 'hooks/hooks.json' } },
];

function fixture(t) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'power agent hooks '));
  t.after(() => fs.rmSync(temp, { recursive: true, force: true }));
  const install = path.join(temp, "installed plugin $HOME 'quoted' `touch INJECTED` $(touch INJECTED) with spaces");
  const cwd = path.join(temp, 'business project');
  const home = path.join(temp, 'home');
  fs.mkdirSync(cwd, { recursive: true });
  fs.mkdirSync(home);
  for (const dir of ['hooks', 'skills/codebase-design/references']) {
    fs.mkdirSync(path.join(install, dir), { recursive: true });
  }
  for (const file of ['hooks/inject.cjs', 'hooks/defaults.cjs', 'hooks/hooks.json', 'hooks/claude.json', 'hooks/codex.json', 'skills/codebase-design/references/minimal-complete-change.md']) {
    fs.copyFileSync(path.join(repo, file), path.join(install, file));
  }
  return { install, cwd, home };
}

function command(host, event, install) {
  const config = JSON.parse(fs.readFileSync(path.join(install, host.configs[event]), 'utf8'));
  let hook = config.hooks[event][0];
  if (hook.hooks) hook = hook.hooks[0];
  if (hook.args) {
    return { executable: process.execPath, args: hook.args.map(arg => arg.replace(`\${${host.root}}`, install)) };
  }
  // Factory expands plugin-root tokens when loading, before its shell sees them.
  let shellCommand = process.platform === 'win32' ? (hook.commandWindows || hook.powershell || hook.command) : (hook.bash || hook.command);
  if (host.name === 'factory') {
    shellCommand = shellCommand.replace(/\$(?:\{(?:CLAUDE|DROID)_PLUGIN_ROOT\}|(?:CLAUDE|DROID)_PLUGIN_ROOT\b)/g, () => install);
  }
  return process.platform === 'win32'
    ? { executable: 'powershell.exe', args: ['-NoProfile', '-Command', shellCommand] }
    : { executable: '/bin/sh', args: ['-c', shellCommand] };
}

function run(host, event, f, input) {
  const { executable, args } = command(host, event, f.install);
  return spawnSync(executable, args, {
    cwd: f.cwd,
    env: { HOME: f.home, XDG_CONFIG_HOME: f.home, XDG_CACHE_HOME: f.home, CODEX_HOME: f.home, CLAUDE_CONFIG_DIR: f.home, PATH: `${path.dirname(process.execPath)}${path.delimiter}/usr/bin${path.delimiter}/bin`, [host.root]: host.name === 'factory' ? '/PLUGIN_ROOT_NOT_EXPANDED_ERROR' : f.install },
    input,
    encoding: 'utf8',
    timeout: 5000,
  });
}

test('registered hooks inject installed defaults for each supported context event', t => {
  const f = fixture(t);
  const defaults = require(path.join(f.install, 'hooks/defaults.cjs')).getDefaults();
  for (const host of hosts) {
    for (const event of Object.keys(host.configs)) {
      // Deliberately invalid input demonstrates that no prompt or project data is needed.
      const result = run(host, event, f, '{invalid JSON');
      assert.equal(result.error, undefined, `${host.name}/${event}: ${result.error}`);
      assert.equal(result.status, 0, `${host.name}/${event}: ${result.stderr}`);
      const output = JSON.parse(result.stdout);
      assert.deepEqual(output, { hookSpecificOutput: { hookEventName: event, additionalContext: defaults } });
    }
  }
  assert.deepEqual(fs.readdirSync(f.cwd), []);
});

test('hook reports a missing or empty installed source without returning fake context', t => {
  const f = fixture(t);
  const source = path.join(f.install, 'skills/codebase-design/references/minimal-complete-change.md');
  for (const missing of [true, false]) {
    if (missing) fs.unlinkSync(source);
    else fs.writeFileSync(source, '   \n');
    for (const host of hosts) {
      const result = run(host, Object.keys(host.configs)[0], f, '');
      assert.equal(result.status, 1, `${host.name}: ${result.stderr}`);
      assert.equal(result.stdout, '');
      assert.match(result.stderr, /Power-Agent defaults unavailable:/);
    }
  }
});

test('hook exits without waiting for an open stdin pipe', async t => {
  const f = fixture(t);
  const child = spawn(process.execPath, [path.join(f.install, 'hooks/inject.cjs'), 'SessionStart'], {
    cwd: f.cwd, env: { HOME: f.home, XDG_CONFIG_HOME: f.home, XDG_CACHE_HOME: f.home, PATH: '/usr/bin:/bin' }, stdio: ['pipe', 'pipe', 'pipe'],
  });
  let stdout = '';
  child.stdout.setEncoding('utf8').on('data', data => { stdout += data; });
  const status = await new Promise((resolve, reject) => {
    const timer = setTimeout(() => { child.kill(); reject(new Error('hook waited for stdin EOF')); }, 5000);
    child.on('error', error => { clearTimeout(timer); reject(error); });
    child.on('close', code => { clearTimeout(timer); resolve(code); });
  });
  assert.equal(status, 0);
  assert.equal(JSON.parse(stdout).hookSpecificOutput.hookEventName, 'SessionStart');
});

test('unsupported invocation fails safely', t => {
  const f = fixture(t);
  const result = spawnSync(process.execPath, [path.join(f.install, 'hooks/inject.cjs'), 'PreToolUse'], { cwd: f.cwd, env: { HOME: f.home, XDG_CONFIG_HOME: f.home, XDG_CACHE_HOME: f.home, PATH: '/usr/bin:/bin' }, encoding: 'utf8' });
  assert.equal(result.status, 1);
  assert.equal(result.stdout, '');
  assert.match(result.stderr, /unsupported event/);
});
