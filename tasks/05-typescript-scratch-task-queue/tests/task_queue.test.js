const { TaskQueue } = require('../task_queue');

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

describe('TaskQueue', () => {
    test('runs a single task', async () => {
        const queue = new TaskQueue();
        const result = await queue.add(async () => 42);
        expect(result).toBe(42);
    });

    test('respects concurrency limit', async () => {
        const queue = new TaskQueue({ concurrency: 2 });
        let maxRunning = 0;
        let currentRunning = 0;

        const makeTask = () => async () => {
            currentRunning++;
            maxRunning = Math.max(maxRunning, currentRunning);
            await delay(50);
            currentRunning--;
            return true;
        };

        await Promise.all([
            queue.add(makeTask()),
            queue.add(makeTask()),
            queue.add(makeTask()),
            queue.add(makeTask()),
        ]);

        expect(maxRunning).toBe(2);
    });

    test('higher priority tasks run first', async () => {
        const queue = new TaskQueue({ concurrency: 1 });
        const order = [];

        // Add a blocking task first
        const blocker = queue.add(async () => {
            await delay(50);
            order.push('blocker');
        });

        // These get queued while blocker runs
        const low = queue.add(async () => { order.push('low'); }, { priority: 1 });
        const high = queue.add(async () => { order.push('high'); }, { priority: 10 });
        const mid = queue.add(async () => { order.push('mid'); }, { priority: 5 });

        await Promise.all([blocker, low, high, mid]);
        expect(order).toEqual(['blocker', 'high', 'mid', 'low']);
    });

    test('retries failed tasks', async () => {
        const queue = new TaskQueue();
        let attempts = 0;

        const result = await queue.add(async () => {
            attempts++;
            if (attempts < 3) throw new Error('fail');
            return 'success';
        }, { retries: 2 });

        expect(result).toBe('success');
        expect(attempts).toBe(3);
    });

    test('rejects after exhausting retries', async () => {
        const queue = new TaskQueue();

        await expect(
            queue.add(async () => { throw new Error('always fails'); }, { retries: 2 })
        ).rejects.toThrow('always fails');
    });

    test('timeout rejects task', async () => {
        const queue = new TaskQueue();

        await expect(
            queue.add(async () => { await delay(500); return 'late'; }, { timeout: 50 })
        ).rejects.toThrow(/timeout/i);
    });

    test('size reflects pending tasks', async () => {
        const queue = new TaskQueue({ concurrency: 1 });

        // Block the queue
        let resolve;
        const blockPromise = new Promise(r => { resolve = r; });
        queue.add(() => blockPromise);

        queue.add(async () => 'a');
        queue.add(async () => 'b');

        // Give time for first task to start
        await delay(10);
        expect(queue.size).toBe(2);
        expect(queue.running).toBe(1);

        resolve();
        await queue.onEmpty();
    });

    test('onEmpty resolves when queue is drained', async () => {
        const queue = new TaskQueue({ concurrency: 2 });

        queue.add(async () => { await delay(30); });
        queue.add(async () => { await delay(30); });
        queue.add(async () => { await delay(30); });

        await queue.onEmpty();
        expect(queue.size).toBe(0);
        expect(queue.running).toBe(0);
    });
});
