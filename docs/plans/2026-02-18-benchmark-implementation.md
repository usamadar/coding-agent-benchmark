# Coding Agent Benchmark — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a fully automated benchmark harness that runs 10 synthetic coding tasks through Claude Code and Codex CLI, then produces a comparison report.

**Architecture:** Python harness orchestrates task execution. Each task is a self-contained directory with source code, tests, prompt, and metadata. The harness copies repos to temp dirs, shells out to each agent CLI, runs test suites, collects metrics, and generates a report.

**Tech Stack:** Python 3.11+ (harness), pytest (Python task tests), Jest (TS task tests), Karma/Jasmine (Angular task tests), Make + assert.h (C/C++ task tests), PyYAML (config parsing)

---

### Task 1: Project Scaffolding & Config

**Files:**
- Create: `harness/__init__.py`
- Create: `harness/config.yaml`
- Create: `harness/config.py`
- Create: `requirements.txt`

**Step 1: Create requirements.txt**

```txt
pyyaml>=6.0
```

**Step 2: Create config.yaml**

```yaml
agents:
  claude-code:
    command: "claude"
    args:
      - "-p"
      - "{prompt}"
      - "--output-format"
      - "json"
      - "--allowedTools"
      - "Bash,Read,Edit,Write,Glob,Grep"
      - "--no-session-persistence"
    model: "claude-sonnet-4-6"
    timeout_seconds: 300

  codex:
    command: "codex"
    args:
      - "exec"
      - "{prompt}"
      - "--json"
      - "--ephemeral"
      - "-a"
      - "never"
      - "--sandbox"
      - "workspace-write"
    model: null  # uses default
    timeout_seconds: 300

test_runners:
  python:
    command: "python -m pytest {test_dir} -v --tb=short"
    pattern: "tests/"
  typescript:
    command: "npx jest {test_dir} --verbose"
    pattern: "tests/"
  angular:
    command: "npx ng test --watch=false --browsers=ChromeHeadless"
    pattern: "tests/"
  c:
    command: "cd {workspace} && make test"
    pattern: "tests/"
  cpp:
    command: "cd {workspace} && make test"
    pattern: "tests/"

results_dir: "results"
```

**Step 3: Create config.py**

```python
import yaml
from pathlib import Path
from dataclasses import dataclass


@dataclass
class AgentConfig:
    name: str
    command: str
    args: list[str]
    model: str | None
    timeout_seconds: int


@dataclass
class TestRunnerConfig:
    language: str
    command: str
    pattern: str


@dataclass
class BenchmarkConfig:
    agents: list[AgentConfig]
    test_runners: dict[str, TestRunnerConfig]
    results_dir: str


def load_config(path: Path = None) -> BenchmarkConfig:
    if path is None:
        path = Path(__file__).parent / "config.yaml"
    with open(path) as f:
        raw = yaml.safe_load(f)

    agents = []
    for name, cfg in raw["agents"].items():
        agents.append(AgentConfig(
            name=name,
            command=cfg["command"],
            args=cfg["args"],
            model=cfg.get("model"),
            timeout_seconds=cfg.get("timeout_seconds", 300),
        ))

    test_runners = {}
    for lang, cfg in raw["test_runners"].items():
        test_runners[lang] = TestRunnerConfig(
            language=lang,
            command=cfg["command"],
            pattern=cfg["pattern"],
        )

    return BenchmarkConfig(
        agents=agents,
        test_runners=test_runners,
        results_dir=raw.get("results_dir", "results"),
    )
```

**Step 4: Create harness/__init__.py**

Empty file.

**Step 5: Install dependencies and verify**

Run: `pip install -r requirements.txt`
Run: `python -c "from harness.config import load_config; c = load_config(); print(f'{len(c.agents)} agents, {len(c.test_runners)} runners')"`
Expected: `2 agents, 5 runners`

**Step 6: Commit**

```bash
git add harness/ requirements.txt
git commit -m "Add project scaffolding and config loader"
```

---

### Task 2: Task Loader

**Files:**
- Create: `harness/task_loader.py`
- Create: `tests/harness/test_task_loader.py`

**Step 1: Write the failing test**

