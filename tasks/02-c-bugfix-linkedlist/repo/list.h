#ifndef LIST_H
#define LIST_H

typedef struct Node {
    int data;
    struct Node *next;
} Node;

/* Insert a new node with the given value at the head of the list. */
void list_insert(Node **head, int value);

/* Remove the first node with the given value. Returns 1 if found, 0 otherwise. */
int list_remove(Node **head, int value);

/* Find a node with the given value. Returns pointer to node or NULL. */
Node *list_find(Node *head, int value);

/* Free all nodes in the list. */
void list_free(Node **head);

/* Return the number of nodes in the list. */
int list_length(Node *head);

#endif
