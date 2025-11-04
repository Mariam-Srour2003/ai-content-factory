"""
Custom exceptions for the AI Content Factory.
"""

class AIContentFactoryError(Exception):
    """Base exception class for AI Content Factory."""
    pass

class ConfigurationError(AIContentFactoryError):
    """Raised when there is an error in configuration."""
    pass

class ContentGenerationError(AIContentFactoryError):
    """Raised when content generation fails."""
    pass

class ValidationError(AIContentFactoryError):
    """Raised when validation of input or output fails."""
    pass

class ResourceNotFoundError(AIContentFactoryError):
    """Raised when a required resource is not found."""
    pass

class APIError(AIContentFactoryError):
    """Raised when there is an error in API communication."""
    pass