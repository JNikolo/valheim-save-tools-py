"""Custom exceptions for Valheim Save Tools."""


class ValheimSaveToolsError(Exception):
    """Base exception for all Valheim Save Tools errors."""
    pass


class JarNotFoundError(ValheimSaveToolsError):
    """Raised when the JAR file cannot be found."""
    pass


class JavaNotFoundError(ValheimSaveToolsError):
    """Raised when Java executable cannot be found."""
    pass


class CommandExecutionError(ValheimSaveToolsError):
    """Raised when a command execution fails."""
    pass


class FileTypeError(ValheimSaveToolsError):
    """Raised when an invalid file type is provided for an operation."""
    pass


class ItemParseError(ValheimSaveToolsError):
    """Raised when parsing Valheim item data fails."""
    pass


class TemporaryFileError(ValheimSaveToolsError):
    """Raised when temporary file operations fail."""
    pass
