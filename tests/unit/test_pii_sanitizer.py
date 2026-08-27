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

"""Unit tests for PII Sanitization and Redaction engine."""

from app.memory.pii_sanitizer import PIISanitizer


def test_sanitize_email_redaction():
    """Verifies that email addresses are properly redacted."""
    text = "Please send confirmation to traveler.john@gmail.com and support@travelcorp.org."
    sanitized, redacted = PIISanitizer.sanitize_text(text)

    assert "traveler.john@gmail.com" not in sanitized
    assert "support@travelcorp.org" not in sanitized
    assert "[EMAIL_REDACTED]" in sanitized
    assert "EMAIL" in redacted


def test_sanitize_phone_redaction():
    """Verifies that phone numbers in various formats are redacted."""
    text = "Call me at +1-416-555-0199 or (555) 234-5678 when we arrive."
    sanitized, redacted = PIISanitizer.sanitize_text(text)

    assert "416-555-0199" not in sanitized
    assert "(555) 234-5678" not in sanitized
    assert "[PHONE_REDACTED]" in sanitized
    assert "PHONE" in redacted


def test_sanitize_ssn_and_passport():
    """Verifies SSN and Passport number redaction."""
    text = "My SSN is 123-45-6789 and passport number is AB1234567."
    sanitized, redacted = PIISanitizer.sanitize_text(text)

    assert "123-45-6789" not in sanitized
    assert "AB1234567" not in sanitized
    assert "[ID_REDACTED]" in sanitized
    assert "SSN" in redacted or "PASSPORT" in redacted


def test_sanitize_credit_card():
    """Verifies that valid credit card patterns are redacted."""
    # Standard Visa test number (4532 ... Luhn valid)
    text = "Pay using card 4532 0150 0000 0004 for booking."
    sanitized, redacted = PIISanitizer.sanitize_text(text)

    assert "4532 0150 0000 0004" not in sanitized
    assert "[CARD_REDACTED]" in sanitized
    assert "CREDIT_CARD" in redacted


def test_sanitize_street_address():
    """Verifies that street addresses are redacted."""
    text = "Pickup location is 123 Maple Street, Apt 4."
    sanitized, redacted = PIISanitizer.sanitize_text(text)

    assert "123 Maple Street" not in sanitized
    assert "[ADDRESS_REDACTED]" in sanitized
    assert "STREET_ADDRESS" in redacted


def test_sanitize_dict_recursive():
    """Verifies that nested dictionaries and lists are sanitized."""
    data = {
        "user_profile": {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "preferences": ["vegan", "budget"],
        },
        "notes": ["Contact at +1-800-555-1234", "Strictly gluten-free"],
    }
    sanitized_data, redacted_types = PIISanitizer.sanitize_dict(data)

    assert sanitized_data["user_profile"]["email"] == "[EMAIL_REDACTED]"
    assert "[PHONE_REDACTED]" in sanitized_data["notes"][0]
    assert sanitized_data["user_profile"]["preferences"] == ["vegan", "budget"]
    assert "EMAIL" in redacted_types
    assert "PHONE" in redacted_types


def test_sanitize_preserves_clean_travel_text():
    """Verifies that regular travel preferences without PII remain untouched."""
    text = "We want a 3-day relaxed itinerary in Tokyo on a backpacker budget with vegan food."
    sanitized, redacted = PIISanitizer.sanitize_text(text)

    assert sanitized == text
    assert len(redacted) == 0
