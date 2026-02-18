# Task: Add Pagination to Item Store

The file `store.py` contains an `ItemStore` class that manages a list of items (dictionaries with `id`, `name`, and `price` fields). Currently `get_items()` returns all items at once.

Add a `get_page(page, per_page)` method that:
1. Returns a dictionary with:
   - `items`: the subset of items for the requested page
   - `page`: current page number (1-indexed)
   - `per_page`: items per page
   - `total_items`: total number of items in the store
   - `total_pages`: total number of pages (rounded up)
   - `has_next`: boolean, whether there is a next page
   - `has_prev`: boolean, whether there is a previous page
2. Default values: page=1, per_page=10
3. If page is out of range (< 1 or > total_pages), return an empty items list but still include correct metadata
4. per_page must be at least 1; if less, treat as 1

Also add a `search(query, page, per_page)` method that:
1. Filters items where `name` contains the query (case-insensitive)
2. Returns the same paginated response format as `get_page`
3. Defaults: page=1, per_page=10
