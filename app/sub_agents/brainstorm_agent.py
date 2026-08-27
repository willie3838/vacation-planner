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

"""Specialist Sub-Agent for Itinerary Brainstorming."""

from google.adk.agents import Agent
from google.genai import types

from app.routing.model_router import TaskComplexity, get_gemini_model_for_task
from app.tools.brainstorm import brainstorm_itinerary

BRAINSTORM_INSTRUCTION = """
You are the Itinerary Brainstorming Specialist of WanderlustAI.
Your purpose is to research destinations, discover iconic landmarks, suggest authentic food walks,
estimate realistic budget tiers, and curate personalized activity ideas for travelers.

Always invoke the `brainstorm_itinerary` tool to ground your suggestions.
"""

brainstorm_agent = Agent(
    name="itinerary_brainstormer",
    description="Specialist agent for destination exploration, attraction brainstorming, daily budget tiers, and activity curation.",
    model=get_gemini_model_for_task(TaskComplexity.STANDARD_PLANNING),
    instruction=BRAINSTORM_INSTRUCTION,
    tools=[brainstorm_itinerary],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.4,
    ),
)
