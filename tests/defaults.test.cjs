'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');
const { START, END, mergeDefaults, removeDefaults } = require('../hooks/defaults.cjs');
const managed = (text) => `${START}\n${text}\n${END}`;

test('updating owned defaults preserves all surrounding instructions and converges', () => {
  const before = `用户的安全策略\n\n${managed('old')}\n\n# Project policy\nKeep this exact trailing whitespace.  \n`;
  const next = managed('new');
  const expected = `用户的安全策略\n\n${next}\n\n# Project policy\nKeep this exact trailing whitespace.  \n`;
  assert.equal(mergeDefaults(before, next), expected);
  assert.equal(mergeDefaults(expected, next), expected);
  assert.equal(removeDefaults(expected), '用户的安全策略\n\n\n\n# Project policy\nKeep this exact trailing whitespace.  \n');
});

test('duplicate owned blocks collapse without dropping instructions between them', () => {
  const next = managed('current');
  const before = `${managed('old one')}\nKeep the middle.\n${managed('old two')}\nKeep the end.`;
  assert.equal(mergeDefaults(before, next), `${next}\nKeep the middle.\n\nKeep the end.`);
  assert.equal(removeDefaults(before), '\nKeep the middle.\n\nKeep the end.');
});

test('missing, reversed or nested markers refuse destructive updates', () => {
  for (const text of [START, END, `${END}\n${START}`, `${START}\n${START}\n${END}`, `${managed('valid')}\n${START}`]) {
    assert.throws(() => mergeDefaults(text, managed('new')), /Unbalanced/);
    assert.throws(() => removeDefaults(text), /Unbalanced/);
  }
});

test('invalid replacement cannot overwrite an existing owned block', () => {
  for (const replacement of ['unmarked', `${managed('one')}\n${managed('two')}`, `unowned\n${managed('one')}`]) {
    assert.throws(() => mergeDefaults(managed('old'), replacement), /one complete managed block/);
  }
});
