# Task: Fix Segfault in Multi-File C Project

This project implements a simple string hashmap (`hashmap.h`/`hashmap.c`) and uses it in `main.c` to count word frequencies.

The program segfaults when run. There are two bugs:

1. In `hashmap.c`, the `hashmap_get` function does not handle the case where the bucket's linked list has a NULL entry, causing a null pointer dereference.
2. In `hashmap.c`, the `hashmap_put` function does not correctly allocate memory for the key string (it assigns the pointer directly instead of copying), causing use-after-free when the original string is modified or freed.

Fix both bugs. Do not change the function signatures in `hashmap.h`.
Build and test with `make test`.
