const { DataTable } = require('../table');

const SAMPLE_DATA = [
    { name: 'Alice Johnson', email: 'alice@example.com', role: 'admin' },
    { name: 'Bob Smith', email: 'bob@corp.com', role: 'user' },
    { name: 'Charlie Brown', email: 'charlie@example.com', role: 'user' },
    { name: 'Diana Prince', email: 'diana@corp.com', role: 'admin' },
    { name: 'Eve Adams', email: 'eve@example.com', role: 'moderator' },
];

describe('DataTable', () => {
    let table;

    beforeEach(() => {
        table = new DataTable([...SAMPLE_DATA.map(r => ({...r}))]);
    });

    test('getRows returns all rows', () => {
        expect(table.getRows()).toHaveLength(5);
    });

    test('filter by name returns matching rows', () => {
        const result = table.filter('alice');
        expect(result).toHaveLength(1);
        expect(result[0].name).toBe('Alice Johnson');
    });

    test('filter is case-insensitive', () => {
        const result = table.filter('ALICE');
        expect(result).toHaveLength(1);
        expect(result[0].name).toBe('Alice Johnson');
    });

    test('filter matches email field', () => {
        const result = table.filter('corp.com');
        expect(result).toHaveLength(2);
    });

    test('filter matches role field', () => {
        const result = table.filter('admin');
        expect(result).toHaveLength(2);
    });

    test('filter with empty query returns all rows', () => {
        expect(table.filter('')).toHaveLength(5);
        expect(table.filter(undefined)).toHaveLength(5);
    });

    test('filter does not modify original data', () => {
        table.filter('alice');
        expect(table.getRows()).toHaveLength(5);
    });

    test('filter with no matches returns empty array', () => {
        expect(table.filter('zzzzz')).toHaveLength(0);
    });

    test('sortBy name ascending', () => {
        const result = table.sortBy('name', 'asc');
        expect(result[0].name).toBe('Alice Johnson');
        expect(result[4].name).toBe('Eve Adams');
    });

    test('sortBy name descending', () => {
        const result = table.sortBy('name', 'desc');
        expect(result[0].name).toBe('Eve Adams');
        expect(result[4].name).toBe('Alice Johnson');
    });

    test('sortBy defaults to ascending', () => {
        const result = table.sortBy('name');
        expect(result[0].name).toBe('Alice Johnson');
    });

    test('sortBy does not modify original data', () => {
        const original = table.getRows();
        table.sortBy('name', 'desc');
        expect(table.getRows()).toEqual(original);
    });

    test('sortBy email', () => {
        const result = table.sortBy('email', 'asc');
        expect(result[0].email).toBe('alice@example.com');
    });
});
