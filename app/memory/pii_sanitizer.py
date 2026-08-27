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

"""PII Sanitization and Redaction engine for memory pipelines and logging."""

import re
from typing import Any

# Regular Expression Patterns for Sensitive PII
PATTERNS = {
    "EMAIL": (
        re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b", re.IGNORECASE
        ),
        "[EMAIL_REDACTED]",
    ),
    "CREDIT_CARD": (
        re.compile(r"\b(?:\d{4}[ -]?){3}\d{1,7}\b|\b\d{13,19}\b"),
        "[CARD_REDACTED]",
    ),
    "PHONE": (
        re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
        "[PHONE_REDACTED]",
    ),
    "SSN": (
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "[ID_REDACTED]",
    ),
    "PASSPORT": (
        re.compile(r"\b[A-Z]{1,2}[0-9]{7,9}\b"),
        "[ID_REDACTED]",
    ),
    "STREET_ADDRESS": (
        re.compile(
            r"\b\d{1,6}\s+[A-Za-z0-9\s.,-]+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Lane|Ln|Way|Court|Ct)\b",
            re.IGNORECASE,
        ),
        "[ADDRESS_REDACTED]",
    ),
    "API_SECRET": (
        re.compile(
            r"\b(?:ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|AIza[0-9A-Za-z-_]{35}|sk-[A-Za-z0-9]{32,})\b"
        ),
        "[SECRET_REDACTED]",
    ),
}


class PIISanitizer:
    """Detects and redacts sensitive PII from text, messages, and structured state."""

    @classmethod
    def sanitize_text(cls, text: str) -> tuple[str, list[str]]:
        """Redacts sensitive PII from a string.

        Returns:
            Tuple of (sanitized_text, list_of_redacted_entity_types).
        """
        if not text or not isinstance(text, str):
            return text, []

        redacted_types: list[str] = []
        sanitized = text

        # 1. Email Redaction
        if PATTERNS["EMAIL"][0].search(sanitized):
            sanitized = PATTERNS["EMAIL"][0].sub(PATTERNS["EMAIL"][1], sanitized)
            redacted_types.append("EMAIL")

        # 2. API Secrets
        if PATTERNS["API_SECRET"][0].search(sanitized):
            sanitized = PATTERNS["API_SECRET"][0].sub(
                PATTERNS["API_SECRET"][1], sanitized
            )
            redacted_types.append("API_SECRET")

        # 3. SSN & National ID
        if PATTERNS["SSN"][0].search(sanitized):
            sanitized = PATTERNS["SSN"][0].sub(PATTERNS["SSN"][1], sanitized)
            redacted_types.append("SSN")

        # 4. Street Address
        if PATTERNS["STREET_ADDRESS"][0].search(sanitized):
            sanitized = PATTERNS["STREET_ADDRESS"][0].sub(
                PATTERNS["STREET_ADDRESS"][1], sanitized
            )
            redacted_types.append("STREET_ADDRESS")

        # 5. Credit Cards (13-19 digits formatted or raw)
        for match in list(PATTERNS["CREDIT_CARD"][0].finditer(sanitized)):
            raw_match = match.group()
            digits = "".join(c for c in raw_match if c.isdigit())
            if 13 <= len(digits) <= 19:
                sanitized = sanitized.replace(raw_match, PATTERNS["CREDIT_CARD"][1])
                if "CREDIT_CARD" not in redacted_types:
                    redacted_types.append("CREDIT_CARD")

        # 6. Phone Numbers (after credit cards & addresses to avoid sub-matching)
        if PATTERNS["PHONE"][0].search(sanitized):
            sanitized = PATTERNS["PHONE"][0].sub(PATTERNS["PHONE"][1], sanitized)
            redacted_types.append("PHONE")

        # 7. Passport
        if PATTERNS["PASSPORT"][0].search(sanitized):
            for match in PATTERNS["PASSPORT"][0].finditer(sanitized):
                val = match.group()
                if re.match(r"^[A-Z]{1,2}[0-9]{7,9}$", val):
                    sanitized = sanitized.replace(val, PATTERNS["PASSPORT"][1])
                    if "PASSPORT" not in redacted_types:
                        redacted_types.append("PASSPORT")

        return sanitized, redacted_types

    @classmethod
    def sanitize_dict(cls, data: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Recursively redacts PII from dictionaries and lists."""
        all_redacted: list[str] = []

        def _recursive_sanitize(item: Any) -> Any:
            if isinstance(item, str):
                cleaned, redacted = cls.sanitize_text(item)
                all_redacted.extend(redacted)
                return cleaned
            elif isinstance(item, dict):
                return {k: _recursive_sanitize(v) for k, v in item.items()}
            elif isinstance(item, list):
                return [_recursive_sanitize(elem) for elem in item]
            return item

        sanitized_data = _recursive_sanitize(data)
        return sanitized_data, list(set(all_redacted))
