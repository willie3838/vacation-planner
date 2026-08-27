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

"""Telemetry, OpenTelemetry tracing, and Intent vs. Outcome tracking."""

import logging
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

from opentelemetry import trace

from app.telemetry.logging import log_structured

logger = logging.getLogger(__name__)
tracer = trace.get_tracer("vacation_planner.telemetry")


# Intent Categories
INTENT_BRAINSTORM = "ITINERARY_BRAINSTORM"
INTENT_SCHEDULE = "SCHEDULE_GENERATION"
INTENT_SPONTANEOUS = "SPONTANEOUS_EXPLORATION"
INTENT_PREFERENCES = "MEMORY_PREFERENCE_UPDATE"
INTENT_GENERAL = "GENERAL_TRAVEL_INQUIRY"

INTENT_KEYWORDS = {
    INTENT_BRAINSTORM: [
        "brainstorm",
        "ideas",
        "suggest",
        "top attractions",
        "what to do",
        "places to visit",
        "recommendations",
    ],
    INTENT_SCHEDULE: [
        "schedule",
        "itinerary",
        "plan my day",
        "day 1",
        "day 2",
        "day-by-day",
        "hourly",
        "timeline",
    ],
    INTENT_SPONTANEOUS: [
        "spontaneous",
        "nearby",
        "right now",
        "hidden gem",
        "lowkey",
        "around here",
        "current location",
    ],
    INTENT_PREFERENCES: [
        "i am vegan",
        "vegetarian",
        "budget",
        "allergy",
        "my preference",
        "i prefer",
        "hate crowds",
    ],
}


def detect_user_intent(text: str) -> dict[str, Any]:
    """Classifies user input into structured intent metadata."""
    lower = text.lower()
    matched_intents: list[str] = []

    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            matched_intents.append(intent)

    primary_intent = matched_intents[0] if matched_intents else INTENT_GENERAL
    confidence = 0.9 if matched_intents else 0.5

    return {
        "primary_intent": primary_intent,
        "matched_intents": matched_intents,
        "confidence": confidence,
    }


@dataclass
class IntentOutcomeRecord:
    """Data model capturing explicit intent vs. execution outcome."""

    turn_id: str
    user_intent: str
    tools_executed: list[str] = field(default_factory=list)
    outcome_status: str = "SUCCESS"  # SUCCESS, PARTIAL, FAILED
    latency_ms: float = 0.0
    error_message: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AgentMetricsCollector:
    """Collects token usage, latency, tool execution, and intent vs outcome metrics."""

    def __init__(self) -> None:
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_invocations = 0
        self.tool_execution_counts: dict[str, int] = {}
        self.intent_distribution: dict[str, int] = {}
        self.outcome_distribution: dict[str, int] = {}
        self.latencies_ms: list[float] = []
        self.recent_records: list[dict[str, Any]] = []

    def record_turn(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        tool_name: str | None = None,
        intent: str | None = None,
        outcome_status: str = "SUCCESS",
    ) -> None:
        """Records a single conversation turn with intent and outcome metrics."""
        self.total_invocations += 1
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.latencies_ms.append(latency_ms)

        if tool_name:
            self.tool_execution_counts[tool_name] = (
                self.tool_execution_counts.get(tool_name, 0) + 1
            )

        if intent:
            self.intent_distribution[intent] = (
                self.intent_distribution.get(intent, 0) + 1
            )

        self.outcome_distribution[outcome_status] = (
            self.outcome_distribution.get(outcome_status, 0) + 1
        )

    def record_intent_outcome(self, record: IntentOutcomeRecord) -> None:
        """Stores and aggregates an intent vs. outcome record."""
        self.recent_records.append(record.to_dict())
        # Keep last 100 in memory
        if len(self.recent_records) > 100:
            self.recent_records.pop(0)

        self.intent_distribution[record.user_intent] = (
            self.intent_distribution.get(record.user_intent, 0) + 1
        )
        self.outcome_distribution[record.outcome_status] = (
            self.outcome_distribution.get(record.outcome_status, 0) + 1
        )

    def get_summary(self) -> dict[str, Any]:
        """Returns aggregated telemetry metrics including intent/outcome distributions."""
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
            "intent_distribution": self.intent_distribution,
            "outcome_distribution": self.outcome_distribution,
        }


metrics_collector = AgentMetricsCollector()


def record_intent_and_outcome(
    turn_id: str,
    user_input: str,
    tools_executed: list[str],
    outcome_status: str = "SUCCESS",
    latency_ms: float = 0.0,
    error_message: str | None = None,
) -> IntentOutcomeRecord:
    """Explicitly records intent vs outcome to OTel traces, structured JSON logs, and metrics."""
    intent_meta = detect_user_intent(user_input)
    detected_intent = intent_meta["primary_intent"]

    record = IntentOutcomeRecord(
        turn_id=turn_id,
        user_intent=detected_intent,
        tools_executed=tools_executed,
        outcome_status=outcome_status,
        latency_ms=latency_ms,
        error_message=error_message,
    )

    metrics_collector.record_intent_outcome(record)

    # Attach attributes to current OpenTelemetry span if available
    span = trace.get_current_span()
    if span and span.is_recording():
        span.set_attribute("agent.turn_id", turn_id)
        span.set_attribute("agent.intent.category", detected_intent)
        span.set_attribute("agent.intent.confidence", intent_meta["confidence"])
        span.set_attribute("agent.outcome.status", outcome_status)
        span.set_attribute("agent.outcome.tools_count", len(tools_executed))
        span.set_attribute("agent.outcome.latency_ms", latency_ms)

    # Emit structured JSON log
    log_structured(
        logger=logger,
        level=logging.INFO if outcome_status == "SUCCESS" else logging.WARNING,
        message=f"Intent vs. Outcome: {detected_intent} -> {outcome_status}",
        event_type="intent_vs_outcome",
        turn_id=turn_id,
        user_intent=detected_intent,
        tools_executed=tools_executed,
        outcome_status=outcome_status,
        latency_ms=latency_ms,
        error=error_message,
    )

    return record


def trace_tool_execution(tool_name: str, args: dict[str, Any]) -> Any:
    """Context manager or tracer span helper for tool execution with structured logging."""
    with tracer.start_as_current_span(f"tool.{tool_name}") as span:
        span.set_attribute("tool.name", tool_name)
        span.set_attribute("tool.args_count", len(args))
        log_structured(
            logger=logger,
            level=logging.INFO,
            message=f"Executing tool {tool_name}",
            event_type="tool_execution",
            tool_name=tool_name,
            args_count=len(args),
        )
        return span
