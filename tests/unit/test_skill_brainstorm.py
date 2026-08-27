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

"""Unit tests for Skill 1: Brainstorm Itinerary (3 Positive + 3 Negative)."""

from unittest.mock import patch

from app.tools.brainstorm import brainstorm_itinerary

# --- Positive Test Cases (3 Cases) ---


def test_brainstorm_valid_destination_structure():
    """Positive 1: Valid destination and duration returns full structured payload."""
    result = brainstorm_itinerary(
        destination="Rome, Italy",
        duration_days=3,
        travel_style="cultural",
        interests="colosseum, art",
    )
    assert result["status"] == "success"
    assert result["destination"] == "Rome, Italy"
    assert result["duration_days"] == 3
    assert len(result["top_activities"]) >= 4

    # Check top activity schema
    first_act = result["top_activities"][0]
    assert "name" in first_act
    assert "best_time" in first_act
    assert "estimated_cost" in first_act
    assert "description" in first_act
    assert "estimated_daily_budget" in result


def test_brainstorm_foodie_style_filtering():
    """Positive 2: Foodie travel style assigns food categories and tags."""
    result = brainstorm_itinerary(
        destination="Tokyo, Japan",
        duration_days=2,
        travel_style="foodie",
        interests="ramen, sushi, izakaya",
    )
    assert result["status"] == "success"
    assert result["travel_style"] == "foodie"
    assert "ramen" in result["interests"]

    # Verify food activity exists
    categories = [act["category"] for act in result["top_activities"]]
    assert any("Food" in cat for cat in categories)


def test_brainstorm_multi_day_expansion():
    """Positive 3: Multi-day (5+ days) trip expands with museum and day-trip options."""
    result = brainstorm_itinerary(
        destination="Kyoto, Japan",
        duration_days=5,
        travel_style="relaxation",
        interests="temples, gardens",
    )
    assert result["status"] == "success"
    assert len(result["top_activities"]) >= 5
    activity_names = [act["name"] for act in result["top_activities"]]
    assert any("Day Trip" in name for name in activity_names)


# --- Negative Test Cases (3 Cases) ---


def test_brainstorm_empty_destination_returns_error_recovery():
    """Negative 1: Empty or whitespace destination returns structured guided recovery response."""
    result = brainstorm_itinerary(
        destination="   ",
        duration_days=3,
        travel_style="budget",
        interests="",
    )
    assert result["status"] == "error"
    assert result["error"] is not None
    assert "Destination cannot be empty" in result["error"]
    assert result["recovery_instruction"] is not None
    assert result.suggested_action == "PROMPT_USER_FOR_DESTINATION"


def test_brainstorm_invalid_duration_returns_error_recovery():
    """Negative 2: Zero or negative duration returns structured guided recovery response."""
    result_zero = brainstorm_itinerary(
        destination="Paris, France",
        duration_days=0,
        travel_style="balanced",
        interests="art",
    )
    assert result_zero["status"] == "error"
    assert result_zero["recovery_instruction"] is not None
    assert result_zero.suggested_action == "PROMPT_USER_FOR_DURATION"

    result_neg = brainstorm_itinerary(
        destination="Paris, France",
        duration_days=-3,
        travel_style="balanced",
        interests="art",
    )
    assert result_neg["status"] == "error"
    assert result_neg["recovery_instruction"] is not None


@patch(
    "app.tools.brainstorm.search_web",
    side_effect=RuntimeError("Search API unavailable"),
)
def test_brainstorm_search_failure_graceful_fallback(mock_search):
    """Negative 3: Search engine outage recovers with local fallback without crash."""
    result = brainstorm_itinerary(
        destination="London, UK",
        duration_days=2,
        travel_style="sightseeing",
        interests="museums",
    )
    assert result["status"] == "success"
    assert len(result["top_activities"]) >= 3
    assert result["destination"] == "London, UK"
