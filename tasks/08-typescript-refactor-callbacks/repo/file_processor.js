// Simulated I/O - DO NOT MODIFY these two functions
function _simulateRead(path) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (path === 'error.txt') reject(new Error('File not found'));
            else resolve(`id,name,score\n1,Alice,85\n2,Bob,92\n3,Charlie,78`);
        }, 10);
    });
}

function _simulateWrite(path, content) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (path === 'readonly.txt') reject(new Error('Permission denied'));
            else resolve({ path, bytes: content.length });
        }, 10);
    });
}

// --- Refactor the functions below from callbacks to async/await ---

function readFile(path, callback) {
    _simulateRead(path).then(
        data => callback(null, data),
        err => callback(err)
    );
}

function parseData(csvText, callback) {
    try {
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',');
        const records = lines.slice(1).map(line => {
            const values = line.split(',');
            const obj = {};
            headers.forEach((h, i) => { obj[h] = values[i]; });
            return obj;
        });
        callback(null, records);
    } catch (err) {
        callback(err);
    }
}

function transformData(records, callback) {
    try {
        const transformed = records.map(r => ({
            ...r,
            score: Number(r.score),
            grade: Number(r.score) >= 90 ? 'A' : Number(r.score) >= 80 ? 'B' : 'C',
        }));
        callback(null, transformed);
    } catch (err) {
        callback(err);
    }
}

function writeFile(path, data, callback) {
    const content = JSON.stringify(data, null, 2);
    _simulateWrite(path, content).then(
        result => callback(null, result),
        err => callback(err)
    );
}

function processFile(inputPath, outputPath, callback) {
    readFile(inputPath, (err, rawData) => {
        if (err) return callback(err);
        parseData(rawData, (err, records) => {
            if (err) return callback(err);
            transformData(records, (err, transformed) => {
                if (err) return callback(err);
                writeFile(outputPath, transformed, (err, result) => {
                    if (err) return callback(err);
                    callback(null, result);
                });
            });
        });
    });
}

module.exports = { readFile, parseData, transformData, writeFile, processFile, _simulateRead, _simulateWrite };
