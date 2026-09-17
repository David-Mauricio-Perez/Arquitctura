"""Core domain exceptions."""


class DomainException(Exception):
    """Base exception for domain errors."""



class UserNotFoundError(DomainException):
    """Raised when a user is not found."""



class UserAlreadyExistsError(DomainException):
    """Raised when attempting to create a user that already exists."""



class AuthenticationFailedError(DomainException):
    """Raised when authentication fails."""



class InvalidUserError(DomainException):
    """Raised when user data is invalid."""



class RolNotFoundError(DomainException):
    """Raised when a rol is not found."""



class RolAlreadyExistsError(DomainException):
    """Raised when attempting to create a rol that already exists."""



class InvalidRolError(DomainException):
    """Raised when rol data is invalid."""

