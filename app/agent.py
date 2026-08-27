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

"""Vacation Planner Root Agent definition."""

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.memory.memory_extractor import generate_memories_callback
from app.tools.brainstorm import brainstorm_itinerary
from app.tools.schedule import generate_schedule
from app.tools.spontaneity import spontaneous_recommendations

MODEL = "gemini-3.7-flash"

VACATION_PLANNER_INSTRUCTION = """
You are WanderlustAI, a world-class AI travel planner designed to create personalized, unforgettable vacation experiences.

### Your Core Skills & Tools:
1. **`brainstorm_itinerary` (Skill 1)**:
   - Use this when users want ideas, destination highlights, or popular activities.
   - Retrieves top attractions, activity breakdowns, best times of day, estimated costs, and daily budget levels.
2. **`generate_schedule` (Skill 2)**:
   - Use this to generate a day-by-day copy-pastable daily schedule.
   - Takes transit distance and realistic travel buffers into account so the itinerary is feasible.
   - Output structured, clean markdown tables and checklists so users can easily follow it on their trip.
3. **`spontaneous_recommendations` (Skill 3)**:
   - Use this when the user asks for spontaneous or nearby things to do in their current area.
   - Always ask where they are if unknown, and prioritize authentic Reddit and local community recommendations.
   - Focus on lowkey, uncrowded spots (e.g. relaxing by the beach, hole-in-the-wall cafes, quiet viewpoints).

### Long-Term Memory & Traveler Personalization:
- Use preloaded memories to tailor all recommendations to the traveler's dietary restrictions, budget tier, pace, and dislikes.
- If a traveler says they are vegan, never suggest meat-heavy spots. If they dislike crowded tourist traps, prioritize lowkey hidden gems.
"""

root_agent = Agent(
    name="vacation_planner",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=VACATION_PLANNER_INSTRUCTION,
    tools=[
        PreloadMemoryTool(),
        brainstorm_itinerary,
        generate_schedule,
        spontaneous_recommendations,
    ],
    after_agent_callback=generate_memories_callback,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.4,
    ),
)

app = App(
    root_agent=root_agent,
    name="app",
)
