class TodoService {
    constructor(api) {
        this.api = api;
    }

    listTodos() {
        return this.api.listTodos();
    }

    addTodo(title) {
        return this.api.addTodo(title);
    }

    // TODO: Add updateTodo(id, updates)

    // TODO: Add deleteTodo(id)

    // TODO: Add getStats()
}

module.exports = { TodoService };
