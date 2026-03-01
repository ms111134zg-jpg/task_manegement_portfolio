

class AppError(Exception):
    def __init__(self, message: str, *, code: str = "app_error", extra: dict | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.extra = extra or {}

class NotFoundError(AppError):
    def __init__(self, message="not found", *, extra=None):
        super().__init__(message, code="not_found", extra=extra)

class ConflictError(AppError):
    def __init__(self, message="conflict", *, extra=None):
        super().__init__(message, code="conflict", extra=extra)

class ValidationError(AppError):
    def __init__(self, message="validation error", *, extra=None):
        super().__init__(message, code="validation_error", extra=extra)