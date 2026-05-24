import json
from time import sleep
from typing import Any

from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelHTTPError

from wren_memory import build_toolkit

QUESTIONS = [
    "Who is the manager of Vikram Nair",
    "Which departments have the highest salary cost but lowest average performance?",
    "Find employees who are high performers, promotion recommended, but also high attrition risk.",
    "Which projects have the highest employee allocation concentration?",
    "Which managers have the strongest teams based on average performance score?",
    "Find overallocated employees and show their projects, roles, and total allocation.",
    "Which business unit has the highest billable allocation percentage?",
    "Show salary-to-performance efficiency by department.",
]


def run_with_retries(agent: Agent, question: str, max_attempts: int = 4) -> Any:
    for attempt in range(1, max_attempts + 1):
        try:
            return agent.run_sync(question)
        except ModelHTTPError as exc:
            if exc.status_code != 429 or attempt == max_attempts:
                raise
            sleep(2 * attempt)

    raise RuntimeError("unreachable")


def print_run_trace(result: Any) -> None:
    print("\nTrace:", flush=True)
    final_sql = None

    for message in result.all_messages():
        for part in message.parts:
            if getattr(part, "part_kind", None) == "thinking":
                continue

            if getattr(part, "part_kind", None) == "tool-call":
                args = _tool_args(part)
                tool_name = part.tool_name
                if tool_name == "wren_query":
                    final_sql = args.get("sql")
                print(f"- call {tool_name}: {_format_tool_args(tool_name, args)}", flush=True)

            if getattr(part, "part_kind", None) == "tool-return":
                print(
                    f"- return {part.tool_name}: {_summarize_tool_return(part.content)}",
                    flush=True,
                )

    print("\nFinal SQL:", flush=True)
    print(final_sql or "(no wren_query SQL generated)", flush=True)


def _tool_args(part: Any) -> dict[str, Any]:
    if isinstance(part.args, dict):
        return part.args
    if isinstance(part.args, str):
        try:
            parsed = json.loads(part.args)
        except json.JSONDecodeError:
            return {"raw": part.args}
        return parsed if isinstance(parsed, dict) else {"raw": parsed}
    return {}


def _format_tool_args(tool_name: str, args: dict[str, Any]) -> str:
    if tool_name in {"wren_query", "wren_dry_plan"} and "sql" in args:
        return args["sql"]
    if tool_name == "wren_fetch_context":
        return f"question={args.get('question')!r}, limit={args.get('limit', 5)!r}"
    if tool_name == "wren_recall_queries":
        return f"question={args.get('question')!r}, limit={args.get('limit', 3)!r}"
    return json.dumps(args, default=str)


def _summarize_tool_return(content: Any) -> str:
    if hasattr(content, "model_dump"):
        content = content.model_dump()

    if isinstance(content, dict):
        if {"row_count", "columns"}.issubset(content):
            return (
                f"{content['row_count']} row(s), "
                f"columns={', '.join(content.get('columns') or [])}"
            )
        if "strategy" in content:
            return f"context strategy={content['strategy']}"
    if isinstance(content, list):
        return f"{len(content)} item(s)"
    text = str(content).replace("\n", " ")
    return text[:240] + ("..." if len(text) > 240 else "")


def main() -> None:
    toolkit = build_toolkit("./db")
    toolset = toolkit.toolset()
    agent = Agent(
        "openai-chat:gpt-4o",
        instructions=toolkit.instructions(toolset=toolset),
        toolsets=[toolset],
        model_settings={"temperature": 0},
    )

    for number, question in enumerate(QUESTIONS, start=1):
        print(f"\n--- Question {number} ---", flush=True)
        print(question, flush=True)
        result = run_with_retries(agent, question)
        print_run_trace(result)
        print("\nAnswer:", flush=True)
        print(result.output)


if __name__ == "__main__":
    main()
