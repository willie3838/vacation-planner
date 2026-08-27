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

"""Unit tests for Telemetry, Structured Logging, and Intent vs. Outcome tracking."""

import json
import logging

from app.telemetry.logging import StructuredJsonFormatter
from app.telemetry.tracing import (
    INTENT_BRAINSTORM,
    INTENT_SCHEDULE,
    AgentMetricsCollector,
    detect_user_intent,
    record_intent_and_outcome,
    trace_tool_execution,
)


def test_structured_json_formatter():
    """Verifies that log records are formatted into valid JSON with Google Cloud fields."""
    formatter = StructuredJsonFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path.py",
        lineno=10,
        msg="Test structured log message",
        args=(),
        exc_info=None,
    )
    record.event_type = "test_event"
    record.attributes = {"user_id": "u123", "latency_ms": 45.2}

    formatted_str = formatter.format(record)
    parsed = json.loads(formatted_str)

    assert parsed["severity"] == "INFO"
    assert parsed["message"] == "Test structured log message"
    assert parsed["logger"] == "test_logger"
    assert parsed["event_type"] == "test_event"
    assert parsed["attributes"]["user_id"] == "u123"
    assert parsed["attributes"]["latency_ms"] == 45.2
    assert "timestamp" in parsed


def test_detect_user_intent_classification():
    """Verifies user intent classification rules."""
    brainstorm_input = "Can you brainstorm ideas for 4 days in Paris?"
    meta = detect_user_intent(brainstorm_input)
    assert meta["primary_intent"] == INTENT_BRAINSTORM
    assert meta["confidence"] >= 0.8

    schedule_input = "Generate a day-by-day hourly schedule for Rome."
    meta_sched = detect_user_intent(schedule_input)
    assert meta_sched["primary_intent"] == INTENT_SCHEDULE


def test_record_intent_and_outcome():
    """Verifies intent vs. outcome recording and tracking."""
    record = record_intent_and_outcome(
        turn_id="turn_001",
        user_input="Brainstorm things to do in Kyoto",
        tools_executed=["brainstorm_itinerary"],
        outcome_status="SUCCESS",
        latency_ms=950.0,
    )

    assert record.turn_id == "turn_001"
    assert record.user_intent == INTENT_BRAINSTORM
    assert record.outcome_status == "SUCCESS"
    assert record.tools_executed == ["brainstorm_itinerary"]
    assert record.latency_ms == 950.0


def test_metrics_collector_recording_and_summary():
    """Verifies that token usage, turn count, intent distributions, and latencies aggregate correctly."""
    collector = AgentMetricsCollector()

    collector.record_turn(
        prompt_tokens=150,
        completion_tokens=50,
        latency_ms=800.0,
        tool_name="brainstorm_itinerary",
        intent=INTENT_BRAINSTORM,
        outcome_status="SUCCESS",
    )
    collector.record_turn(
        prompt_tokens=200,
        completion_tokens=100,
        latency_ms=1200.0,
        tool_name="generate_schedule",
        intent=INTENT_SCHEDULE,
        outcome_status="SUCCESS",
    )

    summary = collector.get_summary()
    assert summary["total_invocations"] == 2
    assert summary["total_prompt_tokens"] == 350
    assert summary["total_completion_tokens"] == 150
    assert summary["total_tokens"] == 500
    assert summary["average_latency_ms"] == 1000.0
    assert summary["tool_calls"]["brainstorm_itinerary"] == 1
    assert summary["tool_calls"]["generate_schedule"] == 1
    assert summary["intent_distribution"][INTENT_BRAINSTORM] == 1
    assert summary["outcome_distribution"]["SUCCESS"] == 2


def test_trace_tool_execution_span():
    """Verifies trace span execution wrapper."""
    span = trace_tool_execution(
        "spontaneous_recommendations", {"current_location": "Rome"}
    )
    assert span is not None
