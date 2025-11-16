"""Custom exceptions for Valheim Save Tools."""


class ValheimSaveToolsError(Exception):
    """Base exception."""
    pass


class JarNotFoundError(ValheimSaveToolsError):
    """JAR file not found."""
    pass


class JavaNotFoundError(ValheimSaveToolsError):
    """Java not found."""
    pass


class CommandExecutionError(ValheimSaveToolsError):
    """Command execution failed."""
    pass
