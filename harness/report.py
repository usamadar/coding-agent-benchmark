from harness.scoring import TaskScore, compute_summary


def format_report(scores: list[TaskScore]) -> str:
    summary = compute_summary(scores)
    agents = sorted(summary.keys())
    col = 15

    lines = []
    lines.append("=" * (30 + col * len(agents) + len(agents)))
    lines.append("  BENCHMARK RESULTS")
    lines.append("=" * (30 + col * len(agents) + len(agents)))
    lines.append("")

    # Per-task results
    lines.append("TASK RESULTS")
    lines.append("-" * (30 + col * len(agents) + len(agents)))

    # Group scores by task
    by_task: dict[str, dict[str, TaskScore]] = {}
    for s in scores:
        by_task.setdefault(s.task, {})[s.agent] = s

    header = f"{'Task':<30}" + "".join(f" {a:<{col}}" for a in agents)
    lines.append(header)
    lines.append("-" * (30 + col * len(agents) + len(agents)))

    for task_name in sorted(by_task.keys()):
        task_scores = by_task[task_name]
        parts = [f"{task_name:<30}"]
        for agent in agents:
            s = task_scores.get(agent)
            if s is None:
                parts.append(f" {'N/A':<{col}}")
            elif s.timed_out:
                parts.append(f" {'TIMEOUT':<{col}}")
            else:
                icon = "PASS" if s.tests_passed == s.tests_total else "FAIL"
                cell = f"{icon} {s.tests_passed}/{s.tests_total} {s.wall_clock_seconds:.0f}s"
                parts.append(f" {cell:<{col}}")
        lines.append("".join(parts))

    lines.append("")
    lines.append("SUMMARY")
    sep_width = 25 + col * len(agents) + len(agents)
    lines.append("-" * sep_width)
    header = f"{'Metric':<25}" + "".join(f" {a:<{col}}" for a in agents)
    lines.append(header)
    lines.append("-" * sep_width)

    metrics = [
        ("Tasks fully passed", lambda s: f"{s['tasks_fully_passed']}/{s['total_tasks']}"),
        ("Avg correctness", lambda s: str(s["avg_correctness"])),
        ("Avg speed (s)", lambda s: str(s["avg_speed_seconds"])),
    ]

    for metric_name, fmt in metrics:
        row = f"{metric_name:<25}"
        for agent in agents:
            row += f" {fmt(summary[agent]):<{col}}"
        lines.append(row)

    return "\n".join(lines)
