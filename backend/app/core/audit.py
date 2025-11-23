"""
Structured audit logging helpers.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import settings


class AuditLogger:
    """
    JSON-line audit logger that records security-sensitive events.
    """

    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._logger = logging.getLogger("audit")
        if not self._logger.handlers:
            handler = logging.FileHandler(self.log_path, encoding="utf-8")
            handler.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)
            self._logger.propagate = False

    def log_event(
        self,
        event_type: str,
        *,
        user_id: Optional[str] = None,
        ip: Optional[str] = None,
        path: Optional[str] = None,
        method: Optional[str] = None,
        status_code: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "user_id": user_id,
            "ip": ip,
            "path": path,
            "method": method,
            "status_code": status_code,
            "metadata": metadata or {},
            "request_id": request_id,
        }
        self._logger.info(json.dumps(entry, default=str))

    def log_auth_event(
        self,
        *,
        action: str,
        result: str,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        ip: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        event_metadata = metadata.copy() if metadata else {}
        if email:
            event_metadata.setdefault("email", email)
        event_metadata["result"] = result
        self.log_event(
            event_type=f"auth.{action}",
            user_id=user_id,
            ip=ip,
            metadata=event_metadata,
            request_id=request_id,
        )

    def log_data_access(
        self,
        *,
        resource: str,
        action: str,
        user_id: Optional[str],
        metadata: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        event_metadata = metadata.copy() if metadata else {}
        event_metadata["resource"] = resource
        event_metadata["action"] = action
        self.log_event(
            event_type="data.access",
            user_id=user_id,
            metadata=event_metadata,
            request_id=request_id,
        )


audit_logger = AuditLogger(settings.AUDIT_LOG_PATH)

__all__ = ["audit_logger", "AuditLogger"]



