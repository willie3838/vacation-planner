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

"""Strategic Model Router for dynamic, task-complexity-aware model selection."""

import os
from enum import StrEnum

from google.adk.models import Gemini
from google.genai import types


class TaskComplexity(StrEnum):
    """Task complexity tiers for strategic model selection."""

    FAST_LOOKUP = (
        "FAST_LOOKUP"  # Low latency, high throughput (spontaneous, search, quick tags)
    )
    STANDARD_PLANNING = (
        "STANDARD_PLANNING"  # Balanced reasoning (brainstorming, activity curation)
    )
    COMPLEX_REASONING = "COMPLEX_REASONING"  # Deep reasoning (schedule optimization, constraint satisfaction)
    COORDINATOR = (
        "COORDINATOR"  # Orchestration, multi-agent dispatch, memory management
    )


DEFAULT_MODELS = {
    TaskComplexity.FAST_LOOKUP: os.getenv("FAST_MODEL", "gemini-2.5-flash"),
    TaskComplexity.STANDARD_PLANNING: os.getenv("PLANNING_MODEL", "gemini-3.7-flash"),
    TaskComplexity.COMPLEX_REASONING: os.getenv("REASONING_MODEL", "gemini-2.5-pro"),
    TaskComplexity.COORDINATOR: os.getenv("PRIMARY_MODEL", "gemini-3.7-flash"),
}


def get_model_name_for_task(task_type: TaskComplexity) -> str:
    """Returns the configured model string for a specific task complexity tier."""
    if task_type == TaskComplexity.FAST_LOOKUP:
        return os.getenv("FAST_MODEL", DEFAULT_MODELS[TaskComplexity.FAST_LOOKUP])
    elif task_type == TaskComplexity.COMPLEX_REASONING:
        return os.getenv(
            "REASONING_MODEL", DEFAULT_MODELS[TaskComplexity.COMPLEX_REASONING]
        )
    elif task_type == TaskComplexity.STANDARD_PLANNING:
        return os.getenv(
            "PLANNING_MODEL", DEFAULT_MODELS[TaskComplexity.STANDARD_PLANNING]
        )
    else:
        return os.getenv("PRIMARY_MODEL", DEFAULT_MODELS[TaskComplexity.COORDINATOR])


def get_gemini_model_for_task(
    task_type: TaskComplexity,
    max_retries: int = 3,
) -> Gemini:
    """Instantiates a Gemini model configured appropriately for the task complexity."""
    model_name = get_model_name_for_task(task_type)

    return Gemini(
        model=model_name,
        retry_options=types.HttpRetryOptions(attempts=max_retries),
    )
