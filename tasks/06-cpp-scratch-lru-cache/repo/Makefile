CXX = g++
CXXFLAGS = -Wall -Wextra -std=c++17 -g

all: test

test: tests/test_lru_cache.cpp lru_cache.cpp lru_cache.h
	$(CXX) $(CXXFLAGS) -I. -o test_runner tests/test_lru_cache.cpp lru_cache.cpp
	./test_runner

clean:
	rm -f test_runner

.PHONY: all test clean
