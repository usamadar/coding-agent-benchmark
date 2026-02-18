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
