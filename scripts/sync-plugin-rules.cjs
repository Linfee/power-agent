'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { START, END, getDefaults, removeDefaults } = require('../hooks/defaults.cjs');

const root = path.resolve(__dirname, '..');

const artifacts = [
  {
    relative: 'rules/minimal-complete-change.mdc',
    header: '---\ndescription: Prefer the smallest complete change that meets the user goal.\nalwaysApply: true\n---\n\n',
  },
  { relative: 'rules/AGENTS.md', header: '' },
];

function main(args) {
  if (args.length > 1 || (args.length && args[0] !== '--check')) {
    throw new Error('Usage: node scripts/sync-plugin-rules.cjs [--check]');
  }
  const check = args[0] === '--check';
  const defaults = getDefaults().trimEnd() + '\n';
  for (const { relative, header } of artifacts) {
    const target = path.join(root, relative);
    const content = header + defaults;
    for (const segment of [path.dirname(target), target]) {
      try {
        if (fs.lstatSync(segment).isSymbolicLink()) throw new Error(`Refusing symbolic link: ${segment}`);
      } catch (error) {
        if (error.code !== 'ENOENT') throw error;
      }
    }
    let current;
    try {
      current = fs.readFileSync(target, 'utf8');
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
    }
    if (current === content) continue;
    if (check) throw new Error(`Missing or stale generated rule: ${relative}`);
    if (current !== undefined && (
      current.split(START).length !== 2 || current.split(END).length !== 2 ||
      removeDefaults(current) !== header + '\n'
    )) {
      throw new Error(`Refusing to overwrite unowned content or metadata in ${relative}.`);
    }
    fs.mkdirSync(path.dirname(target), { recursive: true });
    const temporary = path.join(path.dirname(target), `.power-agent-${require('node:crypto').randomUUID()}.tmp`);
    try {
      fs.writeFileSync(temporary, content, { flag: 'wx' });
      fs.renameSync(temporary, target);
    } finally {
      try {
        fs.unlinkSync(temporary);
      } catch (error) {
        if (error.code !== 'ENOENT') throw error;
      }
    }
    console.log(`Generated ${relative}`);
  }
}

if (require.main === module) {
  try { main(process.argv.slice(2)); } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}

