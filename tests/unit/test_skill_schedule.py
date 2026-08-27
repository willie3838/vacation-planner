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

"""Unit tests for Skill 2: Generate Schedule (3 Positive + 3 Negative)."""

import pytest

from app.tools.schedule import generate_schedule

# --- Positive Test Cases (3 Cases) ---


def test_generate_schedule_transit_buffers_and_timelines():
    """Positive 1: Generates daily timeline with transit buffers between POIs."""
    activities = [
        {
            "name": "Colosseum Tour",
            "location": "Piazza del Colosseo",
            "duration_minutes": 120,
            "estimated_cost": "$30",
        },
        {
            "name": "Roman Forum Walk",
            "location": "Via della Salara Vecchia",
            "duration_minutes": 90,
            "estimated_cost": "$15",
        },
        {
            "name": "Trevi Fountain",
            "location": "Piazza di Trevi",
            "duration_minutes": 45,
            "estimated_cost": "Free",
        },
    ]
    result = generate_schedule(
        destination="Rome",
        days_count=1,
        selected_activities=activities,
        pace="balanced",
        lodging_area="Monti Neighborhood",
    )
    assert result["status"] == "success"
    assert len(result["days"]) == 1

    day_1 = result["days"][0]
    assert len(day_1["timeline"]) == 3
    # Check transit buffer calculated
    assert day_1["timeline"][0]["transit_from_prior_minutes"] == 20
    assert day_1["timeline"][1]["transit_from_prior_minutes"] == 25
    assert "copy_pastable_markdown" in result
    assert "### Day 1" in result["copy_pastable_markdown"]


def test_generate_schedule_anchored_lodging_hub():
    """Positive 2: Custom lodging hub anchors start and end points of the day."""
    activities = [
        {
            "name": "Shibuya Sky",
            "location": "Shibuya Scramble Square",
            "duration_minutes": 90,
        },
        {
            "name": "Meiji Shrine",
            "location": "Yoyogikamizonocho",
            "duration_minutes": 120,
        },
    ]
    result = generate_schedule(
        destination="Tokyo",
        days_count=1,
        selected_activities=activities,
        pace="balanced",
        lodging_area="Shinjuku Hotel",
    )
    assert result["lodging_area"] == "Shinjuku Hotel"
    assert (
        result["days"][0]["timeline"][0]["transit_from_prior_location"]
        == "Shinjuku Hotel"
    )


def test_generate_schedule_relaxed_pacing_limit():
    """Positive 3: Relaxed pace allocates at most 2 activities per day."""
    activities = [
        {"name": f"Activity {i}", "location": f"Spot {i}", "duration_minutes": 60}
        for i in range(6)
    ]
    result = generate_schedule(
        destination="Kyoto",
        days_count=3,
        selected_activities=activities,
        pace="relaxed",
        lodging_area="Gion",
    )
    assert result["pace"] == "relaxed"
    for day in result["days"]:
        assert len(day["timeline"]) <= 2


# --- Negative Test Cases (3 Cases) ---


def test_generate_schedule_empty_activities_raises_error():
    """Negative 1: Empty activities list raises ValueError."""
    with pytest.raises(ValueError, match="Selected activities list cannot be empty"):
        generate_schedule(
            destination="Rome",
            days_count=2,
            selected_activities=[],
            pace="balanced",
            lodging_area="City Center",
        )


def test_generate_schedule_overcrowded_warning():
    """Negative 2: Overcrowded day (>6 activities/day) returns pacing warning alert."""
    activities = [
        {
            "name": f"Rush Activity {i}",
            "location": f"Location {i}",
            "duration_minutes": 60,
        }
        for i in range(8)
    ]
    result = generate_schedule(
        destination="Paris",
        days_count=1,
        selected_activities=activities,
        pace="fast",
        lodging_area="Le Marais",
    )
    assert result["status"] == "success"
    assert result["pacing_warning"] is not None
    assert "Overcrowded schedule" in result["pacing_warning"]


def test_generate_schedule_invalid_destination_raises_error():
    """Negative 3: Blank destination or invalid day count raises ValueError."""
    with pytest.raises(ValueError, match="Destination cannot be empty"):
        generate_schedule(
            destination="   ",
            days_count=1,
            selected_activities=[{"name": "Sight"}],
            pace="balanced",
            lodging_area="Center",
        )
    with pytest.raises(ValueError, match="Days count must be positive"):
        generate_schedule(
            destination="London",
            days_count=-1,
            selected_activities=[{"name": "Sight"}],
            pace="balanced",
            lodging_area="Center",
        )
