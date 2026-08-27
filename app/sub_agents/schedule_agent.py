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

"""Specialist Sub-Agent for Daily Schedule and Transit Optimization."""

from google.adk.agents import Agent
from google.genai import types

from app.routing.model_router import TaskComplexity, get_gemini_model_for_task
from app.tools.schedule import generate_schedule

SCHEDULE_INSTRUCTION = """
You are the Schedule Optimization Specialist of WanderlustAI.
Your purpose is to organize activities into logical daily timelines, calculate realistic transit buffers
between points of interest, prevent schedule overcrowding, and generate clean copy-pastable markdown schedules.

Always invoke the `generate_schedule` tool to compute feasible daily itineraries.
"""

schedule_agent = Agent(
    name="schedule_planner",
    description="Specialist agent for schedule optimization, transit buffer calculation, pacing, and day-by-day markdown timeline generation.",
    model=get_gemini_model_for_task(TaskComplexity.COMPLEX_REASONING),
    instruction=SCHEDULE_INSTRUCTION,
    tools=[generate_schedule],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
    ),
)
