#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "hashmap.h"

/* Declared in main.c */
extern void count_words(HashMap *map, const char *text);

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
    HashMap *map = hashmap_create();
    hashmap_put(map, "hello", 42);
    assert(hashmap_get(map, "hello") == 42);
    hashmap_destroy(map);
}

void test_contains() {
    HashMap *map = hashmap_create();
    hashmap_put(map, "key1", 10);
    assert(hashmap_contains(map, "key1") == 1);
    assert(hashmap_contains(map, "key2") == 0);
    hashmap_destroy(map);
}

void test_update_value() {
    HashMap *map = hashmap_create();
    hashmap_put(map, "key", 10);
    hashmap_put(map, "key", 20);
    assert(hashmap_get(map, "key") == 20);
    hashmap_destroy(map);
}

void test_multiple_keys() {
    HashMap *map = hashmap_create();
    hashmap_put(map, "a", 1);
    hashmap_put(map, "b", 2);
    hashmap_put(map, "c", 3);
    assert(hashmap_get(map, "a") == 1);
    assert(hashmap_get(map, "b") == 2);
    assert(hashmap_get(map, "c") == 3);
    hashmap_destroy(map);
}

void test_put_with_local_buffer() {
    /* This test exposes the strdup bug:
       keys are stored from a local buffer that gets overwritten */
    HashMap *map = hashmap_create();
    char buf[64];

    strcpy(buf, "first");
    hashmap_put(map, buf, 1);

    strcpy(buf, "second");
    hashmap_put(map, buf, 2);

    /* If key was not copied, "first" key now points to "second" */
    assert(hashmap_contains(map, "first") == 1);
    assert(hashmap_get(map, "first") == 1);
    assert(hashmap_contains(map, "second") == 1);
    assert(hashmap_get(map, "second") == 2);

    hashmap_destroy(map);
}

void test_count_words_basic() {
    HashMap *map = hashmap_create();
    count_words(map, "hello world hello");
    assert(hashmap_get(map, "hello") == 2);
    assert(hashmap_get(map, "world") == 1);
    hashmap_destroy(map);
}

void test_count_words_case_insensitive() {
    HashMap *map = hashmap_create();
    count_words(map, "Hello HELLO hello");
    assert(hashmap_get(map, "hello") == 3);
    hashmap_destroy(map);
}

void test_count_words_punctuation() {
    HashMap *map = hashmap_create();
    count_words(map, "the cat, the dog, and the fish.");
    assert(hashmap_get(map, "the") == 3);
    assert(hashmap_get(map, "cat") == 1);
    assert(hashmap_get(map, "and") == 1);
    hashmap_destroy(map);
}

int main(void) {
    printf("Running hashmap tests...\n");

    RUN_TEST(test_put_and_get);
    RUN_TEST(test_contains);
    RUN_TEST(test_update_value);
    RUN_TEST(test_multiple_keys);
    RUN_TEST(test_put_with_local_buffer);
    RUN_TEST(test_count_words_basic);
    RUN_TEST(test_count_words_case_insensitive);
    RUN_TEST(test_count_words_punctuation);

    printf("\nResults: %d/%d passed\n", passed, total);
    return (passed == total) ? 0 : 1;
}
