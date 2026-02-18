import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BenchmarkTask:
    name: str
    prompt: str
    language: str
    test_languages: list[str]
    category: str
    timeout_seconds: int
    repo_dir: Path
    tests_dir: Path
    task_dir: Path


def load_tasks(tasks_dir: Path) -> list[BenchmarkTask]:
    tasks = []
    for child in sorted(tasks_dir.iterdir()):
        if not child.is_dir():
            continue
        metadata_path = child / "metadata.json"
        prompt_path = child / "prompt.md"
        if not metadata_path.exists() or not prompt_path.exists():
            continue

        with open(metadata_path) as f:
            meta = json.load(f)

        test_languages = meta.get("test_languages")
        if test_languages is None:
            test_languages = [meta["language"]]
        elif isinstance(test_languages, str):
            test_languages = [test_languages]

        tasks.append(BenchmarkTask(
            name=child.name,
            prompt=prompt_path.read_text(),
            language=meta["language"],
            test_languages=test_languages,
            category=meta["category"],
            timeout_seconds=meta.get("timeout_seconds", 300),
            repo_dir=child / "repo",
            tests_dir=child / "tests",
            task_dir=child,
        ))
    return tasks
