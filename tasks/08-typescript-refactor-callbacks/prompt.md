# Task: Convert Callbacks to Async/Await

The file `file_processor.js` contains functions that use nested callbacks to process files. Refactor all functions to use async/await instead.

Requirements:
1. Convert `readFile`, `parseData`, `transformData`, `writeFile`, and `processFile` from callback-based to async/await
2. Each function should return a Promise (be an async function)
3. `processFile(inputPath, outputPath)` should chain the operations: read → parse → transform → write
4. Error handling: if any step fails, the error should propagate (reject the promise)
5. Keep the same function names and export them

The simulated I/O functions (`_simulateRead` and `_simulateWrite`) are provided and should NOT be changed — they simulate filesystem operations with delays.
