"""
Custom exceptions for the health check system.
"""


class HealthCheckError(Exception):
    """Base exception for all health check related errors."""
    pass


class ConfigurationError(HealthCheckError):
    """Raised when there's an issue with configuration."""
    pass


class ConnectionError(HealthCheckError):
    """Raised when there's an issue with SSH connections."""
    pass


class CommandExecutionError(HealthCheckError):
    """Raised when command execution fails."""
    pass


class ReportGenerationError(HealthCheckError):
    """Raised when report generation fails."""
    pass


class ValidationError(HealthCheckError):
    """Raised when validation of inputs or prerequisites fails."""
    pass


class TimeoutError(HealthCheckError):
    """Raised when operations timeout."""
    pass


class AuthenticationError(ConnectionError):
    """Raised when SSH authentication fails."""
    pass