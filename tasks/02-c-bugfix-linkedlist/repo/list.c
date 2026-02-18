#include <stdlib.h>
#include "list.h"

void list_insert(Node **head, int value) {
    Node *new_node = malloc(sizeof(Node));
    new_node->data = value;
    new_node->next = *head;
    *head = new_node;
}

int list_remove(Node **head, int value) {
    Node *current = *head;
    Node *prev = NULL;

    while (current != NULL) {
        if (current->data == value) {
            if (prev != NULL) {
                prev->next = current->next;
            }
            /* BUG 1: Missing free(current) — memory leak */
            /* BUG 2: Missing head update when prev == NULL (removing head node) */
            return 1;
        }
        prev = current;
        current = current->next;
    }
    return 0;
}

Node *list_find(Node *head, int value) {
    Node *current = head;
    while (current != NULL) {
        if (current->data == value) {
            return current;
        }
        current = current->next;
    }
    return NULL;
}

void list_free(Node **head) {
    Node *current = *head;
    while (current != NULL) {
        Node *next = current->next;
        free(current);
        current = next;
    }
    *head = NULL;
}

int list_length(Node *head) {
    int count = 0;
    Node *current = head;
    while (current != NULL) {
        count++;
        current = current->next;
    }
    return count;
}
