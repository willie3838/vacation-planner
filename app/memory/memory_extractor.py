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

"""Memory extraction and Vertex AI Memory Bank integration."""

import logging

from google.adk.agents.callback_context import CallbackContext
from google.genai import types

logger = logging.getLogger(__name__)

PREFERENCE_KEYWORDS = {
    "diet": [
        "vegan",
        "vegetarian",
        "gluten-free",
        "kosher",
        "halal",
        "pescatarian",
        "dairy-free",
        "nut allergy",
    ],
    "budget": [
        "budget",
        "backpacker",
        "hostel",
        "affordable",
        "cheap",
        "luxury",
        "5-star",
        "fine dining",
        "splurge",
    ],
    "pace": ["relaxed", "slow", "easy-going", "intense", "fast-paced", "packed"],
    "dislikes": [
        "hate crowds",
        "no tourist traps",
        "avoid lines",
        "dislike museums",
        "no buses",
    ],
}


def extract_traveler_preferences_from_text(text: str) -> dict[str, list[str]]:
    """Programmatically extracts traveler preference tags from conversation text."""
    lower_text = text.lower()
    extracted = {
        "dietary_restrictions": [],
        "budget_hints": [],
        "pacing_hints": [],
        "dislikes_and_avoidances": [],
    }

    for diet in PREFERENCE_KEYWORDS["diet"]:
        if diet in lower_text:
            extracted["dietary_restrictions"].append(diet)

    for budget in PREFERENCE_KEYWORDS["budget"]:
        if budget in lower_text:
            extracted["budget_hints"].append(budget)

    for pace in PREFERENCE_KEYWORDS["pace"]:
        if pace in lower_text:
            extracted["pacing_hints"].append(pace)

    for dislike in PREFERENCE_KEYWORDS["dislikes"]:
        if dislike in lower_text:
            extracted["dislikes_and_avoidances"].append(dislike)

    return extracted


async def generate_memories_callback(
    callback_context: CallbackContext,
) -> types.Content | None:
    """Callback executed after agent turn to ingest conversation into Vertex AI Memory Bank.

    Args:
        callback_context: ADK CallbackContext containing session state and events.

    Returns:
        None to proceed normally without modifying agent response.
    """
    try:
        # Ingest session into Google Cloud Vertex AI Memory Bank
        await callback_context.add_session_to_memory()
        logger.info("Successfully triggered Vertex AI Memory Bank session ingestion.")
    except Exception as e:
        logger.warning(
            "Memory Bank session ingestion caught exception (handled gracefully): %s", e
        )

    return None
