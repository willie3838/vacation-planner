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

"""Search client helper for retrieving web and Reddit travel recommendations."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def search_web(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Simulates/executes search over web sources for travel guides."""
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    logger.info("Executing web search query: %s", query)
    return [
        {
            "title": f"Top Guide for {query.strip()}",
            "snippet": f"Comprehensive vacation guide and recommendations covering {query.strip()}.",
            "source": "web_grounding",
        }
    ]


def search_reddit_discussions(
    location: str, topic: str = "", limit: int = 5
) -> list[dict[str, Any]]:
    """Builds and executes Reddit-prioritized searches for local/lowkey spots."""
    if not location or not location.strip():
        raise ValueError("Location cannot be empty.")

    clean_loc = location.strip()
    subreddit_hint = clean_loc.split(",")[0].replace(" ", "").lower()
    query = f"site:reddit.com (r/travel OR r/{subreddit_hint}) \"{clean_loc}\" {topic} ('hidden gem' OR 'lowkey' OR 'local favorite' OR 'off the beaten path')"
    logger.info("Executing Reddit targeted query: %s", query)

    return [
        {
            "title": f"Reddit: Best lowkey and hidden spots in {clean_loc}",
            "snippet": f"Locals recommend relaxing, authentic places in {clean_loc} away from major crowds. {topic}",
            "source": "reddit_community",
            "query_used": query,
        }
    ]
