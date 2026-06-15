from typing import Any

from fastapi import HTTPException, status


def create_credential_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_service_unavailable_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=detail,
    )


class DuplicatedError(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class AuthError(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


class NotFoundError(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class ValidationError(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(422, detail, headers)


class PermissionDeniedError(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


class UnauthorizedError(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, headers)


class NotSatisfiableError(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(416, detail, headers)
