# Task: Fix Memory Leak in Linked List

The files `list.h` and `list.c` implement a singly linked list with insert, remove, find, and free operations.

There is a bug in `list_remove`: when removing a node, the node's memory is not freed, causing a memory leak. Additionally, the `list_remove` function does not correctly update the head pointer when the first element is removed.

Fix both bugs:
1. Free the removed node's memory in `list_remove`.
2. Correctly handle removal of the head node by updating `*head`.

Do not change the function signatures in `list.h`.
