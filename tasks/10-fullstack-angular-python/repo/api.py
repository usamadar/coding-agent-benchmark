"""Todo API module."""


class TodoAPI:
    def __init__(self):
        self.todos = []
        self._next_id = 1

    def list_todos(self):
        return list(self.todos)

    def add_todo(self, title):
        todo = {
            "id": self._next_id,
            "title": title,
            "completed": False,
        }
        self._next_id += 1
        self.todos.append(todo)
        return todo

    # TODO: Add update_todo(todo_id, updates) method

    # TODO: Add delete_todo(todo_id) method

    # TODO: Add get_stats() method
