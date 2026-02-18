from pathlib import Path
from unittest.mock import patch

from harness import config as harness_config
from harness import test_executor as harness_test_executor
from harness.run import run_tests_for_task
from harness.task_loader import BenchmarkTask


def _task_with_test_languages(languages: list[str]) -> BenchmarkTask:
    primary = languages[0] if languages else "python"
    return BenchmarkTask(
        name="sample-task",
        prompt="Implement the feature",
        language=primary,
        test_languages=languages,
        category="feature",
        timeout_seconds=120,
        repo_dir=Path("/tmp/repo"),
        tests_dir=Path("/tmp/tests"),
        task_dir=Path("/tmp/task"),
    )


def test_run_tests_for_task_aggregates_multiple_runners():
    task = _task_with_test_languages(["python", "typescript"])
    runners = {
        "python": harness_config.TestRunnerConfig(language="python", command="pytest", pattern="tests/"),
        "typescript": harness_config.TestRunnerConfig(language="typescript", command="jest", pattern="tests/"),
    }
    with patch("harness.run.TestExecutor.run", side_effect=[
        harness_test_executor.TestResult(tests_total=2, tests_passed=2, passed=True, raw_output="python ok"),
        harness_test_executor.TestResult(tests_total=3, tests_passed=2, passed=False, raw_output="ts fail"),
    ]):
        result = run_tests_for_task(task, Path("/tmp/workspace"), runners)

    assert result.tests_total == 5
    assert result.tests_passed == 4
    assert result.passed is False
    assert result.error is None
    assert "[python]" in result.raw_output
    assert "[typescript]" in result.raw_output


def test_run_tests_for_task_reports_missing_runner():
    task = _task_with_test_languages(["python", "rust"])
    runners = {
        "python": harness_config.TestRunnerConfig(language="python", command="pytest", pattern="tests/"),
    }
    with patch("harness.run.TestExecutor.run", return_value=harness_test_executor.TestResult(
        tests_total=1, tests_passed=1, passed=True, raw_output="python ok"
    )):
        result = run_tests_for_task(task, Path("/tmp/workspace"), runners)

    assert result.tests_total == 1
    assert result.tests_passed == 1
    assert result.passed is False
    assert result.error == "No test runner for rust"
