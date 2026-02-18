"""Data processor - monolithic version.

This module processes CSV data with various transformations and statistics.
Refactor into CsvReader, DataTransformer, and StatsSummary classes.
"""


def read_csv(text):
    """Parse CSV text into list of dicts using first row as headers."""
    lines = text.strip().split('\n')
    if not lines:
        return []
    headers = [h.strip() for h in lines[0].split(',')]
    records = []
    for line in lines[1:]:
        values = [v.strip() for v in line.split(',')]
        record = dict(zip(headers, values))
        records.append(record)
    return records


def filter_records(records, field, value):
    """Filter records where field matches value (case-insensitive)."""
    return [r for r in records if r.get(field, '').lower() == value.lower()]


def add_computed_field(records, name, fn):
    """Add a computed field to each record."""
    for r in records:
        r[name] = fn(r)
    return records


def count_records(records):
    return len(records)


def sum_field(records, field):
    return sum(float(r.get(field, 0)) for r in records)


def avg_field(records, field):
    if not records:
        return 0.0
    return sum_field(records, field) / len(records)


def group_count(records, field):
    groups = {}
    for r in records:
        key = r.get(field, '')
        groups[key] = groups.get(key, 0) + 1
    return groups


def process_data(csv_text, filter_field=None, filter_value=None):
    """Main processing pipeline."""
    records = read_csv(csv_text)
    if filter_field and filter_value:
        records = filter_records(records, filter_field, filter_value)
    return {
        'records': records,
        'count': count_records(records),
    }
