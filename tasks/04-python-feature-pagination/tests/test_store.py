import sys
from pathlib import Path
_base = Path(__file__).parent.parent
sys.path.insert(0, str(_base))
if (_base / "repo").exists():
    sys.path.insert(0, str(_base / "repo"))

from store import ItemStore


def _make_store(n=25):
    items = [{"id": i, "name": f"Item {i:03d}", "price": i * 10.0} for i in range(1, n + 1)]
    return ItemStore(items)


def test_get_page_defaults():
    store = _make_store(25)
    result = store.get_page()
    assert len(result["items"]) == 10
    assert result["page"] == 1
    assert result["per_page"] == 10
    assert result["total_items"] == 25
    assert result["total_pages"] == 3
    assert result["has_next"] is True
    assert result["has_prev"] is False


def test_get_page_second_page():
    store = _make_store(25)
    result = store.get_page(page=2, per_page=10)
    assert len(result["items"]) == 10
    assert result["page"] == 2
    assert result["has_next"] is True
    assert result["has_prev"] is True


def test_get_page_last_page():
    store = _make_store(25)
    result = store.get_page(page=3, per_page=10)
    assert len(result["items"]) == 5
    assert result["has_next"] is False
    assert result["has_prev"] is True


def test_get_page_out_of_range():
    store = _make_store(25)
    result = store.get_page(page=99)
    assert len(result["items"]) == 0
    assert result["total_items"] == 25
    assert result["total_pages"] == 3


def test_get_page_per_page_one():
    store = _make_store(5)
    result = store.get_page(page=1, per_page=1)
    assert len(result["items"]) == 1
    assert result["total_pages"] == 5


def test_get_page_per_page_less_than_one():
    store = _make_store(5)
    result = store.get_page(page=1, per_page=0)
    assert result["per_page"] == 1
    assert len(result["items"]) == 1


def test_search_basic():
    store = _make_store(25)
    result = store.search("Item 00")
    assert result["total_items"] == 9  # Item 001 through Item 009
    assert len(result["items"]) == 9


def test_search_case_insensitive():
    store = _make_store(25)
    result = store.search("item 00")
    assert result["total_items"] == 9


def test_search_with_pagination():
    store = _make_store(25)
    result = store.search("Item", page=1, per_page=5)
    assert len(result["items"]) == 5
    assert result["total_items"] == 25
    assert result["total_pages"] == 5
    assert result["has_next"] is True


def test_search_no_results():
    store = _make_store(25)
    result = store.search("nonexistent")
    assert result["total_items"] == 0
    assert len(result["items"]) == 0
    assert result["total_pages"] == 0
