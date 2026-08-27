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

"""Unit tests for Strategic Model Router."""

import os
from unittest.mock import patch

from app.routing.model_router import (
    TaskComplexity,
    get_gemini_model_for_task,
    get_model_name_for_task,
)


def test_default_model_routing_tiers():
    """Verifies default model mappings for task complexity tiers."""
    fast_model = get_model_name_for_task(TaskComplexity.FAST_LOOKUP)
    assert "flash" in fast_model.lower()

    planning_model = get_model_name_for_task(TaskComplexity.STANDARD_PLANNING)
    assert "flash" in planning_model.lower() or "pro" in planning_model.lower()

    reasoning_model = get_model_name_for_task(TaskComplexity.COMPLEX_REASONING)
    assert "pro" in reasoning_model.lower() or "flash" in reasoning_model.lower()

    coord_model = get_model_name_for_task(TaskComplexity.COORDINATOR)
    assert coord_model is not None


def test_environment_override_model_routing():
    """Verifies that environment variables dynamically override model tiers."""
    with patch.dict(
        os.environ,
        {
            "FAST_MODEL": "custom-fast-model",
            "REASONING_MODEL": "custom-reasoning-model",
        },
    ):
        assert (
            get_model_name_for_task(TaskComplexity.FAST_LOOKUP) == "custom-fast-model"
        )
        assert (
            get_model_name_for_task(TaskComplexity.COMPLEX_REASONING)
            == "custom-reasoning-model"
        )


def test_get_gemini_model_for_task_instance():
    """Verifies Gemini model instance creation with retries."""
    model_instance = get_gemini_model_for_task(
        TaskComplexity.COORDINATOR, max_retries=5
    )
    assert model_instance is not None
    assert model_instance.model is not None
