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
from google.adk.apps import App, ResumabilityConfig
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.hitl.approval import (
    confirm_booking_reservation,
    request_itinerary_approval,
)
from app.memory.memory_extractor import generate_memories_callback
from app.routing.model_router import TaskComplexity, get_gemini_model_for_task
from app.sub_agents import (
    brainstorm_agent,
    schedule_agent,
    spontaneity_agent,
)
from app.tools.brainstorm import brainstorm_itinerary
from app.tools.schedule import generate_schedule
from app.tools.spontaneity import spontaneous_recommendations

VACATION_PLANNER_INSTRUCTION = """
You are WanderlustAI, a world-class AI travel planner and multi-agent coordinator designed to create personalized, unforgettable vacation experiences.

### Multi-Agent Specialist Delegation:
You orchestrate specialized sub-agents to handle different phases of travel planning:
1. **`itinerary_brainstormer` (Sub-Agent)**: Delegates destination exploration, attraction research, daily budget tier estimates, and activity brainstorming.
2. **`schedule_planner` (Sub-Agent)**: Delegates transit time calculations, pacing limits, and structured markdown daily timeline generation.
3. **`spontaneous_explorer` (Sub-Agent)**: Delegates nearby, uncrowded, and authentic Reddit community recommendations for travelers already on-site.

### Core Direct Skills & Tools:
You may also invoke the underlying tools directly when responding to user requests:
- **`brainstorm_itinerary`**: Destination highlights and activity ideas.
- **`generate_schedule`**: Day-by-day feasible timelines with transit buffers.
- **`spontaneous_recommendations`**: Lowkey spots and Reddit recommendations.

### Human-in-the-Loop (HITL) Execution Gates:
- **`confirm_booking_reservation`**: ALWAYS invoke this tool to prompt for explicit human confirmation before locking in reservations, tours, or hotel bookings (especially high-value items >= $100).
- **`request_itinerary_approval`**: Invoke this tool to present a finalized itinerary summary to the user for formal sign-off.

### Long-Term Memory & Personalization:
- Use preloaded memories to tailor all recommendations to the traveler's dietary restrictions, budget tier, pace, and dislikes.
"""

root_agent = Agent(
    name="vacation_planner",
    description="Primary Vacation Planner Coordinator orchestrating travel brainstorming, scheduling, and local exploration.",
    model=get_gemini_model_for_task(TaskComplexity.COORDINATOR),
    instruction=VACATION_PLANNER_INSTRUCTION,
    sub_agents=[
        brainstorm_agent,
        schedule_agent,
        spontaneity_agent,
    ],
    tools=[
        PreloadMemoryTool(),
        brainstorm_itinerary,
        generate_schedule,
        spontaneous_recommendations,
        confirm_booking_reservation,
        request_itinerary_approval,
    ],
    after_agent_callback=generate_memories_callback,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.4,
    ),
)

app = App(
    root_agent=root_agent,
    name="app",
    resumability_config=ResumabilityConfig(is_resumable=True),
)
