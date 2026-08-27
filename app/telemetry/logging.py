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

"""Structured JSON logging formatter with OpenTelemetry trace correlation."""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from opentelemetry import trace

SEVERITY_MAP = {
    "DEBUG": "DEBUG",
    "INFO": "INFO",
    "WARNING": "WARNING",
    "ERROR": "ERROR",
    "CRITICAL": "CRITICAL",
}


class StructuredJsonFormatter(logging.Formatter):
    """Formats log records into structured JSON compliant with Google Cloud Logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "severity": SEVERITY_MAP.get(record.levelname, "DEFAULT"),
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Correlate OpenTelemetry trace and span IDs if active
        span = trace.get_current_span()
        if span and span.is_recording():
            span_ctx = span.get_span_context()
            if span_ctx.is_valid:
                log_entry["logging.googleapis.com/trace"] = format(
                    span_ctx.trace_id, "032x"
                )
                log_entry["logging.googleapis.com/spanId"] = format(
                    span_ctx.span_id, "016x"
                )
                log_entry["logging.googleapis.com/trace_sampled"] = (
                    span_ctx.trace_flags.sampled
                )

        # Capture custom structured event attributes if passed in extra
        if hasattr(record, "event_type"):
            log_entry["event_type"] = record.event_type

        if hasattr(record, "attributes") and isinstance(record.attributes, dict):
            log_entry["attributes"] = record.attributes

        # Capture exception details
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def setup_structured_logging(level: int = logging.INFO) -> logging.Logger:
    """Configures the root logger with StructuredJsonFormatter."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers if already configured
    for handler in list(root_logger.handlers):
        if isinstance(handler.formatter, StructuredJsonFormatter):
            return root_logger
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJsonFormatter())
    root_logger.addHandler(handler)
    return root_logger


def log_structured(
    logger: logging.Logger,
    level: int,
    message: str,
    event_type: str | None = None,
    **kwargs: Any,
) -> None:
    """Helper to log a message with structured attributes and event_type."""
    extra: dict[str, Any] = {}
    if event_type:
        extra["event_type"] = event_type
    if kwargs:
        extra["attributes"] = kwargs
    logger.log(level, message, extra=extra)