```python
# tests/harness/test_task_loader.py
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
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/harness/test_task_loader.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'harness.task_loader'`

**Step 3: Write minimal implementation**

```python
# harness/task_loader.py
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BenchmarkTask:
    name: str
    prompt: str
    language: str
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

        tasks.append(BenchmarkTask(
            name=child.name,
            prompt=prompt_path.read_text(),
            language=meta["language"],
            category=meta["category"],
            timeout_seconds=meta.get("timeout_seconds", 300),
            repo_dir=child / "repo",
            tests_dir=child / "tests",
            task_dir=child,
        ))
    return tasks
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/harness/test_task_loader.py -v`
Expected: 3 passed

**Step 5: Commit**

```bash
git add harness/task_loader.py tests/
git commit -m "Add task loader with tests"
```

---

### Task 3: Agent Runner

**Files:**
- Create: `harness/runner.py`
- Create: `tests/harness/test_runner.py`

**Step 1: Write the failing test**

```python
# tests/harness/test_runner.py
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from harness.runner import AgentRunner, AgentResult
from harness.config import AgentConfig


def test_prepare_workspace_copies_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("code here")
    (repo / "subdir").mkdir()
    (repo / "subdir" / "util.py").write_text("util code")

    runner = AgentRunner(AgentConfig(
        name="test", command="echo", args=[], model=None, timeout_seconds=60
    ))
    workspace = runner.prepare_workspace(repo)
    assert (workspace / "main.py").exists()
    assert (workspace / "main.py").read_text() == "code here"
    assert (workspace / "subdir" / "util.py").exists()
    runner.cleanup()


def test_copy_tests_into_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_main.py").write_text("assert True")

    runner = AgentRunner(AgentConfig(
        name="test", command="echo", args=[], model=None, timeout_seconds=60
    ))
    runner.copy_tests(tests_dir, workspace)
    assert (workspace / "tests" / "test_main.py").exists()


def test_parse_claude_output_extracts_tokens():
    output = json.dumps({
        "result": "Done",
        "usage": {"input_tokens": 1000, "output_tokens": 500},
        "session_id": "abc123"
    })
    runner = AgentRunner(AgentConfig(
        name="claude-code", command="claude", args=[], model=None, timeout_seconds=60
    ))
    tokens = runner.parse_token_usage(output)
    assert tokens == {"input_tokens": 1000, "output_tokens": 500}


def test_parse_codex_output_extracts_tokens():
    # Codex emits JSONL, token info is in turn.completed events
    lines = [
        json.dumps({"type": "turn.completed", "usage": {"input_tokens": 2000, "output_tokens": 800}}),
        json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "Done"}}),
    ]
    output = "\n".join(lines)
    runner = AgentRunner(AgentConfig(
        name="codex", command="codex", args=[], model=None, timeout_seconds=60
    ))
    tokens = runner.parse_token_usage(output)
    assert tokens == {"input_tokens": 2000, "output_tokens": 800}
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/harness/test_runner.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# harness/runner.py
import json
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from harness.config import AgentConfig


@dataclass
class AgentResult:
    agent: str
    model: str | None
    wall_clock_seconds: float
    input_tokens: int
    output_tokens: int
    timed_out: bool
    error: str | None
    raw_output: str


class AgentRunner:
    def __init__(self, config: AgentConfig):
        self.config = config
        self._temp_dirs: list[Path] = []

    def prepare_workspace(self, repo_dir: Path) -> Path:
        temp_dir = Path(tempfile.mkdtemp(prefix=f"bench-{self.config.name}-"))
        shutil.copytree(repo_dir, temp_dir, dirs_exist_ok=True)
        self._temp_dirs.append(temp_dir)
        return temp_dir

    def copy_tests(self, tests_dir: Path, workspace: Path) -> None:
        dest = workspace / "tests"
        shutil.copytree(tests_dir, dest)

    def run(self, prompt: str, workspace: Path) -> AgentResult:
        args = [self.config.command]
        for arg in self.config.args:
            args.append(arg.replace("{prompt}", prompt))

        if self.config.name == "codex":
            args.extend(["-C", str(workspace)])

        start = time.monotonic()
        timed_out = False
        error = None
        raw_output = ""

        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                cwd=str(workspace) if self.config.name != "codex" else None,
            )
            raw_output = result.stdout
            if result.returncode != 0:
                error = result.stderr or f"Exit code {result.returncode}"
        except subprocess.TimeoutExpired:
            timed_out = True
            error = f"Timed out after {self.config.timeout_seconds}s"

        elapsed = time.monotonic() - start
        tokens = self.parse_token_usage(raw_output)

        return AgentResult(
            agent=self.config.name,
            model=self.config.model,
            wall_clock_seconds=round(elapsed, 2),
            input_tokens=tokens.get("input_tokens", 0),
            output_tokens=tokens.get("output_tokens", 0),
            timed_out=timed_out,
            error=error,
            raw_output=raw_output,
        )

    def parse_token_usage(self, output: str) -> dict:
        if not output.strip():
            return {"input_tokens": 0, "output_tokens": 0}

        if self.config.name == "claude-code":
            try:
                data = json.loads(output)
                usage = data.get("usage", {})
                return {
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0),
                }
            except json.JSONDecodeError:
                return {"input_tokens": 0, "output_tokens": 0}

        if self.config.name == "codex":
            total_input = 0
            total_output = 0
            for line in output.strip().split("\n"):
                try:
                    event = json.loads(line)
                    if event.get("type") == "turn.completed":
                        usage = event.get("usage", {})
                        total_input += usage.get("input_tokens", 0)
                        total_output += usage.get("output_tokens", 0)
                except json.JSONDecodeError:
                    continue
            return {"input_tokens": total_input, "output_tokens": total_output}

        return {"input_tokens": 0, "output_tokens": 0}

    def cleanup(self):
        for d in self._temp_dirs:
            shutil.rmtree(d, ignore_errors=True)
        self._temp_dirs.clear()
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/harness/test_runner.py -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add harness/runner.py tests/harness/test_runner.py
git commit -m "Add agent runner with workspace isolation and token parsing"
```

