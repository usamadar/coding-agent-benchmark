#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include "hashmap.h"

/* Count word frequencies in a string */
void count_words(HashMap *map, const char *text) {
    char word[256];
    int wi = 0;

    for (int i = 0; text[i] != '\0'; i++) {
        if (isalpha(text[i])) {
            word[wi++] = tolower(text[i]);
        } else if (wi > 0) {
            word[wi] = '\0';
            /* This uses a stack-allocated buffer — the strdup bug in hashmap_put
               causes the key to point to this buffer, which gets overwritten */
            int count = hashmap_get(map, word);
            hashmap_put(map, word, count + 1);
            wi = 0;
        }
    }
    if (wi > 0) {
        word[wi] = '\0';
        int count = hashmap_get(map, word);
        hashmap_put(map, word, count + 1);
    }
}
