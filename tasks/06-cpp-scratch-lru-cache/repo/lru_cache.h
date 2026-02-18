#ifndef LRU_CACHE_H
#define LRU_CACHE_H

class LRUCache {
public:
    explicit LRUCache(int capacity);
    ~LRUCache();

    int get(int key);
    void put(int key, int value);
    int size() const;
    bool contains(int key) const;

private:
    int capacity_;
    // TODO: add data structures
};

#endif