---

### Task 4: Test Runner (executes test suites)

**Files:**
- Create: `harness/test_executor.py`
- Create: `tests/harness/test_test_executor.py`

**Step 1: Write the failing test**

```python
# tests/harness/test_test_executor.py
import subprocess
from unittest.mock import patch
from pathlib import Path

from harness.test_executor import TestExecutor, TestResult


def test_parse_pytest_output_all_pass():
    output = """
test_main.py::test_one PASSED
test_main.py::test_two PASSED

============================== 2 passed ==============================
"""
    result = TestExecutor.parse_pytest_output(output, returncode=0)
    assert result.tests_total == 2
    assert result.tests_passed == 2
    assert result.passed is True


def test_parse_pytest_output_some_fail():
    output = """
test_main.py::test_one PASSED
test_main.py::test_two FAILED
test_main.py::test_three PASSED

========================= 2 passed, 1 failed =========================
"""
    result = TestExecutor.parse_pytest_output(output, returncode=1)
    assert result.tests_total == 3
    assert result.tests_passed == 2
    assert result.passed is False


def test_parse_jest_output_all_pass():
    output = """
Tests:       5 passed, 5 total
"""
    result = TestExecutor.parse_jest_output(output, returncode=0)
    assert result.tests_total == 5
    assert result.tests_passed == 5
    assert result.passed is True


def test_parse_make_test_output():
    output = """
[PASS] test_insert
[PASS] test_delete
[FAIL] test_search
Results: 2/3 passed
"""
    result = TestExecutor.parse_make_test_output(output, returncode=1)
    assert result.tests_total == 3
    assert result.tests_passed == 2
    assert result.passed is False
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/harness/test_test_executor.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# harness/test_executor.py
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from harness.config import TestRunnerConfig


@dataclass
class TestResult:
    tests_total: int
    tests_passed: int
    passed: bool
    raw_output: str
    error: str | None = None


class TestExecutor:
    def __init__(self, config: TestRunnerConfig):
        self.config = config

    def run(self, workspace: Path) -> TestResult:
        test_dir = workspace / self.config.pattern.rstrip("/")
        cmd = self.config.command.replace("{test_dir}", str(test_dir)).replace("{workspace}", str(workspace))

        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=120, cwd=str(workspace),
            )
            output = result.stdout + "\n" + result.stderr

            if self.config.language == "python":
                return self.parse_pytest_output(output, result.returncode)
            elif self.config.language in ("typescript", "angular"):
                return self.parse_jest_output(output, result.returncode)
            elif self.config.language in ("c", "cpp"):
                return self.parse_make_test_output(output, result.returncode)

            return TestResult(
                tests_total=0, tests_passed=0, passed=result.returncode == 0,
                raw_output=output,
            )
        except subprocess.TimeoutExpired:
            return TestResult(
                tests_total=0, tests_passed=0, passed=False,
                raw_output="", error="Test execution timed out",
            )

    @staticmethod
    def parse_pytest_output(output: str, returncode: int) -> TestResult:
        # Look for "X passed" and "X failed" in summary line
        passed_match = re.search(r"(\d+) passed", output)
        failed_match = re.search(r"(\d+) failed", output)
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        total = passed + failed
        return TestResult(
            tests_total=total, tests_passed=passed,
            passed=returncode == 0, raw_output=output,
        )

    @staticmethod
    def parse_jest_output(output: str, returncode: int) -> TestResult:
        # Jest: "Tests:  X passed, Y total" or "Tests:  X failed, Y passed, Z total"
        passed_match = re.search(r"(\d+) passed", output)
        total_match = re.search(r"(\d+) total", output)
        passed = int(passed_match.group(1)) if passed_match else 0
        total = int(total_match.group(1)) if total_match else 0
        return TestResult(
            tests_total=total, tests_passed=passed,
            passed=returncode == 0, raw_output=output,
        )

    @staticmethod
    def parse_make_test_output(output: str, returncode: int) -> TestResult:
        # Custom format: "Results: X/Y passed" or count [PASS]/[FAIL] lines
        results_match = re.search(r"(\d+)/(\d+) passed", output)
        if results_match:
            passed = int(results_match.group(1))
            total = int(results_match.group(2))
        else:
            passed = len(re.findall(r"\[PASS\]", output))
            failed = len(re.findall(r"\[FAIL\]", output))
            total = passed + failed
        return TestResult(
            tests_total=total, tests_passed=passed,
            passed=total > 0 and passed == total, raw_output=output,
        )
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/harness/test_test_executor.py -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add harness/test_executor.py tests/harness/test_test_executor.py
git commit -m "Add test executor with pytest/jest/make output parsers"
```

