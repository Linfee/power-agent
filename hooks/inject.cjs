#!/usr/bin/env node
'use strict';

// The event is fixed in the hook registration. Input can contain private prompt
// data and is unnecessary here, so never read stdin or depend on EOF.
const [event] = process.argv.slice(2);
const valid = ['SessionStart', 'SubagentStart'];

try {
  if (!valid.includes(event)) {
    throw new Error('unsupported event');
  }
  const { getDefaults } = require('./defaults.cjs');
  const additionalContext = getDefaults();
  process.stdout.write(`${JSON.stringify({ hookSpecificOutput: { hookEventName: event, additionalContext } })}\n`);
} catch (error) {
  // Exit 1 is a non-blocking hook failure, unlike the hosts' special exit 2.
  console.error(`Power-Agent defaults unavailable: ${error.message}`);
  process.exitCode = 1;
}
