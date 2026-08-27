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

"""Unit tests for Telemetry and Metrics collection."""

from app.telemetry.tracing import AgentMetricsCollector, trace_tool_execution


def test_metrics_collector_recording_and_summary():
    """Verifies that token usage, turn count, and latencies aggregate correctly."""
    collector = AgentMetricsCollector()

    collector.record_turn(
        prompt_tokens=150,
        completion_tokens=50,
        latency_ms=800.0,
        tool_name="brainstorm_itinerary",
    )
    collector.record_turn(
        prompt_tokens=200,
        completion_tokens=100,
        latency_ms=1200.0,
        tool_name="generate_schedule",
    )

    summary = collector.get_summary()
    assert summary["total_invocations"] == 2
    assert summary["total_prompt_tokens"] == 350
    assert summary["total_completion_tokens"] == 150
    assert summary["total_tokens"] == 500
    assert summary["average_latency_ms"] == 1000.0
    assert summary["tool_calls"]["brainstorm_itinerary"] == 1
    assert summary["tool_calls"]["generate_schedule"] == 1


def test_trace_tool_execution_span():
    """Verifies trace span execution wrapper."""
    span = trace_tool_execution(
        "spontaneous_recommendations", {"current_location": "Rome"}
    )
    assert span is not None