---

### Task 5: Scoring Module

**Files:**
- Create: `harness/scoring.py`
- Create: `tests/harness/test_scoring.py`

**Step 1: Write the failing test**

```python
# tests/harness/test_scoring.py
from harness.scoring import TaskScore, compute_summary


def _make_score(agent, task, tests_passed, tests_total, seconds, tokens_in, tokens_out, timed_out=False):
    return TaskScore(
        task=task, agent=agent, model="test-model",
        tests_passed=tests_passed, tests_total=tests_total,
        correctness=tests_passed / tests_total if tests_total else 0,
        wall_clock_seconds=seconds,
        input_tokens=tokens_in, output_tokens=tokens_out,
        timed_out=timed_out, error=None,
    )


def test_summary_counts_passed_tasks():
    scores = [
        _make_score("claude", "task1", 5, 5, 30, 1000, 500),
        _make_score("claude", "task2", 3, 5, 40, 2000, 800),
        _make_score("codex", "task1", 5, 5, 45, 1500, 600),
        _make_score("codex", "task2", 5, 5, 35, 1800, 700),
    ]
    summary = compute_summary(scores)
    assert summary["claude"]["tasks_fully_passed"] == 1
    assert summary["codex"]["tasks_fully_passed"] == 2


def test_summary_avg_correctness():
    scores = [
        _make_score("claude", "task1", 4, 4, 30, 1000, 500),
        _make_score("claude", "task2", 2, 4, 40, 2000, 800),
    ]
    summary = compute_summary(scores)
    assert summary["claude"]["avg_correctness"] == 0.75


def test_summary_excludes_timed_out_from_speed():
    scores = [
        _make_score("claude", "task1", 4, 4, 30, 1000, 500),
        _make_score("claude", "task2", 0, 4, 300, 0, 0, timed_out=True),
    ]
    summary = compute_summary(scores)
    assert summary["claude"]["avg_speed_seconds"] == 30.0
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/harness/test_scoring.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# harness/scoring.py
from dataclasses import dataclass


@dataclass
class TaskScore:
    task: str
    agent: str
    model: str | None
    tests_passed: int
    tests_total: int
    correctness: float
    wall_clock_seconds: float
    input_tokens: int
    output_tokens: int
    timed_out: bool
    error: str | None


def compute_summary(scores: list[TaskScore]) -> dict:
    by_agent: dict[str, list[TaskScore]] = {}
    for s in scores:
        by_agent.setdefault(s.agent, []).append(s)

    summary = {}
    for agent, agent_scores in by_agent.items():
        total_tasks = len(agent_scores)
        fully_passed = sum(1 for s in agent_scores if s.tests_passed == s.tests_total and s.tests_total > 0)
        avg_correctness = sum(s.correctness for s in agent_scores) / total_tasks if total_tasks else 0

        non_timed_out = [s for s in agent_scores if not s.timed_out]
        avg_speed = (
            sum(s.wall_clock_seconds for s in non_timed_out) / len(non_timed_out)
            if non_timed_out else 0
        )
        avg_tokens = (
            sum(s.input_tokens + s.output_tokens for s in non_timed_out) / len(non_timed_out)
            if non_timed_out else 0
        )

        summary[agent] = {
            "total_tasks": total_tasks,
            "tasks_fully_passed": fully_passed,
            "avg_correctness": round(avg_correctness, 2),
            "avg_speed_seconds": round(avg_speed, 2),
            "avg_total_tokens": round(avg_tokens, 2),
            "scores": [_score_to_dict(s) for s in agent_scores],
        }

    return summary


def _score_to_dict(s: TaskScore) -> dict:
    return {
        "task": s.task,
        "agent": s.agent,
        "model": s.model,
        "tests_passed": s.tests_passed,
        "tests_total": s.tests_total,
        "correctness": s.correctness,
        "wall_clock_seconds": s.wall_clock_seconds,
        "input_tokens": s.input_tokens,
        "output_tokens": s.output_tokens,
        "timed_out": s.timed_out,
        "error": s.error,
    }
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/harness/test_scoring.py -v`
Expected: 3 passed

