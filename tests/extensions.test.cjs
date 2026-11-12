'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { pathToFileURL } = require('node:url');
const path = require('node:path');
const fs = require('node:fs');
const os = require('node:os');
const { START, END, getDefaults } = require('../hooks/defaults.cjs');

const load = (file) => import(pathToFileURL(path.join(__dirname, '..', file)).href);
const count = (text) => text.split(START).length - 1;

async function piHandler() {
  const { default: extension } = await load('pi-extension/index.mjs');
  const handlers = new Map();
  extension({ on: (name, handler) => handlers.set(name, handler) });
  return handlers.get('before_agent_start');
}

test('pi updates its structured section without disturbing others or replacing the prompt', async () => {
  const handler = await piHandler();
  const options = { sections: { other: 'other extension', power_agent: 'keep before\n' + START + '\nold\n' + END + '\nkeep after' } };
  const event = { systemPrompt: 'rendered prompt', systemPromptOptions: options };
  assert.equal(await handler(event, {}), undefined);
  assert.equal(options.sections.other, 'other extension');
  assert.equal(options.sections.power_agent, `keep before\n${getDefaults()}\nkeep after`);
  await handler(event, {});
  assert.equal(count(options.sections.power_agent), 1);
});

test('pi preserves a forced string prompt and updates rather than duplicating', async () => {
  const handler = await piHandler();
  const options = { forceSystemPrompt: 'forced', sections: { other: 'unchanged' } };
  const first = await handler({ systemPrompt: 'forced', systemPromptOptions: options }, {});
  assert.equal(first.systemPrompt, `forced\n\n${getDefaults()}`);
  const second = await handler({ systemPrompt: first.systemPrompt, systemPromptOptions: options }, {});
  assert.equal(second.systemPrompt, first.systemPrompt);
  assert.deepEqual(options.sections, { other: 'unchanged' });
});

test('OMP prompt arrays retain unknown parts and do not mutate the supplied array', async () => {
  const handler = await piHandler();
  const unknown = { kind: 'unknown', text: 'opaque' };
  const old = { type: 'text', text: `prefix ${START}\nold\n${END} suffix`, cache: 'preserve' };
  const event = { systemPrompt: ['first', unknown, old, `${START}\nduplicate\n${END} outside`] };
  const first = await handler(event, {});
  assert.notEqual(first.systemPrompt, event.systemPrompt);
  assert.deepEqual(event.systemPrompt, ['first', unknown, old, `${START}\nduplicate\n${END} outside`]);
  assert.equal(first.systemPrompt[1], unknown);
  assert.deepEqual(first.systemPrompt[2], { ...old, text: `prefix ${getDefaults()} suffix` });
  assert.equal(first.systemPrompt[3], ' outside');
  const next = await handler({ systemPrompt: first.systemPrompt }, {});
  assert.deepEqual(next, first);
});

test('pi refuses malformed markers without modifying the prompt', async () => {
  const handler = await piHandler();
  const event = { systemPrompt: ['first', `${START} missing end`] };
  const warnings = [];
  const result = await handler(event, { hasUI: true, ui: { notify: (message) => warnings.push(message) } });
  assert.equal(result, undefined);
  assert.deepEqual(event.systemPrompt, ['first', `${START} missing end`]);
  assert.match(warnings[0], /Power-Agent defaults unavailable/);
});

test('missing canonical source reports failure and leaves the prompt alone', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'power-agent-extensions-'));
  const warnings = [];
  try {
    for (const file of ['hooks/defaults.cjs', 'pi-extension/index.mjs']) {
      const destination = path.join(root, file);
      fs.mkdirSync(path.dirname(destination), { recursive: true });
      fs.copyFileSync(path.join(__dirname, '..', file), destination);
    }
    const importCopy = (file) => import(pathToFileURL(path.join(root, file)).href);
    let pi;
    (await importCopy('pi-extension/index.mjs')).default({ on: (_name, handler) => { pi = handler; } });
    const options = { sections: { other: 'unchanged' } };
    await pi({ systemPrompt: 'unchanged', systemPromptOptions: options }, {
      hasUI: true, ui: { notify: (message) => warnings.push(message) },
    });
    assert.deepEqual(options.sections, { other: 'unchanged' });
    assert.equal(warnings.length, 1);
    assert.match(warnings[0], /Power-Agent defaults unavailable/);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
