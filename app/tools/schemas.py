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

"""Strict Pydantic schemas and error models for Vacation Planner tools."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolResponseBase(BaseModel):
    """Base tool response supporting attribute access and dict subscripting for backward compatibility."""

    status: Literal["success", "error"] = Field(
        ..., description="Execution status: success or error"
    )
    error: str | None = Field(
        default=None, description="Error message if execution failed"
    )
    recovery_instruction: str | None = Field(
        default=None,
        description="Actionable instructions guiding the LLM how to recover and what to prompt the user for",
    )
    suggested_action: str | None = Field(
        default=None, description="Machine-readable recovery action code"
    )

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


# --- Skill 1: Brainstorm Schemas ---


class ActivityItem(BaseModel):
    """Structured representation of a single recommended activity."""

    name: str = Field(..., description="Name of the activity or attraction")
    category: str = Field(
        ..., description="Category (e.g. Culture, Food & Dining, Scenic)"
    )
    best_time: str = Field(
        ..., description="Recommended time window (e.g. Morning 09:00 - 12:30)"
    )
    estimated_cost: str = Field(..., description="Estimated cost per person or free")
    description: str = Field(..., description="Detailed description of the spot")
    style_tags: list[str] = Field(
        default_factory=list, description="Associated style and interest tags"
    )

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class BrainstormResponse(ToolResponseBase):
    """Output schema for brainstorm_itinerary tool."""

    destination: str | None = Field(default=None, description="Destination city/region")
    duration_days: int | None = Field(
        default=None, description="Number of vacation days"
    )
    travel_style: str | None = Field(default=None, description="Travel style")
    interests: list[str] = Field(
        default_factory=list, description="Parsed traveler interests"
    )
    top_activities: list[ActivityItem] = Field(
        default_factory=list, description="Curated activity list"
    )
    estimated_daily_budget: dict[str, str] = Field(
        default_factory=dict, description="Estimated budget breakdown"
    )
    search_grounding: list[dict[str, Any]] = Field(
        default_factory=list, description="Online search citations"
    )


# --- Skill 2: Schedule Schemas ---


class TimelineItem(BaseModel):
    """Single scheduled event in a daily timeline."""

    time_slot: str = Field(..., description="Time window (e.g. 09:00 - 11:00)")
    name: str = Field(..., description="Activity name")
    location: str = Field(..., description="Activity location / address")
    transit_from_prior_minutes: int = Field(
        ..., description="Transit buffer minutes from previous stop"
    )
    transit_from_prior_location: str = Field(
        ..., description="Starting point for transit calculation"
    )
    duration_minutes: int = Field(..., description="Duration at venue")
    estimated_cost: str = Field(..., description="Estimated cost")

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class ScheduleDay(BaseModel):
    """Daily schedule breakdown."""

    day_number: int = Field(..., description="Day number (1, 2, 3...)")
    theme: str = Field(..., description="Theme for the day")
    timeline: list[TimelineItem] = Field(
        default_factory=list, description="Chronological timeline of events"
    )

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class ScheduleResponse(ToolResponseBase):
    """Output schema for generate_schedule tool."""

    destination: str | None = Field(default=None, description="Trip destination")
    days_count: int | None = Field(default=None, description="Total days count")
    pace: str | None = Field(default=None, description="Trip pace")
    lodging_area: str | None = Field(default=None, description="Base lodging hub")
    pacing_warning: str | None = Field(
        default=None, description="Alert if day is overcrowded"
    )
    days: list[ScheduleDay] = Field(
        default_factory=list, description="Daily schedule breakdowns"
    )
    copy_pastable_markdown: str | None = Field(
        default=None, description="Formatted markdown table"
    )


# --- Skill 3: Spontaneity Schemas ---


class SpontaneousRecommendationItem(BaseModel):
    """Single spontaneous recommendation item."""

    name: str = Field(..., description="Name of spot or activity")
    vibe: str = Field(..., description="Atmosphere or vibe")
    description: str = Field(
        ..., description="Description highlighting why it is lowkey/authentic"
    )
    best_time_to_go: str = Field(..., description="Ideal timing or golden hour")
    estimated_cost: str = Field(..., description="Cost estimate")
    distance: str = Field(..., description="Estimated distance from current location")
    reddit_source: str = Field(..., description="Community discussion consensus source")

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class SpontaneousResponse(ToolResponseBase):
    """Output schema for spontaneous_recommendations tool."""

    current_location: str | None = Field(
        default=None, description="Current traveler location"
    )
    mood_or_preference: str | None = Field(
        default=None, description="Mood or preference"
    )
    radius: str | None = Field(default=None, description="Search radius")
    reddit_grounding: list[dict[str, Any]] = Field(
        default_factory=list, description="Reddit discussion citations"
    )
    recommendations: list[SpontaneousRecommendationItem] = Field(
        default_factory=list, description="Recommended spots"
    )
