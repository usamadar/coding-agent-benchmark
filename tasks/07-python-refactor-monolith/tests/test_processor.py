import sys
from pathlib import Path
_base = Path(__file__).parent.parent
sys.path.insert(0, str(_base))
if (_base / "repo").exists():
    sys.path.insert(0, str(_base / "repo"))

from processor import CsvReader, DataTransformer, StatsSummary

CSV_DATA = """name,department,salary
Alice,Engineering,95000
Bob,Marketing,65000
Charlie,Engineering,105000
Diana,Marketing,70000
Eve,Engineering,90000"""


def test_csv_reader_parse():
    reader = CsvReader(CSV_DATA)
    records = reader.parse()
    assert len(records) == 5
    assert records[0]["name"] == "Alice"
    assert records[0]["department"] == "Engineering"
    assert records[0]["salary"] == "95000"


def test_csv_reader_empty():
    reader = CsvReader("")
    assert reader.parse() == []


def test_transformer_filter_by():
    reader = CsvReader(CSV_DATA)
    records = reader.parse()
    transformer = DataTransformer(records)
    result = transformer.filter_by("department", "Engineering").to_list()
    assert len(result) == 3
    assert all(r["department"] == "Engineering" for r in result)


def test_transformer_filter_case_insensitive():
    reader = CsvReader(CSV_DATA)
    records = reader.parse()
    result = DataTransformer(records).filter_by("department", "engineering").to_list()
    assert len(result) == 3


def test_transformer_add_field():
    reader = CsvReader(CSV_DATA)
    records = reader.parse()
    transformer = DataTransformer(records)
    result = transformer.add_field("salary_k", lambda r: float(r["salary"]) / 1000).to_list()
    assert result[0]["salary_k"] == 95.0


def test_transformer_chaining():
    reader = CsvReader(CSV_DATA)
    records = reader.parse()
    result = (DataTransformer(records)
              .filter_by("department", "Engineering")
              .add_field("bonus", lambda r: float(r["salary"]) * 0.1)
              .to_list())
    assert len(result) == 3
    assert result[0]["bonus"] == 9500.0


def test_transformer_does_not_modify_original():
    reader = CsvReader(CSV_DATA)
    records = reader.parse()
    original_len = len(records)
    DataTransformer(records).filter_by("department", "Engineering")
    assert len(records) == original_len


def test_stats_count():
    reader = CsvReader(CSV_DATA)
    records = reader.parse()
    stats = StatsSummary(records)
    assert stats.count() == 5


def test_stats_sum_field():
    reader = CsvReader(CSV_DATA)
    records = reader.parse()
    stats = StatsSummary(records)
    assert stats.sum_field("salary") == 425000.0


def test_stats_avg_field():
    reader = CsvReader(CSV_DATA)
    records = reader.parse()
    stats = StatsSummary(records)
    assert stats.avg_field("salary") == 85000.0


def test_stats_avg_empty():
    stats = StatsSummary([])
    assert stats.avg_field("salary") == 0.0


def test_stats_group_count():
    reader = CsvReader(CSV_DATA)
    records = reader.parse()
    stats = StatsSummary(records)
    groups = stats.group_count("department")
    assert groups == {"Engineering": 3, "Marketing": 2}
