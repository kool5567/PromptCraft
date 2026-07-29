from typing import Any, Optional


class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        details: Optional[Any] = None,
    ):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        self.details = details


class NotFoundException(AppException):
    def __init__(self, entity: str, entity_id: Any = None):
        detail = f"{entity} not found"
        if entity_id:
            detail = f"{entity} with id '{entity_id}' not found"
        super().__init__(
            status_code=404,
            detail=detail,
            error_code="NOT_FOUND",
        )


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code="UNAUTHORIZED",
        )


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=403,
            detail=detail,
            error_code="FORBIDDEN",
        )


class BadRequestException(AppException):
    def __init__(self, detail: str, error_code: str = "BAD_REQUEST"):
        super().__init__(
            status_code=400,
            detail=detail,
            error_code=error_code,
        )


class ConflictException(AppException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=409,
            detail=detail,
            error_code="CONFLICT",
        )


class RateLimitException(AppException):
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=429,
            detail=detail,
            error_code="RATE_LIMIT",
        )


class SubscriptionRequiredException(AppException):
    def __init__(self, detail: str = "Premium subscription required"):
        super().__init__(
            status_code=402,
            detail=detail,
            error_code="SUBSCRIPTION_REQUIRED",
        )
