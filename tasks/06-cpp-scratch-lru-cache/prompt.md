# Task: Implement an LRU Cache

Implement the `LRUCache` class in `lru_cache.cpp` to match the interface defined in `lru_cache.h`.

The cache should:
1. Store key-value pairs (both int) with a fixed capacity
2. `get(key)` returns the value if the key exists, or -1 if not found. Accessing a key makes it the most recently used.
3. `put(key, value)` inserts or updates a key-value pair. If the cache is at capacity, evict the least recently used item first.
4. Both `get` and `put` should run in O(1) average time.
5. `size()` returns the current number of items in the cache.
6. `contains(key)` returns true if the key exists (does NOT count as an access for LRU purposes).

Build with `make` and run tests with `make test`.
