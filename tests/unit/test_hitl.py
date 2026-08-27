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

"""Unit tests for Human-in-the-Loop (HITL) Execution Hooks and Approval Gates."""

from app.hitl.approval import (
    confirm_booking_reservation,
    request_itinerary_approval,
)


def test_confirm_booking_requires_human_approval():
    """Verifies that unconfirmed bookings return requires_human_approval status."""
    result = confirm_booking_reservation(
        item_type="Guided Tour",
        item_name="Colosseum Underground Special Access",
        estimated_price=120.0,
        travel_dates="2026-09-15 09:30 AM",
        user_confirmed=False,
    )

    assert result["status"] == "requires_human_approval"
    assert result["action_required"] == "CONFIRM_RESERVATION"
    assert "Colosseum Underground" in result["prompt_message"]
    assert result["estimated_price_usd"] == 120.0


def test_confirm_booking_confirmed_by_user():
    """Verifies that user confirmation locks in the booking."""
    result = confirm_booking_reservation(
        item_type="Hotel",
        item_name="Kyoto Traditional Ryokan",
        estimated_price=250.0,
        travel_dates="2026-10-01 to 2026-10-04",
        user_confirmed=True,
    )

    assert result["status"] == "confirmed"
    assert "CONF-" in result["confirmation_code"]
    assert "Kyoto Traditional Ryokan" in result["message"]


def test_request_itinerary_approval_workflow():
    """Verifies itinerary approval gates for pending vs approved sign-offs."""
    # Pending sign-off
    pending = request_itinerary_approval(
        destination="Rome",
        total_days=3,
        itinerary_summary="Day 1: Colosseum, Day 2: Vatican, Day 3: Trastevere",
        user_approved=False,
    )
    assert pending["status"] == "pending_review"
    assert pending["action_required"] == "APPROVE_ITINERARY"

    # Approved sign-off
    approved = request_itinerary_approval(
        destination="Rome",
        total_days=3,
        itinerary_summary="Day 1: Colosseum, Day 2: Vatican, Day 3: Trastevere",
        user_approved=True,
    )
    assert approved["status"] == "approved"
    assert "approved" in approved["message"].lower()
