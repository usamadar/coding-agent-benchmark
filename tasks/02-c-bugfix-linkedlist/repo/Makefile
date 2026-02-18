CC = gcc
CFLAGS = -Wall -Wextra -g

all: test

test: tests/test_list.c list.c list.h
	$(CC) $(CFLAGS) -I. -o test_runner tests/test_list.c list.c
	./test_runner

clean:
	rm -f test_runner

.PHONY: all test clean
