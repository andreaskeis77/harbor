"""Harbor domain exceptions.

These replace the previous pattern of raising KeyError/ValueError with string
keys and matching them via str(exc) in route handlers. Each exception type
maps to a single HTTP status code, and carries structured attributes for
the route layer to translate without string matching.

Hierarchy:
    HarborError
    ├── NotFoundError        → 404
    ├── DuplicateError       → 409
    ├── NotPromotableError   → 409
    └── InvalidPayloadError  → 422
"""

from __future__ import annotations


class HarborError(Exception):
    """Base class for all Harbor domain exceptions."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(HarborError):
    """A requested resource does not exist."""

    def __init__(self, resource_type: str, resource_id: str | None = None) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id
        detail = f"{resource_type} not found."
        if resource_id:
            detail = f"{resource_type} '{resource_id}' not found."
        super().__init__(detail)


class DuplicateError(HarborError):
    """A resource already exists or is already associated."""

    def __init__(self, resource_type: str, detail: str | None = None) -> None:
        self.resource_type = resource_type
        message = detail or f"{resource_type} already exists."
        super().__init__(message)


class NotPromotableError(HarborError):
    """A resource cannot be promoted in its current state."""

    def __init__(self, resource_type: str, reason: str) -> None:
        self.resource_type = resource_type
        self.reason = reason
        super().__init__(f"{resource_type} is not promotable: {reason}")


class InvalidPayloadError(HarborError):
    """A request payload failed domain validation."""

    def __init__(self, resource_type: str, reason: str) -> None:
        self.resource_type = resource_type
        self.reason = reason
        super().__init__(f"Invalid {resource_type} payload: {reason}")
