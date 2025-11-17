# Custom exceptions
class SinacorParserException(Exception):
    """Base exception for Sinacor Parser"""

    pass


class FileValidationError(SinacorParserException):
    """Raised when file validation fails"""

    pass


class BrokerDetectionError(SinacorParserException):
    """Raised when broker cannot be detected"""

    pass


class ParsingError(SinacorParserException):
    """Raised when PDF parsing fails"""

    pass


class ConfigurationError(SinacorParserException):
    """Raised when configuration is invalid"""

    pass
