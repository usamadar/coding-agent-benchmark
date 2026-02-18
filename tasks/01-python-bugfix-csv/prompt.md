# Task: Fix CSV Parser Bug

The file `csv_parser.py` contains a `parse_csv` function that parses CSV text into rows and fields.

There are two bugs:
1. Fields containing newlines inside quotes are split incorrectly — the parser breaks on newlines even when inside a quoted field.
2. Escaped quotes (`""` inside quoted fields) are not handled — they should produce a single `"` character.

Fix both bugs. The function signature should remain the same: `parse_csv(text: str) -> list[list[str]]`.
