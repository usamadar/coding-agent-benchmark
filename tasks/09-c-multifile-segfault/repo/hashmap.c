#include <stdlib.h>
#include <string.h>
#include "hashmap.h"

static unsigned int hash(const char *key) {
    unsigned int h = 0;
    while (*key) {
        h = h * 31 + (unsigned char)(*key);
        key++;
    }
    return h % HASHMAP_SIZE;
}

HashMap *hashmap_create(void) {
    HashMap *map = calloc(1, sizeof(HashMap));
    return map;
}

void hashmap_destroy(HashMap *map) {
    for (int i = 0; i < HASHMAP_SIZE; i++) {
        Entry *entry = map->buckets[i];
        while (entry) {
            Entry *next = entry->next;
            free(entry->key);
            free(entry);
            entry = next;
        }
    }
    free(map);
}

void hashmap_put(HashMap *map, const char *key, int value) {
    unsigned int idx = hash(key);
    Entry *entry = map->buckets[idx];

    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            entry->value = value;
            return;
        }
        entry = entry->next;
    }

    Entry *new_entry = malloc(sizeof(Entry));
    new_entry->key = (char *)key;  /* BUG: should be strdup(key) */
    new_entry->value = value;
    new_entry->next = map->buckets[idx];
    map->buckets[idx] = new_entry;
}

int hashmap_get(HashMap *map, const char *key) {
    unsigned int idx = hash(key);
    Entry *entry = map->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            return entry->value;
        }
        entry = entry->next;
    }
    return 0;
}

int hashmap_contains(HashMap *map, const char *key) {
    unsigned int idx = hash(key);
    Entry *entry = map->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            return 1;
        }
        entry = entry->next;
    }
    return 0;
}