**Step 5: Commit**

```bash
git add harness/scoring.py tests/harness/test_scoring.py
git commit -m "Add scoring module with summary computation"
```

---

### Task 6: Report Generator

**Files:**
- Create: `harness/report.py`
- Create: `tests/harness/test_report.py`

**Step 1: Write the failing test**

```python
# tests/harness/test_report.py
from harness.report import format_report
from harness.scoring import TaskScore


def _make_score(agent, task, passed, total, seconds, tokens_in, tokens_out, category="bugfix", language="python"):
    return TaskScore(
        task=task, agent=agent, model="test",
        tests_passed=passed, tests_total=total,
        correctness=passed / total if total else 0,
        wall_clock_seconds=seconds,
        input_tokens=tokens_in, output_tokens=tokens_out,
        timed_out=False, error=None,
    )


def test_format_report_contains_task_results():
    scores = [
        _make_score("claude-code", "task1", 5, 5, 30, 1000, 500),
        _make_score("codex", "task1", 3, 5, 45, 1500, 600),
    ]
    report = format_report(scores)
    assert "task1" in report
    assert "claude-code" in report.lower() or "Claude Code" in report
    assert "codex" in report.lower() or "Codex" in report


def test_format_report_contains_summary():
    scores = [
        _make_score("claude-code", "task1", 5, 5, 30, 1000, 500),
        _make_score("codex", "task1", 5, 5, 45, 1500, 600),
    ]
    report = format_report(scores)
    assert "SUMMARY" in report or "Summary" in report
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/harness/test_report.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# harness/report.py
from harness.scoring import TaskScore, compute_summary


def format_report(scores: list[TaskScore]) -> str:
    summary = compute_summary(scores)
    agents = sorted(summary.keys())
    if len(agents) != 2:
        agents = list(summary.keys())
    a1, a2 = agents[0], agents[1]

    lines = []
    lines.append("=" * 60)
    lines.append("  BENCHMARK RESULTS")
    lines.append("=" * 60)
    lines.append("")

    # Per-task results
    lines.append("TASK RESULTS")
    lines.append("-" * 60)

    # Group scores by task
    by_task: dict[str, dict[str, TaskScore]] = {}
    for s in scores:
        by_task.setdefault(s.task, {})[s.agent] = s

    header = f"{'Task':<30} {a1:<15} {a2:<15}"
    lines.append(header)
    lines.append("-" * 60)

    for task_name in sorted(by_task.keys()):
        task_scores = by_task[task_name]
        parts = [f"{task_name:<30}"]
        for agent in [a1, a2]:
            s = task_scores.get(agent)
            if s is None:
                parts.append(f"{'N/A':<15}")
            elif s.timed_out:
                parts.append(f"{'TIMEOUT':<15}")
            else:
                icon = "PASS" if s.tests_passed == s.tests_total else "FAIL"
                parts.append(f"{icon} {s.tests_passed}/{s.tests_total} {s.wall_clock_seconds:.0f}s  ")
        lines.append("".join(parts))

    lines.append("")
    lines.append("SUMMARY")
    lines.append("-" * 60)
    header = f"{'Metric':<25} {a1:<15} {a2:<15}"
    lines.append(header)
    lines.append("-" * 60)

    s1, s2 = summary[a1], summary[a2]
    lines.append(f"{'Tasks fully passed':<25} {s1['tasks_fully_passed']}/{s1['total_tasks']:<13} {s2['tasks_fully_passed']}/{s2['total_tasks']}")
    lines.append(f"{'Avg correctness':<25} {s1['avg_correctness']:<15} {s2['avg_correctness']}")
    lines.append(f"{'Avg speed (s)':<25} {s1['avg_speed_seconds']:<15} {s2['avg_speed_seconds']}")
    lines.append(f"{'Avg tokens':<25} {s1['avg_total_tokens']:<15} {s2['avg_total_tokens']}")

    return "\n".join(lines)
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/harness/test_report.py -v`
Expected: 2 passed

