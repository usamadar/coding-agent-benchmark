import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from harness.config import load_config
from harness.task_loader import load_tasks
from harness.runner import AgentRunner, AgentResult
from harness.test_executor import TestExecutor, TestResult
from harness.scoring import TaskScore, compute_summary
from harness.report import format_report


def run_tests_for_task(task, workspace: Path, test_runners: dict) -> TestResult:
    tests_total = 0
    tests_passed = 0
    all_passed = True
    raw_outputs: list[str] = []
    errors: list[str] = []

    languages = task.test_languages or [task.language]
    for language in languages:
        test_runner_config = test_runners.get(language)
        if not test_runner_config:
            all_passed = False
            errors.append(f"No test runner for {language}")
            continue

        executor = TestExecutor(test_runner_config)
        result = executor.run(workspace)
        tests_total += result.tests_total
        tests_passed += result.tests_passed
        raw_outputs.append(f"[{language}]\n{result.raw_output}")
        if not result.passed:
            all_passed = False
        if result.error:
            errors.append(f"{language}: {result.error}")

    return TestResult(
        tests_total=tests_total,
        tests_passed=tests_passed,
        passed=all_passed and not errors,
        raw_output="\n\n".join(raw_outputs),
        error="; ".join(errors) if errors else None,
    )


def run_benchmark(tasks_dir: Path = None, config_path: Path = None, dry_run: bool = False):
    root = Path(__file__).parent.parent
    if tasks_dir is None:
        tasks_dir = root / "tasks"
    config = load_config(config_path)
    tasks = load_tasks(tasks_dir)

    if not tasks:
        print("No tasks found. Exiting.")
        sys.exit(1)

    if dry_run:
        print(f"DRY RUN: Loaded {len(tasks)} tasks (skipping agent invocation)")
        agents_to_run = [config.agents[0]] if config.agents else []
    else:
        print(f"Loaded {len(tasks)} tasks, {len(config.agents)} agents")
        agents_to_run = None  # use all agents per task

    run_id = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    results_base = root / config.results_dir / run_id
    all_scores: list[TaskScore] = []

    for task_idx, task in enumerate(tasks):
        if agents_to_run is not None:
            agents = agents_to_run
        else:
            # Rotate which agent goes first for fairness
            agents = list(config.agents)
            rot = task_idx % len(agents)
            agents = agents[rot:] + agents[:rot]

        for agent_config in agents:
            label = f"{agent_config.name} (dry-run)" if dry_run else agent_config.name
            print(f"\n[{task.name}] Running {label}...")

            runner = AgentRunner(agent_config)
            workspace = runner.prepare_workspace(task.repo_dir)

            if dry_run:
                # Skip agent invocation; test the repo as-is
                agent_result = AgentResult(
                    agent=agent_config.name,
                    model=agent_config.model,
                    wall_clock_seconds=0.0,
                    timed_out=False,
                    error=None,
                    raw_output="(dry run)",
                )
            else:
                agent_result = runner.run(task.prompt, workspace)

            # Copy tests and run them
            runner.copy_tests(task.tests_dir, workspace)
            test_result = run_tests_for_task(task, workspace, config.test_runners)
            if test_result.error:
                for err in test_result.error.split("; "):
                    if err.startswith("No test runner for "):
                        missing_lang = err.replace("No test runner for ", "")
                        print(f"  WARNING: No test runner for language '{missing_lang}'")

            # Build score
            score = TaskScore(
                task=task.name,
                agent=agent_config.name,
                model=agent_config.model,
                tests_passed=test_result.tests_passed,
                tests_total=test_result.tests_total,
                correctness=test_result.tests_passed / test_result.tests_total if test_result.tests_total else 0,
                wall_clock_seconds=agent_result.wall_clock_seconds,
                timed_out=agent_result.timed_out,
                error=agent_result.error or test_result.error,
            )
            all_scores.append(score)

            icon = "PASS" if test_result.passed else "FAIL"
            print(f"  {icon} {test_result.tests_passed}/{test_result.tests_total} tests, {agent_result.wall_clock_seconds:.1f}s")

            # Save per-task result
            agent_dir = results_base / agent_config.name
            agent_dir.mkdir(parents=True, exist_ok=True)
            result_file = agent_dir / f"{task.name}.json"
            result_file.write_text(json.dumps({
                "task": task.name,
                "test_languages": task.test_languages,
                "agent": agent_config.name,
                "model": agent_config.model,
                "passed": test_result.passed,
                "tests_total": test_result.tests_total,
                "tests_passed": test_result.tests_passed,
                "wall_clock_seconds": agent_result.wall_clock_seconds,
                "timed_out": agent_result.timed_out,
                "error": agent_result.error or test_result.error,
            }, indent=2))

            runner.cleanup()

    # Generate and print report (need at least 2 agents for comparison)
    if len(set(s.agent for s in all_scores)) >= 2:
        report = format_report(all_scores)
        print("\n" + report)
    else:
        # Single-agent summary (dry-run mode)
        print("\n" + "=" * 60)
        print("  DRY RUN RESULTS")
        print("=" * 60)
        for s in all_scores:
            icon = "PASS" if s.tests_passed == s.tests_total and s.tests_total > 0 else "FAIL"
            print(f"  {icon} {s.task}: {s.tests_passed}/{s.tests_total} tests")

    # Save summary
    summary = compute_summary(all_scores)
    results_base.mkdir(parents=True, exist_ok=True)
    summary_file = results_base / "summary.json"
    summary_file.write_text(json.dumps(summary, indent=2))
    print(f"\nResults saved to {results_base}")


def main():
    parser = argparse.ArgumentParser(description="Run coding agent benchmark")
    parser.add_argument("--tasks-dir", type=Path, help="Path to tasks directory")
    parser.add_argument("--config", type=Path, help="Path to config.yaml")
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip agent invocation, test repos as-is")
    args = parser.parse_args()
    run_benchmark(tasks_dir=args.tasks_dir, config_path=args.config, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
