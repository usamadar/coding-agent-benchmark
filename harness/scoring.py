from dataclasses import dataclass


@dataclass
class TaskScore:
    task: str
    agent: str
    model: str | None
    tests_passed: int
    tests_total: int
    correctness: float
    wall_clock_seconds: float
    input_tokens: int
    output_tokens: int
    timed_out: bool
    error: str | None


def compute_summary(scores: list[TaskScore]) -> dict:
    by_agent: dict[str, list[TaskScore]] = {}
    for s in scores:
        by_agent.setdefault(s.agent, []).append(s)

    summary = {}
    for agent, agent_scores in by_agent.items():
        total_tasks = len(agent_scores)
        fully_passed = sum(1 for s in agent_scores if s.tests_passed == s.tests_total and s.tests_total > 0)
        avg_correctness = sum(s.correctness for s in agent_scores) / total_tasks if total_tasks else 0

        non_timed_out = [s for s in agent_scores if not s.timed_out]
        avg_speed = (
            sum(s.wall_clock_seconds for s in non_timed_out) / len(non_timed_out)
            if non_timed_out else 0
        )
        avg_tokens = (
            sum(s.input_tokens + s.output_tokens for s in non_timed_out) / len(non_timed_out)
            if non_timed_out else 0
        )

        summary[agent] = {
            "total_tasks": total_tasks,
            "tasks_fully_passed": fully_passed,
            "avg_correctness": round(avg_correctness, 2),
            "avg_speed_seconds": round(avg_speed, 2),
            "avg_total_tokens": round(avg_tokens, 2),
            "scores": [_score_to_dict(s) for s in agent_scores],
        }

    return summary


def _score_to_dict(s: TaskScore) -> dict:
    return {
        "task": s.task,
        "agent": s.agent,
        "model": s.model,
        "tests_passed": s.tests_passed,
        "tests_total": s.tests_total,
        "correctness": s.correctness,
        "wall_clock_seconds": s.wall_clock_seconds,
        "input_tokens": s.input_tokens,
        "output_tokens": s.output_tokens,
        "timed_out": s.timed_out,
        "error": s.error,
    }
