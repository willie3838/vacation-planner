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

"""Skill 1: Brainstorm Itineraries and Activities."""

import logging
from typing import Any

from app.tools.search_client import search_web

logger = logging.getLogger(__name__)


def brainstorm_itinerary(
    destination: str,
    duration_days: int,
    travel_style: str,
    interests: str,
) -> dict[str, Any]:
    """Retrieves popular online itineraries and brainstorms activities for a destination.

    Args:
        destination: City, region, or country to plan for (e.g. 'Rome, Italy', 'Kyoto, Japan').
        duration_days: Number of days planned for the vacation (must be positive integer).
        travel_style: Travel style preference (e.g. 'cultural', 'foodie', 'adventure', 'relaxation', 'budget').
        interests: Comma-separated specific interests (e.g. 'art, street food, temples, hiking').

    Returns:
        A dictionary containing the brainstormed itinerary, top activities, timing, costs, and descriptions.
    """
    if not destination or not destination.strip():
        raise ValueError("Destination cannot be empty.")
    if duration_days <= 0:
        raise ValueError(
            f"Duration days must be a positive integer, got {duration_days}."
        )

    dest = destination.strip()
    style = travel_style.strip() if travel_style else "balanced"
    interest_list = (
        [i.strip() for i in interests.split(",") if i.strip()] if interests else []
    )

    try:
        query = f"popular {duration_days}-day itinerary {dest} {style} {' '.join(interest_list)}"
        search_results = search_web(query)
    except Exception as e:
        logger.warning("Search lookup failed, using fallback knowledge: %s", e)
        search_results = [
            {"title": f"Fallback guide for {dest}", "source": "local_fallback"}
        ]

    # Generate curated activity clusters based on duration and style
    activities = []

    # Core iconic highlights
    activities.append(
        {
            "name": f"Historic Center & Iconic Landmarks of {dest}",
            "category": "Culture & Sightseeing"
            if "food" not in style.lower()
            else "Food & Culture Walk",
            "best_time": "Morning (09:00 - 12:30)",
            "estimated_cost": "$20 - $45 per person",
            "description": f"Explore the top architectural and cultural landmarks across central {dest}.",
            "style_tags": [style, "sightseeing", *interest_list[:2]],
        }
    )

    # Cuisine & Food experience
    activities.append(
        {
            "name": f"Local Gastronomy & Market Tour in {dest}",
            "category": "Food & Dining",
            "best_time": "Mid-Day / Lunch (13:00 - 15:00)",
            "estimated_cost": "$15 - $35 per person",
            "description": f"Sample authentic regional delicacies, street food, and vibrant local produce in {dest}.",
            "style_tags": ["foodie", "market", style],
        }
    )

    # Scenic / Relaxed / Cultural Afternoon
    activities.append(
        {
            "name": f"Scenic Neighborhood Stroll & Viewpoint in {dest}",
            "category": "Relaxation & Scenic",
            "best_time": "Late Afternoon / Sunset (16:30 - 19:00)",
            "estimated_cost": "Free - $10",
            "description": f"Walk through charming residential alleys and catch the sunset overlooking {dest}.",
            "style_tags": ["scenic", "sunset", "relaxation"],
        }
    )

    # Multi-day expansions
    if duration_days >= 3:
        activities.append(
            {
                "name": f"Museums & Art Discovery in {dest}",
                "category": "Arts & Heritage",
                "best_time": "Morning (10:00 - 13:00)",
                "estimated_cost": "$15 - $30 per person",
                "description": f"Visit prominent galleries and heritage exhibits showcasing the history of {dest}.",
                "style_tags": ["art", "museums", style],
            }
        )
        activities.append(
            {
                "name": f"Day Trip / Nature Escape near {dest}",
                "category": "Outdoors & Adventure",
                "best_time": "Full Day or Half Day (09:00 - 16:00)",
                "estimated_cost": "$40 - $80 per person (including transit)",
                "description": f"Venture slightly outside {dest} to explore nearby nature trails, coastlines, or historic towns.",
                "style_tags": ["nature", "day-trip", "adventure"],
            }
        )

    return {
        "status": "success",
        "destination": dest,
        "duration_days": duration_days,
        "travel_style": style,
        "interests": interest_list,
        "top_activities": activities,
        "estimated_daily_budget": {
            "budget": "$50 - $80 / day",
            "moderate": "$120 - $220 / day",
            "luxury": "$350+ / day",
        },
        "search_grounding": search_results,
    }
