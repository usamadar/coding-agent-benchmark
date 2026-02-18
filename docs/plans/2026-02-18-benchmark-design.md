# Coding Agent Benchmark: Claude Code vs Codex CLI

**Date:** 2026-02-18
**Goal:** Inform team adoption decision for coding agent tooling
**Tech Stack:** Python, TypeScript/Angular, C/C++

## Overview

An automated benchmark that runs 10 synthetic coding tasks through both Claude Code and Codex CLI, validates results against pre-written test suites, and produces a comparison report covering correctness, speed, and efficiency.

## Task Design

10 tasks across 5 categories and 4 languages. Each task is a purpose-built mini-repo (50-200 lines of source, 20-50 lines of tests). Tasks are designed backwards: write the solution first, write tests, then break the code.

### Task List

| # | Category | Language | Task |
|---|----------|----------|------|
| 1 | Bug Fix | Python | Fix a CSV parser that mishandles quoted fields with newlines |
| 2 | Bug Fix | C | Fix a memory leak in a linked list implementation |
| 3 | Add Feature | TypeScript/Angular | Add filtering/search to an existing table component |
| 4 | Add Feature | Python | Add pagination to an existing REST API |
| 5 | Write from Scratch | TypeScript | Implement a task queue with priority, retry, and timeout |
| 6 | Write from Scratch | C++ | Implement an LRU cache class matching a given interface |
| 7 | Refactor | Python | Refactor a monolithic script into modular classes |
| 8 | Refactor | TypeScript | Convert callback-based async to async/await |
| 9 | Multi-file Debug | C/C++ | Fix a segfault in a multi-file project with Makefile |
| 10 | Multi-file Feature | Angular + Python | Add full-stack feature: API endpoint + Angular component |

## Project Structure

```
coding-agent-benchmark/
├── harness/
│   ├── run.py              # Main benchmark runner
│   ├── config.yaml         # Configuration (models, timeouts)
│   ├── scoring.py          # Collects results, computes scores
│   └── report.py           # Generates comparison report
├── tasks/
│   ├── 01-python-bugfix-csv/
│   │   ├── prompt.md       # Task description given to agent
│   │   ├── metadata.json   # Category, language, difficulty, timeout
│   │   ├── repo/           # Source code (agent's workspace)
│   │   └── tests/          # Test suite (agent never sees this)
│   ├── 02-c-bugfix-linkedlist/
│   └── ... (03 through 10)
├── results/
│   └── {run-id}/
│       ├── summary.json
│       ├── claude-code/
│       │   └── {task}.json
│       └── codex/
│           └── {task}.json
└── docs/
    └── plans/
```

Tests live outside `repo/` so agents cannot read assertions to reverse-engineer solutions. The harness copies tests in after the agent finishes.

## Execution Flow

For each task, for each agent:

1. **Copy** `repo/` into an isolated temp directory
2. **Run agent** with the prompt, pointed at the temp dir. Record wall-clock time and token usage from JSON output.
3. **Copy tests** into the temp dir after agent finishes
4. **Run tests** (pytest for Python, jest/karma for TS/Angular, make + test runner for C/C++)
5. **Save result** as a per-task JSON file

### Agent Invocations

**Claude Code:**
```bash
claude -p "$(cat prompt.md)" \
  --output-format json \
  --allowedTools "Bash,Read,Edit,Write,Glob,Grep" \
  --no-session-persistence \
  --model claude-sonnet-4-6
```

**Codex CLI:**
```bash
codex exec "$(cat prompt.md)" \
  --json \
  --ephemeral \
  -a never \
  --sandbox workspace-write \
  -C /path/to/temp/workspace
```

### Per-Task Result JSON

```json
{
  "task": "01-python-bugfix-csv",
  "agent": "claude-code",
  "model": "claude-sonnet-4-6",
  "passed": true,
  "tests_total": 8,
  "tests_passed": 8,
  "wall_clock_seconds": 34.2,
  "input_tokens": 12450,
  "output_tokens": 3820,
  "timed_out": false,
  "error": null
}
```

## Guardrails

- **5-minute timeout per task** — safety net against infinite loops, not a scoring constraint
- **No token budget, no cost cap** — both tools are on flat subscription plans
- **Token counts recorded** as an efficiency metric, not a limit

## Scoring

Three metrics:

| Metric | What it measures | Calculation |
|--------|-----------------|-------------|
| Correctness | Does the code work? | `tests_passed / tests_total` (0.0 to 1.0) |
| Speed | How fast? | Wall-clock seconds (lower is better) |
| Efficiency | How much work? | Total tokens, input + output (lower is better) |

**Rules:**
- Correctness is the primary metric
- Speed and efficiency are only compared between tasks where both agents passed
- Timed-out tasks score 0 for correctness, excluded from speed/efficiency comparison
- For speed/efficiency, the better agent gets 1.0, the other gets a proportional ratio

## Report Output

Terminal output + `summary.json` breaking down results by:
- Per-task comparison (pass/fail, time, tokens)
- Summary totals (tasks passed, average correctness, average speed, average tokens)
- By category (bug fix, add feature, write from scratch, refactor, multi-file)
- By language (Python, TypeScript/Angular, C/C++, mixed)

## Fairness Controls

- **Identical inputs:** Same prompt, same repo copy, same tests
- **Isolation:** Each agent gets its own temp directory
- **Alternating order:** Task 1 runs Claude first, task 2 runs Codex first, etc.
- **Full access:** Both agents get filesystem read/write and shell command execution
- **Recorded versions:** CLI versions, model names logged in results
- **Single run per task:** No repeated runs; nondeterminism accepted
