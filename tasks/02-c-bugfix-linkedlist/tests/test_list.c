#include <stdio.h>
#include <assert.h>
#include "list.h"

static int passed = 0;
static int failed = 0;

#define RUN_TEST(test_func) do { \
    printf("  Running %s... ", #test_func); \
    test_func(); \
    printf("[PASS]\n"); \
    passed++; \
} while(0)

void test_insert_and_length(void) {
    Node *head = NULL;
    list_insert(&head, 10);
    list_insert(&head, 20);
    list_insert(&head, 30);
    assert(list_length(head) == 3);
    list_free(&head);
}

void test_find(void) {
    Node *head = NULL;
    list_insert(&head, 10);
    list_insert(&head, 20);
    assert(list_find(head, 10) != NULL);
    assert(list_find(head, 20) != NULL);
    assert(list_find(head, 99) == NULL);
    list_free(&head);
}

void test_remove_middle(void) {
    Node *head = NULL;
    list_insert(&head, 10);
    list_insert(&head, 20);
    list_insert(&head, 30);
    /* List is: 30 -> 20 -> 10 */
    int result = list_remove(&head, 20);
    assert(result == 1);
    assert(list_length(head) == 2);
    assert(list_find(head, 20) == NULL);
    assert(list_find(head, 30) != NULL);
    assert(list_find(head, 10) != NULL);
    list_free(&head);
}

void test_remove_head(void) {
    Node *head = NULL;
    list_insert(&head, 10);
    list_insert(&head, 20);
    list_insert(&head, 30);
    /* List is: 30 -> 20 -> 10, remove head (30) */
    int result = list_remove(&head, 30);
    assert(result == 1);
    assert(list_length(head) == 2);
    assert(list_find(head, 30) == NULL);
    /* Head should now be 20 */
    assert(head->data == 20);
    list_free(&head);
}

void test_remove_tail(void) {
    Node *head = NULL;
    list_insert(&head, 10);
    list_insert(&head, 20);
    list_insert(&head, 30);
    /* List is: 30 -> 20 -> 10, remove tail (10) */
    int result = list_remove(&head, 10);
    assert(result == 1);
    assert(list_length(head) == 2);
    assert(list_find(head, 10) == NULL);
    list_free(&head);
}

void test_remove_nonexistent(void) {
    Node *head = NULL;
    list_insert(&head, 10);
    int result = list_remove(&head, 99);
    assert(result == 0);
    assert(list_length(head) == 1);
    list_free(&head);
}

void test_remove_only_element(void) {
    Node *head = NULL;
    list_insert(&head, 42);
    int result = list_remove(&head, 42);
    assert(result == 1);
    assert(list_length(head) == 0);
    assert(head == NULL);
}

void test_free_empty_list(void) {
    Node *head = NULL;
    list_free(&head);
    assert(head == NULL);
}

int main(void) {
    printf("Running linked list tests...\n");

    RUN_TEST(test_insert_and_length);
    RUN_TEST(test_find);
    RUN_TEST(test_remove_middle);
    RUN_TEST(test_remove_head);
    RUN_TEST(test_remove_tail);
    RUN_TEST(test_remove_nonexistent);
    RUN_TEST(test_remove_only_element);
    RUN_TEST(test_free_empty_list);

    printf("\nResults: %d/%d passed\n", passed, passed + failed);
    return failed > 0 ? 1 : 0;
}
