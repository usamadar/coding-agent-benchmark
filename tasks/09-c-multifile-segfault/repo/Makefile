CC = gcc
CFLAGS = -Wall -Wextra -g

all: test

test: tests/test_hashmap.c hashmap.c main.c hashmap.h
	$(CC) $(CFLAGS) -I. -o test_runner tests/test_hashmap.c hashmap.c main.c
	./test_runner

clean:
	rm -f test_runner

.PHONY: all test clean
