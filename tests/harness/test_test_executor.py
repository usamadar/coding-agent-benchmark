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


def test_parse_jest_output_prefers_tests_over_suites():
    output = """
Test Suites: 1 passed, 1 total
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
