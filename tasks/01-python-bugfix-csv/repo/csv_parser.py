def parse_csv(text: str) -> list[list[str]]:
    """Parse CSV text into a list of rows, each row a list of fields.

    Supports quoted fields, escaped quotes (""), and commas within quotes.
    """
    rows = []
    for line in text.split('\n'):
        row = []
        current_field = ""
        in_quotes = False
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                row.append(current_field)
                current_field = ""
            else:
                current_field += char
        row.append(current_field)
        rows.append(row)
    return rows
