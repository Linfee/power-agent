'use strict';

const fs = require('node:fs');
const path = require('node:path');

const START = '<!-- power-agent:defaults -->';
const END = '<!-- /power-agent:defaults -->';
const SOURCE = path.join(__dirname, '..', 'skills', 'codebase-design', 'references', 'minimal-complete-change.md');

function getDefaults() {
  const body = fs.readFileSync(SOURCE, 'utf8').trim();
  if (!body || body.includes(START) || body.includes(END)) {
    throw new Error('Power-Agent defaults source is empty or contains reserved markers. Reinstall or regenerate the package.');
  }
  return `${START}\n${body}\n${END}`;
}

// Validate the whole input before replacing anything: a truncated or nested
// managed block must not turn an update into deletion of the user's text.
function blocks(text) {
  if (typeof text !== 'string') throw new TypeError('Power-Agent prompt must be a string.');
  const ranges = [];
  let cursor = 0;
  while (cursor < text.length) {
    const start = text.indexOf(START, cursor);
    const end = text.indexOf(END, cursor);
    if (start === -1 && end === -1) break;
    if (start === -1 || (end !== -1 && end < start)) {
      throw new Error('Unbalanced Power-Agent defaults markers; preserve the file and repair the managed block first.');
    }
    const close = text.indexOf(END, start + START.length);
    const nested = text.indexOf(START, start + START.length);
    if (close === -1 || (nested !== -1 && nested < close)) {
      throw new Error('Unbalanced Power-Agent defaults markers; preserve the file and repair the managed block first.');
    }
    ranges.push([start, close + END.length]);
    cursor = close + END.length;
  }
  return ranges;
}

function removeDefaults(text) {
  const ranges = blocks(text);
  let result = '';
  let cursor = 0;
  for (const [start, end] of ranges) {
    result += text.slice(cursor, start);
    cursor = end;
  }
  return result + text.slice(cursor);
}

function mergeDefaults(text, defaults = getDefaults()) {
  const ranges = blocks(text);
  const supplied = blocks(defaults);
  if (supplied.length !== 1 || supplied[0][0] !== 0 || supplied[0][1] !== defaults.length) {
    throw new Error('Power-Agent defaults must be one complete managed block.');
  }
  if (!ranges.length) return text ? `${text}${text.endsWith('\n') ? '\n' : '\n\n'}${defaults}` : defaults;
  let result = '';
  let cursor = 0;
  for (let index = 0; index < ranges.length; index++) {
    const [start, end] = ranges[index];
    result += text.slice(cursor, start);
    if (index === 0) result += defaults;
    cursor = end;
  }
  return result + text.slice(cursor);
}

module.exports = { START, END, getDefaults, mergeDefaults, removeDefaults };
