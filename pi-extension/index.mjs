import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { START, END, getDefaults, mergeDefaults, removeDefaults } = require('../hooks/defaults.cjs');

function mergeParts(parts, defaults) {
  let found = false;
  const result = parts.map((part) => {
    const text = typeof part === 'string' ? part : part?.type === 'text' && typeof part.text === 'string' ? part.text : null;
    if (text === null || (!text.includes(START) && !text.includes(END))) return part;
    const updated = found ? removeDefaults(text) : mergeDefaults(text, defaults);
    found = true;
    return typeof part === 'string' ? updated : { ...part, text: updated };
  });
  if (!found) result.push(defaults);
  return result;
}

export default function powerAgent(pi) {
  pi.on('before_agent_start', async (event, ctx) => {
    try {
      const defaults = getDefaults();
      const options = event?.systemPromptOptions;
      // A forced prompt supersedes sections in Pi; do not silently edit an ignored section.
      if (options?.sections && typeof options.sections === 'object' && options.forceSystemPrompt === undefined) {
        options.sections.power_agent = mergeDefaults(options.sections.power_agent ?? '', defaults);
        return;
      }
      if (Array.isArray(event?.systemPrompt)) {
        return { systemPrompt: mergeParts(event.systemPrompt, defaults) };
      }
      if (typeof event?.systemPrompt === 'string') {
        return { systemPrompt: mergeDefaults(event.systemPrompt, defaults) };
      }
      throw new Error('Unsupported system prompt shape; defaults were not applied.');
    } catch (error) {
      const message = `Power-Agent defaults unavailable: ${error.message}`;
      if (ctx?.hasUI && ctx.ui?.notify) ctx.ui.notify(message, 'warning');
      else console.error(message);
    }
  });
}
