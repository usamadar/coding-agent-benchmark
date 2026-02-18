from harness.scoring import TaskScore, compute_summary


def format_report(scores: list[TaskScore]) -> str:
    summary = compute_summary(scores)
    agents = sorted(summary.keys())
    if len(agents) != 2:
        agents = list(summary.keys())
    a1, a2 = agents[0], agents[1]

    lines = []
    lines.append("=" * 60)
    lines.append("  BENCHMARK RESULTS")
    lines.append("=" * 60)
    lines.append("")

    # Per-task results
    lines.append("TASK RESULTS")
    lines.append("-" * 60)

    # Group scores by task
    by_task: dict[str, dict[str, TaskScore]] = {}
    for s in scores:
        by_task.setdefault(s.task, {})[s.agent] = s

    header = f"{'Task':<30} {a1:<15} {a2:<15}"
    lines.append(header)
    lines.append("-" * 60)

    for task_name in sorted(by_task.keys()):
        task_scores = by_task[task_name]
        parts = [f"{task_name:<30}"]
        for agent in [a1, a2]:
            s = task_scores.get(agent)
            if s is None:
                parts.append(f"{'N/A':<15}")
            elif s.timed_out:
                parts.append(f"{'TIMEOUT':<15}")
            else:
                icon = "PASS" if s.tests_passed == s.tests_total else "FAIL"
                parts.append(f"{icon} {s.tests_passed}/{s.tests_total} {s.wall_clock_seconds:.0f}s  ")
        lines.append("".join(parts))

    lines.append("")
    lines.append("SUMMARY")
    lines.append("-" * 60)
    header = f"{'Metric':<25} {a1:<15} {a2:<15}"
    lines.append(header)
    lines.append("-" * 60)

    s1, s2 = summary[a1], summary[a2]
    lines.append(f"{'Tasks fully passed':<25} {s1['tasks_fully_passed']}/{s1['total_tasks']:<13} {s2['tasks_fully_passed']}/{s2['total_tasks']}")
    lines.append(f"{'Avg correctness':<25} {s1['avg_correctness']:<15} {s2['avg_correctness']}")
    lines.append(f"{'Avg speed (s)':<25} {s1['avg_speed_seconds']:<15} {s2['avg_speed_seconds']}")
    lines.append(f"{'Avg tokens':<25} {s1['avg_total_tokens']:<15} {s2['avg_total_tokens']}")

    return "\n".join(lines)
