from harness.report import format_report
from harness.scoring import TaskScore


def _make_score(agent, task, passed, total, seconds):
    return TaskScore(
        task=task, agent=agent, model="test",
        tests_passed=passed, tests_total=total,
        correctness=passed / total if total else 0,
        wall_clock_seconds=seconds,
        timed_out=False, error=None,
    )


def test_format_report_contains_task_results():
    scores = [
        _make_score("claude-code", "task1", 5, 5, 30),
        _make_score("codex", "task1", 3, 5, 45),
    ]
    report = format_report(scores)
    assert "task1" in report
    assert "claude-code" in report.lower() or "Claude Code" in report
    assert "codex" in report.lower() or "Codex" in report


def test_format_report_contains_summary():
    scores = [
        _make_score("claude-code", "task1", 5, 5, 30),
        _make_score("codex", "task1", 5, 5, 45),
    ]
    report = format_report(scores)
    assert "SUMMARY" in report or "Summary" in report
