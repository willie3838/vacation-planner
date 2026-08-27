# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Telemetry and OpenTelemetry tracing utilities for Vacation Planner Agent."""

import logging
from typing import Any

from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer("vacation_planner.telemetry")


class AgentMetricsCollector:
    """Collects token usage, latency, and tool execution metrics."""

    def __init__(self) -> None:
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_invocations = 0
        self.tool_execution_counts: dict[str, int] = {}
        self.latencies_ms: list[float] = []

    def record_turn(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        tool_name: str | None = None,
    ) -> None:
        """Records a single conversation turn's metrics."""
        self.total_invocations += 1
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.latencies_ms.append(latency_ms)

        if tool_name:
            self.tool_execution_counts[tool_name] = (
                self.tool_execution_counts.get(tool_name, 0) + 1
            )

    def get_summary(self) -> dict[str, Any]:
        """Returns aggregated telemetry metrics."""
        avg_latency = (
            sum(self.latencies_ms) / len(self.latencies_ms)
            if self.latencies_ms
            else 0.0
        )
        return {
            "total_invocations": self.total_invocations,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "average_latency_ms": round(avg_latency, 2),
            "tool_calls": self.tool_execution_counts,
        }


metrics_collector = AgentMetricsCollector()


def trace_tool_execution(tool_name: str, args: dict[str, Any]) -> Any:
    """Context manager or tracer span helper for tool execution."""
    with tracer.start_as_current_span(f"tool.{tool_name}") as span:
        span.set_attribute("tool.name", tool_name)
        span.set_attribute("tool.args_count", len(args))
        logger.info("Tracing tool call %s with args %s", tool_name, args)
        return span
