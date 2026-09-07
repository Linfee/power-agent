// Polling fallback for a project without suitable event subscriptions or framework waits.
// Replace these type imports with the project's own event and manager types.
// getEvents must be a synchronous, low-cost read; polling cannot interrupt a blocking getter.

import type { ThreadManager } from '~/threads/thread-manager';
import type { LaceEvent, LaceEventType } from '~/threads/types';

export interface PollingOptions {
  timeoutMs: number;
  pollIntervalMs: number;
}

function getDeadline({ timeoutMs, pollIntervalMs }: PollingOptions): number {
  if (!Number.isFinite(timeoutMs) || timeoutMs < 0 ||
      !Number.isFinite(pollIntervalMs) || pollIntervalMs <= 0) {
    throw new RangeError('Use a finite nonnegative timeout and a finite positive poll interval');
  }
  return performance.now() + timeoutMs;
}

/**
 * Wait for a specific event type in the supplied thread's history.
 * Use waitForEventMatch with an operation identifier when old events could match.
 * Choose the timeout and polling interval from the task's budget and query cost.
 */
export async function waitForEvent(
  threadManager: ThreadManager,
  threadId: string,
  eventType: LaceEventType,
  options: PollingOptions
): Promise<LaceEvent> {
  const deadline = getDeadline(options);

  while (true) {
    const event = threadManager.getEvents(threadId).find((e) => e.type === eventType);
    if (event) return event;

    const remainingMs = deadline - performance.now();
    if (remainingMs <= 0) {
      throw new Error(`Timeout waiting for ${eventType} event after ${options.timeoutMs}ms`);
    }
    await new Promise(resolve =>
      setTimeout(resolve, Math.min(options.pollIntervalMs, remainingMs))
    );
  }
}

/**
 * Wait for the supplied thread history to contain at least count matching events.
 * The caller must account for pre-existing events or use an isolated thread.
 */
export async function waitForEventCount(
  threadManager: ThreadManager,
  threadId: string,
  eventType: LaceEventType,
  count: number,
  options: PollingOptions
): Promise<LaceEvent[]> {
  const deadline = getDeadline(options);

  while (true) {
    const matchingEvents = threadManager.getEvents(threadId).filter((e) => e.type === eventType);
    if (matchingEvents.length >= count) return matchingEvents;

    const remainingMs = deadline - performance.now();
    if (remainingMs <= 0) {
      throw new Error(
        `Timeout waiting for ${count} ${eventType} events after ${options.timeoutMs}ms (got ${matchingEvents.length})`
      );
    }
    await new Promise(resolve =>
      setTimeout(resolve, Math.min(options.pollIntervalMs, remainingMs))
    );
  }
}

/** Wait for an event whose type and data satisfy the operation's contract. */
export async function waitForEventMatch(
  threadManager: ThreadManager,
  threadId: string,
  predicate: (event: LaceEvent) => boolean,
  description: string,
  options: PollingOptions
): Promise<LaceEvent> {
  const deadline = getDeadline(options);

  while (true) {
    const event = threadManager.getEvents(threadId).find(predicate);
    if (event) return event;

    const remainingMs = deadline - performance.now();
    if (remainingMs <= 0) {
      throw new Error(`Timeout waiting for ${description} after ${options.timeoutMs}ms`);
    }
    await new Promise(resolve =>
      setTimeout(resolve, Math.min(options.pollIntervalMs, remainingMs))
    );
  }
}

// Example for a new isolated thread with no earlier tool events:
// const waitOptions = { timeoutMs, pollIntervalMs }; // Values chosen for this test.
// const messagePromise = agent.sendMessage('Execute tools');
// await waitForEventCount(threadManager, threadId, 'TOOL_CALL', 2, waitOptions);
// agent.abort();
// await messagePromise;
// const results = await waitForEventCount(threadManager, threadId, 'TOOL_RESULT', 2, waitOptions);
// expect(results).toHaveLength(2);
// Further assertions must check the expected result and abort semantics.
// This waits for observed conditions; it does not establish the absence of all races.
