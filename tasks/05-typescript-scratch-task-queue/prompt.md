# Task: Implement a Task Queue

Implement a `TaskQueue` class in `task_queue.js` that manages async tasks with priority, retry, and timeout support.

The class should be exported as `module.exports = { TaskQueue }`.

## Required API

### `new TaskQueue(options)`
- `options.concurrency` (number, default 1): max tasks running simultaneously

### `queue.add(taskFn, options)` → Promise
- `taskFn`: an async function (returns a Promise)
- `options.priority` (number, default 0): higher = runs first
- `options.retries` (number, default 0): how many times to retry on failure
- `options.timeout` (number, default 0): timeout in ms (0 = no timeout)
- Returns a Promise that resolves with the task result or rejects with the error

### `queue.size` (getter)
- Returns the number of pending (not yet started) tasks

### `queue.running` (getter)
- Returns the number of currently executing tasks

### `queue.onEmpty()` → Promise
- Returns a Promise that resolves when the queue has no pending or running tasks

## Behavior
- Tasks with higher priority numbers run first
- If a task fails and has retries remaining, it is re-queued (not counted as a new task)
- If a task exceeds its timeout, it should be rejected with an Error whose message includes "timeout"
- Concurrency must be respected: never run more than `concurrency` tasks at once
