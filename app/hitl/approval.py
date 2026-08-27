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

"""Human-in-the-Loop (HITL) execution hooks and approval gates."""

import logging
from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from app.telemetry.logging import log_structured

logger = logging.getLogger(__name__)

HIGH_VALUE_THRESHOLD_USD = 100.0


def confirm_booking_reservation(
    item_type: str,
    item_name: str,
    estimated_price: float,
    travel_dates: str,
    user_confirmed: bool = False,
) -> dict[str, Any]:
    """Requests explicit human-in-the-loop confirmation before locking in reservations or bookings.

    Args:
        item_type: Type of reservation (e.g. "Hotel", "Guided Tour", "Museum Pass", "Transit Ticket").
        item_name: Specific name of the venue or booking item (e.g. "Colosseum Underground Tour").
        estimated_price: Estimated price in USD (must be positive number).
        travel_dates: Target dates or time slot for the reservation.
        user_confirmed: Set to True ONLY if the human user has explicitly approved this specific reservation.

    Returns:
        Structured confirmation status or a pause request for human sign-off.
    """
    if not user_confirmed or (
        estimated_price >= HIGH_VALUE_THRESHOLD_USD and not user_confirmed
    ):
        log_structured(
            logger=logger,
            level=logging.INFO,
            message=f"Human approval required for {item_type}: {item_name} (${estimated_price:.2f})",
            event_type="hitl_approval_required",
            item_name=item_name,
            estimated_price=estimated_price,
            user_confirmed=user_confirmed,
        )
        return {
            "status": "requires_human_approval",
            "item_type": item_type,
            "item_name": item_name,
            "estimated_price_usd": estimated_price,
            "travel_dates": travel_dates,
            "prompt_message": (
                f"⚠️ **Human Approval Required**: Please confirm if you would like to proceed with "
                f"booking **{item_name}** ({item_type}) for **${estimated_price:.2f} USD** on **{travel_dates}**."
            ),
            "action_required": "CONFIRM_RESERVATION",
            "recovery_instruction": "Prompt the user with the prompt_message and wait for their explicit confirmation before re-calling this tool with user_confirmed=True.",
        }

    log_structured(
        logger=logger,
        level=logging.INFO,
        message=f"Human approval granted for {item_type}: {item_name}",
        event_type="hitl_approval_granted",
        item_name=item_name,
        estimated_price=estimated_price,
    )
    return {
        "status": "confirmed",
        "item_type": item_type,
        "item_name": item_name,
        "estimated_price_usd": estimated_price,
        "travel_dates": travel_dates,
        "confirmation_code": f"CONF-{abs(hash(item_name + travel_dates)) % 1000000:06d}",
        "message": f"Successfully confirmed and locked reservation for {item_name} on {travel_dates}.",
    }


def request_itinerary_approval(
    destination: str,
    total_days: int,
    itinerary_summary: str,
    user_approved: bool = False,
) -> dict[str, Any]:
    """Requests explicit human sign-off on a finalized multi-day vacation plan before archiving.

    Args:
        destination: Destination city/country.
        total_days: Number of planned days.
        itinerary_summary: High-level overview of daily activities.
        user_approved: Set to True if the human user has signed off on the plan.

    Returns:
        Structured approval status.
    """
    if not user_approved:
        return {
            "status": "pending_review",
            "destination": destination,
            "total_days": total_days,
            "prompt_message": (
                f"📋 **Review & Sign-off**: Here is your finalized {total_days}-day itinerary overview for **{destination}**:\n"
                f"{itinerary_summary}\n\n"
                "Would you like to lock in this plan or make any adjustments?"
            ),
            "action_required": "APPROVE_ITINERARY",
            "recovery_instruction": "Present the summary to the user and ask if they approve this plan.",
        }

    return {
        "status": "approved",
        "destination": destination,
        "total_days": total_days,
        "message": f"Itinerary for {destination} has been approved by traveler.",
    }


async def hitl_tool_callback(
    callback_context: CallbackContext,
) -> types.Content | None:
    """Callback intercepting tool executions to log HITL events."""
    log_structured(
        logger=logger,
        level=logging.INFO,
        message="Intercepting tool call for HITL audit verification",
        event_type="hitl_tool_audit",
    )
    return None
