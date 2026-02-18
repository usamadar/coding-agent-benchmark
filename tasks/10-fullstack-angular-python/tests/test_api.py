import sys
from pathlib import Path
_base = Path(__file__).parent.parent
sys.path.insert(0, str(_base))
if (_base / "repo").exists():
    sys.path.insert(0, str(_base / "repo"))

from api import TodoAPI


def _make_api_with_todos():
    api = TodoAPI()
    api.add_todo("Buy groceries")
    api.add_todo("Write tests")
    api.add_todo("Deploy app")
    return api


def test_list_todos():
    api = _make_api_with_todos()
    assert len(api.list_todos()) == 3


def test_add_todo():
    api = TodoAPI()
    todo = api.add_todo("New task")
    assert todo["title"] == "New task"
    assert todo["completed"] is False
    assert todo["id"] == 1


def test_update_todo_title():
    api = _make_api_with_todos()
    result = api.update_todo(1, {"title": "Buy organic groceries"})
    assert result is not None
    assert result["title"] == "Buy organic groceries"
    assert result["completed"] is False


def test_update_todo_completed():
    api = _make_api_with_todos()
    result = api.update_todo(2, {"completed": True})
    assert result["completed"] is True
    assert result["title"] == "Write tests"


def test_update_todo_not_found():
    api = _make_api_with_todos()
    result = api.update_todo(999, {"title": "Nope"})
    assert result is None


def test_delete_todo():
    api = _make_api_with_todos()
    assert api.delete_todo(1) is True
    assert len(api.list_todos()) == 2


def test_delete_todo_not_found():
    api = _make_api_with_todos()
    assert api.delete_todo(999) is False


def test_get_stats_all_pending():
    api = _make_api_with_todos()
    stats = api.get_stats()
    assert stats["total"] == 3
    assert stats["completed"] == 0
    assert stats["pending"] == 3


def test_get_stats_mixed():
    api = _make_api_with_todos()
    api.update_todo(1, {"completed": True})
    api.update_todo(2, {"completed": True})
    stats = api.get_stats()
    assert stats["total"] == 3
    assert stats["completed"] == 2
    assert stats["pending"] == 1


def test_get_stats_empty():
    api = TodoAPI()
    stats = api.get_stats()
    assert stats["total"] == 0
    assert stats["completed"] == 0
    assert stats["pending"] == 0
