#include <stdio.h>
#include <assert.h>
#include "lru_cache.h"

static int passed = 0;
static int total = 0;

#define RUN_TEST(test_func) do { \
    total++; \
    printf("  Running %s... ", #test_func); \
    test_func(); \
    printf("[PASS]\n"); \
    passed++; \
} while(0)

void test_put_and_get() {
    LRUCache cache(3);
    cache.put(1, 100);
    cache.put(2, 200);
    assert(cache.get(1) == 100);
    assert(cache.get(2) == 200);
}

void test_get_missing_key() {
    LRUCache cache(3);
    assert(cache.get(99) == -1);
}

void test_eviction() {
    LRUCache cache(2);
    cache.put(1, 100);
    cache.put(2, 200);
    cache.put(3, 300);  // evicts key 1
    assert(cache.get(1) == -1);
    assert(cache.get(2) == 200);
    assert(cache.get(3) == 300);
}

void test_access_updates_lru_order() {
    LRUCache cache(2);
    cache.put(1, 100);
    cache.put(2, 200);
    cache.get(1);       // makes key 1 most recently used
    cache.put(3, 300);  // should evict key 2, not key 1
    assert(cache.get(1) == 100);
    assert(cache.get(2) == -1);
    assert(cache.get(3) == 300);
}

void test_update_existing_key() {
    LRUCache cache(2);
    cache.put(1, 100);
    cache.put(1, 999);
    assert(cache.get(1) == 999);
    assert(cache.size() == 1);
}

void test_size() {
    LRUCache cache(3);
    assert(cache.size() == 0);
    cache.put(1, 100);
    assert(cache.size() == 1);
    cache.put(2, 200);
    assert(cache.size() == 2);
    cache.put(3, 300);
    assert(cache.size() == 3);
    cache.put(4, 400);  // evicts, size stays 3
    assert(cache.size() == 3);
}

void test_contains() {
    LRUCache cache(2);
    cache.put(1, 100);
    assert(cache.contains(1) == true);
    assert(cache.contains(2) == false);
}

void test_contains_does_not_update_lru() {
    LRUCache cache(2);
    cache.put(1, 100);
    cache.put(2, 200);
    cache.contains(1);   // should NOT count as access
    cache.put(3, 300);   // should evict key 1 (LRU), not key 2
    assert(cache.get(1) == -1);
    assert(cache.get(2) == 200);
    assert(cache.get(3) == 300);
}

void test_capacity_one() {
    LRUCache cache(1);
    cache.put(1, 100);
    assert(cache.get(1) == 100);
    cache.put(2, 200);
    assert(cache.get(1) == -1);
    assert(cache.get(2) == 200);
}

int main() {
    printf("Running LRU Cache tests...\n");

    RUN_TEST(test_put_and_get);
    RUN_TEST(test_get_missing_key);
    RUN_TEST(test_eviction);
    RUN_TEST(test_access_updates_lru_order);
    RUN_TEST(test_update_existing_key);
    RUN_TEST(test_size);
    RUN_TEST(test_contains);
    RUN_TEST(test_contains_does_not_update_lru);
    RUN_TEST(test_capacity_one);

    printf("\nResults: %d/%d passed\n", passed, total);
    return (passed == total) ? 0 : 1;
}
