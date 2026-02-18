#ifndef HASHMAP_H
#define HASHMAP_H

#define HASHMAP_SIZE 64

typedef struct Entry {
    char *key;
    int value;
    struct Entry *next;
} Entry;

typedef struct {
    Entry *buckets[HASHMAP_SIZE];
} HashMap;

HashMap *hashmap_create(void);
void hashmap_destroy(HashMap *map);
void hashmap_put(HashMap *map, const char *key, int value);
int hashmap_get(HashMap *map, const char *key);
int hashmap_contains(HashMap *map, const char *key);

#endif
