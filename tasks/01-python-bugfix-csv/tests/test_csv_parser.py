import sys
from pathlib import Path
_base = Path(__file__).parent.parent
sys.path.insert(0, str(_base))
# Also check repo/ subdir for local testing outside the benchmark workspace
if (_base / "repo").exists():
    sys.path.insert(0, str(_base / "repo"))

from csv_parser import parse_csv


def test_simple_row():
    assert parse_csv("a,b,c") == [["a", "b", "c"]]


def test_multiple_rows():
    assert parse_csv("a,b\nc,d") == [["a", "b"], ["c", "d"]]


def test_quoted_field():
    assert parse_csv('"hello","world"') == [["hello", "world"]]


def test_quoted_field_with_comma():
    assert parse_csv('"hello, world",foo') == [["hello, world", "foo"]]


def test_quoted_field_with_newline():
    assert parse_csv('"line1\nline2",foo') == [["line1\nline2", "foo"]]


def test_escaped_quote():
    assert parse_csv('"he said ""hi""",bar') == [['he said "hi"', "bar"]]


def test_empty_fields():
    assert parse_csv("a,,c") == [["a", "", "c"]]


def test_mixed_rows_with_newlines_in_quotes():
    text = 'name,bio\nAlice,"likes\ncats"\nBob,dogs'
    assert parse_csv(text) == [
        ["name", "bio"],
        ["Alice", "likes\ncats"],
        ["Bob", "dogs"],
    ]
