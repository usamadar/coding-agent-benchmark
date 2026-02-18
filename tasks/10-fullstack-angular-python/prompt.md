# Task: Add Full-Stack Todo Feature

This project has a Python API module (`api.py`) and a JavaScript frontend service (`todo_service.js`).

## Backend (api.py)
The `TodoAPI` class currently has `list_todos()` and `add_todo(title)` methods.

Add these methods:
1. `update_todo(todo_id, updates)` — Updates a todo by ID. `updates` is a dict that can contain `title` (str) and/or `completed` (bool). Returns the updated todo dict, or None if not found.
2. `delete_todo(todo_id)` — Deletes a todo by ID. Returns True if deleted, False if not found.
3. `get_stats()` — Returns a dict with `total`, `completed`, and `pending` counts.

## Frontend (todo_service.js)
The `TodoService` class wraps the API with methods that mirror the backend.

Add these methods:
1. `updateTodo(id, updates)` — Calls `api.updateTodo(id, updates)`, returns the updated todo or null
2. `deleteTodo(id)` — Calls `api.deleteTodo(id)`, returns boolean
3. `getStats()` — Calls `api.getStats()`, returns the stats object

The `api` object is injected in the constructor and has methods: `updateTodo(id, updates)`, `deleteTodo(id)`, `getStats()`.
