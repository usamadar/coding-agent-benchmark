const { TodoService } = require('../todo_service');

function createMockApi() {
    const todos = [
        { id: 1, title: 'Task 1', completed: false },
        { id: 2, title: 'Task 2', completed: true },
    ];
    return {
        listTodos: () => [...todos],
        addTodo: (title) => ({ id: 3, title, completed: false }),
        updateTodo: (id, updates) => {
            const todo = todos.find(t => t.id === id);
            if (!todo) return null;
            return { ...todo, ...updates };
        },
        deleteTodo: (id) => {
            const idx = todos.findIndex(t => t.id === id);
            return idx !== -1;
        },
        getStats: () => ({ total: 2, completed: 1, pending: 1 }),
    };
}

describe('TodoService', () => {
    test('listTodos delegates to api', () => {
        const service = new TodoService(createMockApi());
        const result = service.listTodos();
        expect(result).toHaveLength(2);
    });

    test('addTodo delegates to api', () => {
        const service = new TodoService(createMockApi());
        const result = service.addTodo('New task');
        expect(result.title).toBe('New task');
    });

    test('updateTodo delegates to api', () => {
        const service = new TodoService(createMockApi());
        const result = service.updateTodo(1, { title: 'Updated' });
        expect(result.title).toBe('Updated');
    });

    test('updateTodo returns null for missing id', () => {
        const service = new TodoService(createMockApi());
        const result = service.updateTodo(999, { title: 'Nope' });
        expect(result).toBeNull();
    });

    test('deleteTodo delegates to api', () => {
        const service = new TodoService(createMockApi());
        expect(service.deleteTodo(1)).toBe(true);
    });

    test('deleteTodo returns false for missing id', () => {
        const service = new TodoService(createMockApi());
        expect(service.deleteTodo(999)).toBe(false);
    });

    test('getStats delegates to api', () => {
        const service = new TodoService(createMockApi());
        const stats = service.getStats();
        expect(stats.total).toBe(2);
        expect(stats.completed).toBe(1);
        expect(stats.pending).toBe(1);
    });
});
