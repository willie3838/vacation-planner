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

"""Unit tests for Skill 3: Spontaneity & Reddit Recommendations (3 Positive + 3 Negative)."""

from unittest.mock import patch

import pytest

from app.tools.spontaneity import spontaneous_recommendations

# --- Positive Test Cases (3 Cases) ---


def test_spontaneity_valid_location_and_mood():
    """Positive 1: Valid location and mood returns Reddit-backed recommendations."""
    result = spontaneous_recommendations(
        current_location="Trastevere, Rome",
        mood_or_preference="cozy cafe and book reading",
        radius="walking distance",
    )
    assert result["status"] == "success"
    assert result["current_location"] == "Trastevere, Rome"
    assert len(result["recommendations"]) >= 3

    first_rec = result["recommendations"][0]
    assert "name" in first_rec
    assert "vibe" in first_rec
    assert "best_time_to_go" in first_rec
    assert "estimated_cost" in first_rec
    assert "reddit_source" in first_rec


def test_spontaneity_lowkey_scenic_spot_tagging():
    """Positive 2: Identifies scenic viewpoint and tags it as lowkey / free ($0)."""
    result = spontaneous_recommendations(
        current_location="Silver Lake, Los Angeles",
        mood_or_preference="sunset views",
        radius="under 2 miles",
    )
    assert result["status"] == "success"
    scenic_recs = [
        rec
        for rec in result["recommendations"]
        if "Scenic" in rec["name"] or "Sunset" in rec["name"]
    ]
    assert len(scenic_recs) > 0
    assert scenic_recs[0]["estimated_cost"] == "$0 / Free"


def test_spontaneity_walking_distance_radius():
    """Positive 3: Walking distance radius parameter is preserved and formatted."""
    result = spontaneous_recommendations(
        current_location="Shibuya, Tokyo",
        mood_or_preference="late night street food",
        radius="walking distance",
    )
    assert result["radius"] == "walking distance"
    assert any("walk" in rec["distance"].lower() for rec in result["recommendations"])


# --- Negative Test Cases (3 Cases) ---


def test_spontaneity_blank_location_raises_error():
    """Negative 1: Blank current location raises ValueError."""
    with pytest.raises(ValueError, match="Current location cannot be empty"):
        spontaneous_recommendations(
            current_location="   ",
            mood_or_preference="coffee",
            radius="walking distance",
        )


def test_spontaneity_empty_mood_defaults_gracefully():
    """Negative 2: Empty or None mood defaults to relaxing and lowkey."""
    result = spontaneous_recommendations(
        current_location="Mission District, San Francisco",
        mood_or_preference="",
        radius="",
    )
    assert result["status"] == "success"
    assert result["mood_or_preference"] == "relaxing and lowkey"
    assert result["radius"] == "walking distance"


@patch(
    "app.tools.spontaneity.search_reddit_discussions",
    side_effect=RuntimeError("Reddit API timeout"),
)
def test_spontaneity_search_error_fallback(mock_reddit):
    """Negative 3: Reddit network error falls back gracefully to community recommendations."""
    result = spontaneous_recommendations(
        current_location="Santorini, Greece",
        mood_or_preference="beach chilling",
        radius="walking distance",
    )
    assert result["status"] == "success"
    assert len(result["recommendations"]) >= 3
    assert result["current_location"] == "Santorini, Greece"
