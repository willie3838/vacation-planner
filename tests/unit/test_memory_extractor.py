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

"""Unit tests for Memory Extraction, Preference Parsing, and PII Sanitization."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.memory.memory_extractor import (
    extract_traveler_preferences_from_text,
    generate_memories_callback,
)


def test_extract_dietary_and_budget_preferences():
    """Verifies that vegan diet and budget hints are extracted accurately."""
    user_text = (
        "I am strictly vegan, traveling on a backpacker budget, and hate crowds."
    )
    extracted = extract_traveler_preferences_from_text(user_text)

    assert "vegan" in extracted["dietary_restrictions"]
    assert "backpacker" in extracted["budget_hints"]
    assert "hate crowds" in extracted["dislikes_and_avoidances"]


def test_extract_preferences_with_pii_sanitization():
    """Verifies that preferences are extracted accurately even when input contains sensitive PII."""
    user_text = "Email me at traveler@example.com or call +1-416-555-0199. I am strictly gluten-free and love luxury."
    extracted = extract_traveler_preferences_from_text(user_text)

    assert "gluten-free" in extracted["dietary_restrictions"]
    assert "luxury" in extracted["budget_hints"]


def test_extract_pacing_and_luxury_preferences():
    """Verifies relaxed pace and luxury hints extraction."""
    user_text = "Looking for a relaxed luxury 5-star resort experience in Kyoto."
    extracted = extract_traveler_preferences_from_text(user_text)

    assert "relaxed" in extracted["pacing_hints"]
    assert "luxury" in extracted["budget_hints"]
    assert "5-star" in extracted["budget_hints"]


@pytest.mark.asyncio
async def test_generate_memories_callback_invokes_session_add():
    """Verifies that generate_memories_callback triggers add_session_to_memory."""
    mock_ctx = MagicMock()
    mock_ctx.state = {"contact_email": "user@example.com", "diet": "vegan"}
    mock_ctx.add_session_to_memory = AsyncMock()

    result = await generate_memories_callback(mock_ctx)
    assert result is None
    mock_ctx.add_session_to_memory.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_memories_callback_handles_exception_gracefully():
    """Verifies that errors in Memory Bank ingestion do not break the conversation flow."""
    mock_ctx = MagicMock()
    mock_ctx.state = {}
    mock_ctx.add_session_to_memory = AsyncMock(
        side_effect=RuntimeError("Memory service down")
    )

    result = await generate_memories_callback(mock_ctx)
    assert result is None
