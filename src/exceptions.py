### Utils file exceptions

class FileNotFoundError(Exception):
    """Raised when a required file is not found."""
    pass


class InvalidConfigurationError(Exception):
    """Raised when the configuration file is invalid or incomplete."""
    pass


class InvalidDataError(Exception):
    """Raised when the provided data is invalid or incomplete."""
    pass


class TableNotFoundError(Exception):
    """Raised when a specific table is not found in the Word document."""
    pass



