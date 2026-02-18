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
