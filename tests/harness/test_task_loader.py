import json
import os
import tempfile
from pathlib import Path

from harness.task_loader import BenchmarkTask, load_tasks


def _make_task_dir(base: Path, name: str, language: str, category: str) -> Path:
    task_dir = base / name
    task_dir.mkdir()
    (task_dir / "prompt.md").write_text("Fix the bug in main.py")
    (task_dir / "metadata.json").write_text(json.dumps({
        "language": language,
        "category": category,
        "timeout_seconds": 120,
    }))
    repo = task_dir / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("print('hello')")
    tests = task_dir / "tests"
    tests.mkdir()
    (tests / "test_main.py").write_text("def test_one(): assert True")
    return task_dir


def test_load_tasks_finds_all_tasks(tmp_path):
    _make_task_dir(tmp_path, "01-python-bugfix", "python", "bugfix")
    _make_task_dir(tmp_path, "02-c-bugfix", "c", "bugfix")
    tasks = load_tasks(tmp_path)
    assert len(tasks) == 2
    assert tasks[0].name == "01-python-bugfix"
    assert tasks[1].name == "02-c-bugfix"


def test_task_fields_populated(tmp_path):
    _make_task_dir(tmp_path, "01-python-bugfix", "python", "bugfix")
    task = load_tasks(tmp_path)[0]
    assert task.prompt == "Fix the bug in main.py"
    assert task.language == "python"
    assert task.category == "bugfix"
    assert task.timeout_seconds == 120
    assert task.repo_dir.exists()
    assert task.tests_dir.exists()


def test_load_tasks_sorted_by_name(tmp_path):
    _make_task_dir(tmp_path, "03-ts-feature", "typescript", "feature")
    _make_task_dir(tmp_path, "01-python-bugfix", "python", "bugfix")
    tasks = load_tasks(tmp_path)
    assert tasks[0].name == "01-python-bugfix"
    assert tasks[1].name == "03-ts-feature"
