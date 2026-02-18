class DataTable {
    constructor(rows) {
        this.rows = rows || [];
    }

    addRow(row) {
        this.rows.push(row);
    }

    getRows() {
        return [...this.rows];
    }

    getRowCount() {
        return this.rows.length;
    }

    // TODO: Add filter(query) method

    // TODO: Add sortBy(field, order) method
}

module.exports = { DataTable };
