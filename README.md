# Coding Agent Benchmark

A benchmark harness for evaluating and comparing coding agents (LLM-powered CLI tools) across a suite of synthetic software engineering tasks. Measures correctness and speed.

## Overview

The harness runs each configured agent against a set of isolated coding tasks, then executes hidden test suites to score the results. Agents work in temporary workspaces and never see the tests, ensuring a fair evaluation.

**Default agents:** Claude Code (`claude-opus-4-6`) and Codex CLI (`gpt-5.3-codex`)

**Metrics collected per task:**
- Test pass rate (correctness)
- Wall-clock time

## Tasks

11 tasks spanning multiple languages and categories:

| # | Task | Language | Category |
|---|------|----------|----------|
| 00 | smoke-test | Python | bugfix |
| 01 | python-bugfix-csv | Python | bugfix |
| 02 | c-bugfix-linkedlist | C | bugfix |
| 03 | typescript-feature-table-filter | TypeScript | feature |
| 04 | python-feature-pagination | Python | feature |
| 05 | typescript-scratch-task-queue | TypeScript | scratch |
| 06 | cpp-scratch-lru-cache | C++ | scratch |
| 07 | python-refactor-monolith | Python | refactor |
| 08 | typescript-refactor-callbacks | TypeScript | refactor |
| 09 | c-multifile-segfault | C/C++ | multifile |
| 10 | fullstack-angular-python | Python/Angular | multifile |

Each task contains:
```
tasks/<name>/
  metadata.json   # language, category, timeout
  prompt.md       # instruction given to the agent
  repo/           # source code (broken or incomplete)
  tests/          # hidden test suite
```

## Quick Start

### Prerequisites

- Python 3.11+
- Agent CLIs installed and on PATH (e.g. `claude`, `codex`)
- Language toolchains for the tasks you want to run (Python, Node.js, GCC/G++, Make)

### Install

```bash
pip install -r requirements.txt
```

### Run

```bash
# Full benchmark (all agents, all tasks)
python3 -m harness.run

# Dry run -- test the repos as-is without invoking agents
python3 -m harness.run --dry-run

# Custom config or tasks directory
python3 -m harness.run --config path/to/config.yaml --tasks-dir path/to/tasks
```

### CLI Options

| Flag | Description |
|------|-------------|
| `--dry-run` | Skip agent invocation, run tests on unmodified repos |
| `--config PATH` | Path to config YAML (default: `harness/config.yaml`) |
| `--tasks-dir PATH` | Path to tasks directory (default: `tasks/`) |

## Configuration

Agents, test runners, and output directory are defined in `harness/config.yaml`.

### Adding an Agent

```yaml
agents:
  my-agent:
    command: "my-cli"
    args: ["--prompt", "{prompt}", "--model", "{model}"]
    model: "my-model-name"
    timeout_seconds: 300
```

`{prompt}`, `{model}`, and `{workspace}` are replaced at runtime.

### Test Runners

Each language needs a test runner entry:

```yaml
test_runners:
  python:
    command: "python3 -m pytest {test_dir} -v --tb=short"
    pattern: "tests/"
  typescript:
    command: "cd {workspace} && npm install --quiet 2>/dev/null && npx jest {test_dir} --verbose"
    pattern: "tests/"
```

## Output

Results are saved to `results/<run-id>/`:

```
results/2026-02-18-154523/
  summary.json            # per-agent aggregate metrics
  claude-code/
    00-smoke-test.json    # per-task result
    ...
  codex/
    00-smoke-test.json
    ...
```

The terminal report shows a comparison table:

```
==============================================================
  BENCHMARK RESULTS
==============================================================

TASK RESULTS
--------------------------------------------------------------
Task                           claude-code     codex
--------------------------------------------------------------
00-smoke-test                  PASS 2/2 20s    PASS 2/2 29s
01-python-bugfix-csv           PASS 8/8 29s    PASS 8/8 49s
02-c-bugfix-linkedlist         PASS 8/8 18s    PASS 8/8 57s
03-typescript-feature-table-f  PASS 13/13 18s  PASS 13/13 37s
04-python-feature-pagination   PASS 10/10 19s  PASS 10/10 59s
05-typescript-scratch-task-qu  PASS 8/8 56s    PASS 8/8 60s
06-cpp-scratch-lru-cache       PASS 9/9 56s    PASS 9/9 65s
07-python-refactor-monolith    PASS 12/12 20s  PASS 12/12 43s
08-typescript-refactor-callba  PASS 10/10 35s  PASS 10/10 59s
09-c-multifile-segfault        PASS 8/8 69s    PASS 8/8 66s
10-fullstack-angular-python    PASS 10/10 22s  PASS 10/10 44s

SUMMARY
---------------------------------------------------------
Metric                    claude-code     codex
---------------------------------------------------------
Tasks fully passed        11/11           11/11
Avg correctness           1.0             1.0
Avg speed (s)             32.8            51.62
```

## Project Structure

```
harness/
  config.py          # Configuration loading (AgentConfig, TestRunnerConfig)
  config.yaml        # Default agent and test runner definitions
  run.py             # Main benchmark orchestrator and CLI entry point
  runner.py          # Agent execution and workspace isolation
  task_loader.py     # Task discovery and metadata parsing
  test_executor.py   # Test execution and output parsing (pytest, jest, make)
  scoring.py         # Score aggregation and summary computation
  report.py          # Terminal report formatting
tasks/               # Benchmark task definitions
tests/               # Unit tests for the harness
docs/plans/          # Design and implementation documentation
results/             # Benchmark run output (gitignored)
```

## Running Tests

```bash
python3 -m pytest tests/ -v
```

## Adding a Task

1. Create a directory under `tasks/` (prefix with a number for ordering)
2. Add `metadata.json`:
   ```json
   {
     "language": "python",
     "category": "bugfix",
     "timeout_seconds": 120
   }
   ```
   For multi-language tasks, add `"test_languages": ["python", "typescript"]`.
3. Add `prompt.md` with the task description
4. Add `repo/` with the source code
5. Add `tests/` with the test suite

## License

Internal use.
