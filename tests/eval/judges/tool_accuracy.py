# Copyright 2026 Google LLC


def evaluate(instance: dict) -> dict:
    """Programmatic metric: checks tool calling trajectory in agent_data."""
    turns = (instance.get("agent_data") or {}).get("turns", [])
    tool_calls = []

    for turn in turns:
        for event in turn.get("events", []):
            for part in (event.get("content") or {}).get("parts", []):
                if "function_call" in part:
                    tool_calls.append(part["function_call"])

    has_tools = len(tool_calls) > 0
    all_args_valid = (
        all(bool(tc.get("args")) for tc in tool_calls) if has_tools else False
    )
    score = 1.0 if (has_tools and all_args_valid) else (0.5 if has_tools else 0.0)
    return {
        "score": score,
        "explanation": f"Tool count: {len(tool_calls)}, Valid args: {all_args_valid}",
    }
