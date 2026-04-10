from fastapi import HTTPException


class AppError(HTTPException):
    pass


def bad_request(detail: str) -> AppError:
    return AppError(status_code=400, detail=detail)


def unauthorized(detail: str = "Unauthorized") -> AppError:
    return AppError(status_code=401, detail=detail)


def forbidden(detail: str = "Forbidden") -> AppError:
    return AppError(status_code=403, detail=detail)


def not_found(detail: str = "Not found") -> AppError:
    return AppError(status_code=404, detail=detail)