from __future__ import annotations

from fastapi import HTTPException, status


class AnalyticsError(Exception):
    """Raised when portfolio calculations cannot be completed safely."""


def bad_request(message: str, details: dict | None = None) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error_code": "BAD_REQUEST", "message": message, "details": details or {}},
    )


def not_found(entity: str, entity_id: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "NOT_FOUND",
            "message": f"{entity} '{entity_id}' was not found.",
            "details": {"entity": entity, "id": entity_id},
        },
    )

