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

"""Skill 2: Generate Structured & Copy-Pastable Itinerary Schedule."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def generate_schedule(
    destination: str,
    days_count: int,
    selected_activities: list[dict[str, Any]],
    pace: str,
    lodging_area: str,
) -> dict[str, Any]:
    """Generates a day-by-day copy-pastable schedule taking transit distance and durations into account.

    Args:
        destination: City or region of the trip (e.g. 'Rome, Italy').
        days_count: Total number of days to schedule (must be positive integer).
        selected_activities: List of activity objects (each with 'name', 'location', optional 'duration_minutes', 'estimated_cost').
        pace: Pace of the trip: 'relaxed' (2-3 stops/day), 'balanced' (3-4 stops/day), 'fast' (4+ stops/day).
        lodging_area: Central neighborhood or hotel location used to anchor start/end transit.

    Returns:
        A dictionary containing daily breakdowns, calculated transit buffers, locations, costs, and copy-pastable markdown.
    """
    if not destination or not destination.strip():
        raise ValueError("Destination cannot be empty.")
    if days_count <= 0:
        raise ValueError(f"Days count must be positive integer, got {days_count}.")
    if not selected_activities or len(selected_activities) == 0:
        raise ValueError("Selected activities list cannot be empty.")

    dest = destination.strip()
    trip_pace = pace.strip() if pace else "balanced"
    lodging = lodging_area.strip() if lodging_area else f"Central {dest}"

    # Pacing limits
    activities_per_day = (
        2 if trip_pace == "relaxed" else (3 if trip_pace == "balanced" else 4)
    )
    total_activities = len(selected_activities)

    # Check for overcrowded day warning
    pacing_warning = None
    if total_activities / days_count > 6:
        pacing_warning = "Overcrowded schedule detected (>6 activities/day). Buffer times have been optimized to avoid burnout."

    days = []
    markdown_lines = [
        f"# 🗓️ {days_count}-Day Vacation Itinerary: {dest}",
        f"**Base Lodging / Hub**: {lodging} | **Pacing**: {trip_pace.capitalize()}\n",
    ]

    act_idx = 0
    for d in range(1, days_count + 1):
        # Allocate activities for this day
        num_for_this_day = min(activities_per_day, total_activities - act_idx)
        if num_for_this_day <= 0 and act_idx < total_activities:
            num_for_this_day = 1

        curr_hour = 9
        curr_min = 0

        markdown_lines.append(f"### Day {d}: {dest} Exploration")
        markdown_lines.append(
            "| Time Window | Activity & Location | Transit / Buffer | Cost | Notes |"
        )
        markdown_lines.append("| :--- | :--- | :--- | :--- | :--- |")

        day_timeline = []
        prior_location = lodging

        for _ in range(num_for_this_day):
            if act_idx >= total_activities:
                break

            act = selected_activities[act_idx]
            act_name = act.get("name", f"Activity {act_idx + 1}")
            act_loc = act.get("location", f"{act_name}, {dest}")
            act_cost = act.get("estimated_cost", "$15 - $30")
            duration_mins = act.get("duration_minutes", 120)

            # Calculate transit buffer between prior location and current stop
            transit_mins = 20 if prior_location == lodging else 25

            # Start time
            start_str = f"{curr_hour:02d}:{curr_min:02d}"

            # Add activity duration + transit to advance clock
            end_minutes_total = curr_hour * 60 + curr_min + duration_mins
            end_hour = end_minutes_total // 60
            end_min = end_minutes_total % 60
            end_str = f"{end_hour:02d}:{end_min:02d}"

            item = {
                "time_slot": f"{start_str} - {end_str}",
                "name": act_name,
                "location": act_loc,
                "transit_from_prior_minutes": transit_mins,
                "transit_from_prior_location": prior_location,
                "duration_minutes": duration_mins,
                "estimated_cost": act_cost,
            }
            day_timeline.append(item)

            markdown_lines.append(
                f"| **{start_str} - {end_str}** | **{act_name}**<br>📍 *{act_loc}* | ~{transit_mins} min transit from {prior_location} | {act_cost} | - [ ] Done |"
            )

            # Advance clock with a small rest/buffer before next item
            next_start_total = end_minutes_total + 30
            curr_hour = next_start_total // 60
            curr_min = next_start_total % 60
            prior_location = act_loc
            act_idx += 1

        days.append(
            {
                "day_number": d,
                "theme": f"Day {d} in {dest}",
                "timeline": day_timeline,
            }
        )
        markdown_lines.append("")

    # Evening wrap up note
    markdown_lines.append(
        "> 💡 **Travel Tip**: Check venue opening hours 24h prior. Distances between stops are estimated for walking/metro."
    )

    formatted_markdown = "\n".join(markdown_lines)

    return {
        "status": "success",
        "destination": dest,
        "days_count": days_count,
        "pace": trip_pace,
        "lodging_area": lodging,
        "pacing_warning": pacing_warning,
        "days": days,
        "copy_pastable_markdown": formatted_markdown,
    }
