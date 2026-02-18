const { readFile, parseData, transformData, writeFile, processFile } = require('../file_processor');

describe('readFile (async)', () => {
    test('returns file content as a string', async () => {
        const result = await readFile('test.txt');
        expect(typeof result).toBe('string');
        expect(result).toContain('id,name,score');
    });

    test('rejects on error path', async () => {
        await expect(readFile('error.txt')).rejects.toThrow('File not found');
    });
});

describe('parseData (async)', () => {
    test('parses CSV into array of objects', async () => {
        const csv = 'id,name,score\n1,Alice,85\n2,Bob,92';
        const result = await parseData(csv);
        expect(result).toHaveLength(2);
        expect(result[0].name).toBe('Alice');
        expect(result[0].score).toBe('85');
    });
});

describe('transformData (async)', () => {
    test('adds numeric score and grade', async () => {
        const records = [
            { id: '1', name: 'Alice', score: '85' },
            { id: '2', name: 'Bob', score: '92' },
            { id: '3', name: 'Charlie', score: '78' },
        ];
        const result = await transformData(records);
        expect(result[0].score).toBe(85);
        expect(result[0].grade).toBe('B');
        expect(result[1].grade).toBe('A');
        expect(result[2].grade).toBe('C');
    });
});

describe('writeFile (async)', () => {
    test('returns write result', async () => {
        const result = await writeFile('output.json', [{ a: 1 }]);
        expect(result.path).toBe('output.json');
        expect(result.bytes).toBeGreaterThan(0);
    });

    test('rejects on readonly path', async () => {
        await expect(writeFile('readonly.txt', [])).rejects.toThrow('Permission denied');
    });
});

describe('processFile (async)', () => {
    test('processes end-to-end', async () => {
        const result = await processFile('input.csv', 'output.json');
        expect(result.path).toBe('output.json');
        expect(result.bytes).toBeGreaterThan(0);
    });

    test('rejects on read error', async () => {
        await expect(processFile('error.txt', 'output.json')).rejects.toThrow('File not found');
    });

    test('rejects on write error', async () => {
        await expect(processFile('input.csv', 'readonly.txt')).rejects.toThrow('Permission denied');
    });

    test('all functions return promises (not use callbacks)', async () => {
        // Verify that calling without a callback returns a promise
        expect(readFile('test.txt')).toBeInstanceOf(Promise);
        expect(parseData('a,b\n1,2')).toBeInstanceOf(Promise);
        expect(transformData([{score: '90'}])).toBeInstanceOf(Promise);
        expect(writeFile('out.json', [])).toBeInstanceOf(Promise);
        expect(processFile('in.csv', 'out.json')).toBeInstanceOf(Promise);
    });
});
