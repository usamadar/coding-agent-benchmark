# Task: Add Search/Filter to Data Table

The file `table.js` contains a `DataTable` class that stores rows of user data (objects with `name`, `email`, and `role` fields) and has a `getRows()` method that returns all rows.

Add a `filter(query)` method that:
1. Takes a search string `query`
2. Returns only the rows where ANY field (name, email, or role) contains the query string (case-insensitive)
3. If the query is empty or undefined, return all rows
4. The original data should not be modified

Also add a `sortBy(field, order)` method that:
1. Takes a field name (string) and order ("asc" or "desc")
2. Returns the rows sorted by that field alphabetically
3. Default order is "asc" if not specified
4. Should not modify the original data