**Step 5: Commit**

```bash
git add harness/report.py tests/harness/test_report.py
git commit -m "Add report generator for terminal output"
```

---

### Task 7: Main Benchmark Runner (Orchestrator)

**Files:**
- Create: `harness/run.py`

**Step 1: Write the orchestrator**

```python
# harness/run.py
import json
import sys
from datetime import datetime
from pathlib import Path

from harness.config import load_config
from harness.task_loader import load_tasks
from harness.runner import AgentRunner
from harness.test_executor import TestExecutor, TestResult
from harness.scoring import TaskScore, compute_summary
from harness.report import format_report


def run_benchmark(tasks_dir: Path = None, config_path: Path = None):
    root = Path(__file__).parent.parent
    if tasks_dir is None:
        tasks_dir = root / "tasks"
    config = load_config(config_path)
    tasks = load_tasks(tasks_dir)

    if not tasks:
        print("No tasks found. Exiting.")
        sys.exit(1)

    print(f"Loaded {len(tasks)} tasks, {len(config.agents)} agents")

    run_id = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    results_base = root / config.results_dir / run_id
    all_scores: list[TaskScore] = []

    for task_idx, task in enumerate(tasks):
        # Alternate which agent goes first
        agents = list(config.agents)
        if task_idx % 2 == 1:
            agents = list(reversed(agents))

        for agent_config in agents:
            print(f"\n[{task.name}] Running {agent_config.name}...")

            runner = AgentRunner(agent_config)
            workspace = runner.prepare_workspace(task.repo_dir)

            # Run the agent
            agent_result = runner.run(task.prompt, workspace)

            # Copy tests and run them
            runner.copy_tests(task.tests_dir, workspace)
            test_runner_config = config.test_runners.get(task.language)

            if test_runner_config:
                executor = TestExecutor(test_runner_config)
                test_result = executor.run(workspace)
            else:
                print(f"  WARNING: No test runner for language '{task.language}'")
                test_result = TestResult(
                    tests_total=0, tests_passed=0, passed=False,
                    raw_output="", error=f"No test runner for {task.language}",
                )

            # Build score
            score = TaskScore(
                task=task.name,
                agent=agent_config.name,
                model=agent_config.model,
                tests_passed=test_result.tests_passed,
                tests_total=test_result.tests_total,
                correctness=test_result.tests_passed / test_result.tests_total if test_result.tests_total else 0,
                wall_clock_seconds=agent_result.wall_clock_seconds,
                input_tokens=agent_result.input_tokens,
                output_tokens=agent_result.output_tokens,
                timed_out=agent_result.timed_out,
                error=agent_result.error or test_result.error,
            )
            all_scores.append(score)

            icon = "PASS" if test_result.passed else "FAIL"
            print(f"  {icon} {test_result.tests_passed}/{test_result.tests_total} tests, {agent_result.wall_clock_seconds:.1f}s")

            # Save per-task result
            agent_dir = results_base / agent_config.name
            agent_dir.mkdir(parents=True, exist_ok=True)
            result_file = agent_dir / f"{task.name}.json"
            result_file.write_text(json.dumps({
                "task": task.name,
                "agent": agent_config.name,
                "model": agent_config.model,
                "passed": test_result.passed,
                "tests_total": test_result.tests_total,
                "tests_passed": test_result.tests_passed,
                "wall_clock_seconds": agent_result.wall_clock_seconds,
                "input_tokens": agent_result.input_tokens,
                "output_tokens": agent_result.output_tokens,
                "timed_out": agent_result.timed_out,
                "error": agent_result.error or test_result.error,
            }, indent=2))

            runner.cleanup()

    # Generate and print report
    report = format_report(all_scores)
    print("\n" + report)

    # Save summary
    summary = compute_summary(all_scores)
    summary_file = results_base / "summary.json"
    summary_file.write_text(json.dumps(summary, indent=2))
    print(f"\nResults saved to {results_base}")


if __name__ == "__main__":
    run_benchmark()
```

