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
        shutil.copytree(tests_dir, dest, dirs_exist_ok=True)

    def run(self, prompt: str, workspace: Path) -> AgentResult:
        args = [self.config.command]
        for arg in self.config.args:
            rendered = arg.replace("{prompt}", prompt)
            if self.config.model:
                rendered = rendered.replace("{model}", self.config.model)
            args.append(rendered)

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

        return AgentResult(
            agent=self.config.name,
            model=self.config.model,
            wall_clock_seconds=round(elapsed, 2),
            timed_out=timed_out,
            error=error,
            raw_output=raw_output,
        )

    def cleanup(self):
        for d in self._temp_dirs:
            shutil.rmtree(d, ignore_errors=True)
        self._temp_dirs.clear()
