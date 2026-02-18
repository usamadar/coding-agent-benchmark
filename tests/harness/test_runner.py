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
