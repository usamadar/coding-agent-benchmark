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