**Step 2: Verify it at least imports**

Run: `python -c "from harness.run import run_benchmark; print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add harness/run.py
git commit -m "Add main benchmark orchestrator"
```

---

### Task 8: Build Synthetic Task — 01-python-bugfix-csv

**Files:**
- Create: `tasks/01-python-bugfix-csv/prompt.md`
- Create: `tasks/01-python-bugfix-csv/metadata.json`
- Create: `tasks/01-python-bugfix-csv/repo/csv_parser.py`
- Create: `tasks/01-python-bugfix-csv/tests/test_csv_parser.py`

**Step 1: Write the correct solution first (reference, not shipped)**

```python
# Reference only — this is what the correct csv_parser.py should look like
def parse_csv(text: str) -> list[list[str]]:
    rows = []
    current_row = []
    current_field = ""
    in_quotes = False
    i = 0
    while i < len(text):
        char = text[i]
        if in_quotes:
            if char == '"' and i + 1 < len(text) and text[i + 1] == '"':
                current_field += '"'
                i += 2
                continue
            elif char == '"':
                in_quotes = False
            else:
                current_field += char
        else:
            if char == '"':
                in_quotes = True
            elif char == ',':
                current_row.append(current_field)
                current_field = ""
            elif char == '\n':
                current_row.append(current_field)
                rows.append(current_row)
                current_row = []
                current_field = ""
            else:
                current_field += char
        i += 1
    if current_field or current_row:
        current_row.append(current_field)
        rows.append(current_row)
    return rows
```

**Step 2: Write the test suite**

```python
# tasks/01-python-bugfix-csv/tests/test_csv_parser.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

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
```

**Step 3: Write the broken version (what the agent gets)**

```python
# tasks/01-python-bugfix-csv/repo/csv_parser.py
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
```

The bug: splits on `\n` first, so quoted fields containing newlines get broken across rows. Also doesn't handle escaped quotes (`""`) properly.

**Step 4: Write prompt.md**

