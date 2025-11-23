"""
Centralized request input validation and sanitization utilities.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Mapping

from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Validates and sanitizes inbound request payloads to mitigate common attacks.
    - Detects suspicious SQL injection patterns.
    - Detects embedded scripts / inline JS handlers.
    - Enforces maximum field sizes.
    """

    SQLI_PATTERNS = [
        re.compile(r"(?i)(\bUNION\b\s+\bSELECT\b)"),
        re.compile(r"(?i)(\bDROP\b\s+(TABLE|DATABASE))"),
        re.compile(r"(?i)(\bALTER\b\s+(TABLE|DATABASE))"),
        re.compile(r"(?i)(\bINSERT\b\s+INTO\b.*\bSELECT\b)"),
        re.compile(r"(?i)(\bOR\b\s+1=1)"),
    ]

    XSS_PATTERNS = [
        re.compile(r"(?i)<\s*script"),
        re.compile(r"(?i)javascript:"),
        re.compile(r"(?i)on\w+\s*="),
    ]

    SCRIPT_STRIP_PATTERN = re.compile(r"<\s*script.*?>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL)
    NULL_BYTE_PATTERN = re.compile(r"\x00")

    def __init__(self, max_string_length: int = settings.MAX_INPUT_STRING_LENGTH):
        self.max_string_length = max_string_length

    def sanitize_payload(self, payload: Any, location: str = "body") -> Any:
        """
        Recursively walk the payload, sanitizing strings and validating primitives.
        """
        if isinstance(payload, dict):
            return {
                key: self.sanitize_payload(value, f"{location}.{key}")
                for key, value in payload.items()
            }

        if isinstance(payload, list):
            return [
                self.sanitize_payload(item, f"{location}[{idx}]")
                for idx, item in enumerate(payload)
            ]

        if isinstance(payload, str):
            return self._sanitize_string(payload, location)

        # Allowed primitive types (int, float, bool, None)
        return payload

    def validate_query_params(self, params: Mapping[str, str]) -> None:
        """
        Validate query parameters for malicious content.
        """
        for key, value in params.items():
            if value is None:
                continue
            self._sanitize_string(value, f"query.{key}")

    def validate_headers(self, headers: Mapping[str, str]) -> None:
        """
        Validate select headers (only those we care about for injections).
        """
        for header, value in headers.items():
            if header.lower() in {"x-user-context", "x-request-id"} and value:
                self._sanitize_string(value, f"header.{header}")

    def enforce_body_size(self, body: bytes) -> None:
        """
        Enforce maximum JSON body size to avoid abuse.
        """
        if len(body) > settings.MAX_JSON_PAYLOAD_BYTES:
            logger.warning("JSON payload exceeds max size: %s bytes", len(body))
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Payload exceeds maximum allowed size.",
            )

    def _sanitize_string(self, value: str, location: str) -> str:
        """
        Sanitize a string value and raise HTTPException when malicious patterns are detected.
        """
        stripped_value = value.strip()

        if len(stripped_value) > self.max_string_length:
            logger.warning("Input rejected: %s exceeds %s characters", location, self.max_string_length)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Input at {location} exceeds maximum allowed length.",
            )

        if self.NULL_BYTE_PATTERN.search(stripped_value):
            logger.warning("Input rejected due to NULL byte at %s", location)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Embedded NULL bytes are not allowed.",
            )

        for pattern in self.SQLI_PATTERNS:
            if pattern.search(stripped_value):
                logger.warning("SQL injection pattern detected in %s", location)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Suspicious input detected.",
                )

        for pattern in self.XSS_PATTERNS:
            if pattern.search(stripped_value):
                logger.warning("XSS pattern detected in %s", location)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Suspicious input detected.",
                )

        # Remove inline script blocks and compress whitespace for safe logging
        sanitized = self.SCRIPT_STRIP_PATTERN.sub("", stripped_value)
        sanitized = re.sub(r"[\r\n]+", " ", sanitized)
        return sanitized


input_validator = InputValidator()
