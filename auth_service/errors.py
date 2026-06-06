class AuthError(Exception):
    """Base class for expected authentication errors."""


class InvalidCredentials(AuthError):
    pass


class PermissionDenied(AuthError):
    pass


class RateLimited(AuthError):
    pass


class MessagingError(AuthError):
    pass


class ConfigurationError(AuthError):
    pass