```markdown
# Task: Fix CSV Parser Bug

The file `csv_parser.py` contains a `parse_csv` function that parses CSV text into rows and fields.

There are two bugs:
1. Fields containing newlines inside quotes are split incorrectly — the parser breaks on newlines even when inside a quoted field.
2. Escaped quotes (`""` inside quoted fields) are not handled — they should produce a single `"` character.

Fix both bugs. The function signature should remain the same: `parse_csv(text: str) -> list[list[str]]`.
```

**Step 5: Write metadata.json**

```json
{
    "language": "python",
    "category": "bugfix",
    "timeout_seconds": 120
}
```

**Step 6: Verify the tests fail against the broken code**

Run: `cd tasks/01-python-bugfix-csv && python -m pytest tests/ -v`
Expected: Some tests FAIL (specifically `test_quoted_field_with_newline`, `test_escaped_quote`, `test_mixed_rows_with_newlines_in_quotes`)

**Step 7: Commit**

```bash
git add tasks/01-python-bugfix-csv/
git commit -m "Add task 01: Python CSV parser bugfix"
```

---

### Task 9: Build Synthetic Task — 02-c-bugfix-linkedlist

**Files:**
- Create: `tasks/02-c-bugfix-linkedlist/prompt.md`
- Create: `tasks/02-c-bugfix-linkedlist/metadata.json`
- Create: `tasks/02-c-bugfix-linkedlist/repo/list.h`
- Create: `tasks/02-c-bugfix-linkedlist/repo/list.c`
- Create: `tasks/02-c-bugfix-linkedlist/repo/Makefile`
- Create: `tasks/02-c-bugfix-linkedlist/tests/test_list.c`
- Create: `tasks/02-c-bugfix-linkedlist/tests/Makefile`

Follow the same backwards-design pattern as Task 8:
1. Write correct implementation
2. Write tests that validate it
3. Introduce the memory leak bug (missing `free()` in `list_remove`)
4. Write prompt describing the bug
5. Verify tests fail on broken code
6. Commit

---

### Tasks 10-17: Build Remaining Synthetic Tasks (03 through 10)

Each follows the same pattern. For brevity, each task is one implementation step:

**Task 10:** `03-angular-feature-table-filter` — Angular table with search component
**Task 11:** `04-python-feature-pagination` — Flask/FastAPI pagination endpoint
**Task 12:** `05-typescript-scratch-task-queue` — Priority queue with retry/timeout
**Task 13:** `06-cpp-scratch-lru-cache` — LRU cache matching interface
**Task 14:** `07-python-refactor-monolith` — Split monolithic script into classes
**Task 15:** `08-typescript-refactor-callbacks` — Callback to async/await conversion
**Task 16:** `09-c-multifile-segfault` — Multi-file segfault with Makefile
**Task 17:** `10-fullstack-angular-python` — API endpoint + Angular component

For each:
1. Write the correct solution
2. Write the test suite
3. Break/remove the code
4. Write prompt.md and metadata.json
5. Verify tests fail against broken state
6. Commit

---

### Task 18: End-to-End Smoke Test

**Step 1: Create a tiny mock task for testing the full pipeline**

Create `tasks/00-smoke-test/` with a trivial Python task (fix a function that returns the wrong value) and a 2-test test suite.

**Step 2: Run the full benchmark against the smoke test with a mock agent**

Since we can't run the actual agents in CI, create a `--dry-run` flag for `run.py` that skips agent invocation and directly runs tests against the repo as-is. This validates the harness pipeline end-to-end.

Run: `python harness/run.py --dry-run --tasks-dir tasks/00-smoke-test`
Expected: Completes without error, produces a results directory with summary.json

**Step 3: Commit**

```bash
git add tasks/00-smoke-test/ harness/run.py
git commit -m "Add smoke test task and dry-run mode"
```

---

### Task 19: Final Integration — Run Full Benchmark

**Step 1: Verify both CLI tools are installed**

Run: `claude --version && codex --version`

**Step 2: Run the benchmark for real**

Run: `python harness/run.py`

**Step 3: Review results in `results/{run-id}/summary.json` and terminal output**

**Step 4: Commit results**

```bash
git add results/
git commit -m "Add first benchmark run results"
```
