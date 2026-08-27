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

"""Specialist Sub-Agent for Spontaneous Lowkey Discovery."""

from google.adk.agents import Agent
from google.genai import types

from app.routing.model_router import TaskComplexity, get_gemini_model_for_task
from app.tools.spontaneity import spontaneous_recommendations

SPONTANEITY_INSTRUCTION = """
You are the Spontaneous Local Discovery Specialist of WanderlustAI.
Your purpose is to help travelers who are already at their destination discover uncrowded, lowkey,
and authentic spots (viewpoints, cafes, neighborhood strolls) grounded in Reddit community discussions.

Always invoke the `spontaneous_recommendations` tool to find lowkey local favorites.
"""

spontaneity_agent = Agent(
    name="spontaneous_explorer",
    description="Specialist agent for spontaneous, lowkey neighborhood discovery and authentic Reddit community recommendations.",
    model=get_gemini_model_for_task(TaskComplexity.FAST_LOOKUP),
    instruction=SPONTANEITY_INSTRUCTION,
    tools=[spontaneous_recommendations],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
    ),
)
