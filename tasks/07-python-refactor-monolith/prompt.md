# Task: Refactor Monolithic Script into Modules

The file `processor.py` is a monolithic script that handles data processing: reading CSV data, transforming records, filtering, and generating summary statistics.

Refactor it into three separate classes in the SAME file (`processor.py`):

1. **`CsvReader`** class:
   - `__init__(self, text: str)` — takes raw CSV text
   - `parse(self) -> list[dict]` — parses CSV text into a list of dicts using the first row as headers

2. **`DataTransformer`** class:
   - `__init__(self, records: list[dict])` — takes a list of dicts
   - `filter_by(self, field: str, value: str) -> 'DataTransformer'` — returns a new DataTransformer with filtered records (case-insensitive match)
   - `add_field(self, name: str, fn)` — adds a computed field to each record using fn(record), returns self for chaining
   - `to_list(self) -> list[dict]` — returns the records as a list

3. **`StatsSummary`** class:
   - `__init__(self, records: list[dict])` — takes a list of dicts
   - `count(self) -> int` — number of records
   - `sum_field(self, field: str) -> float` — sum of a numeric field
   - `avg_field(self, field: str) -> float` — average of a numeric field
   - `group_count(self, field: str) -> dict` — count of records grouped by field value

Keep all three classes in `processor.py`. Remove the existing procedural functions.
