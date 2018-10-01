"""
This Module handles all the CyberCaptain exceptions.
"""
import logging

logger = logging.getLogger("CyberCaptain")

class Error(Exception):
    """
    Base class for exceptions in this module.

    **Parameters**:
        message : str
            The message why it did not validate.
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class ValidationError(Error):
    """
    Raised when the script config validation has failed.

    **Parameters**:
        module : obj
            The Module object that threw the exception.
        field : list
            The field that has not validated.
        message : str
            The message why it did not validate.
    """

    def __init__(self, module, fields, message):
        super().__init__(message)
        self.module = module
        self.fields = fields

        logger.error("ValidationError in %s for the attribute(s) %s '%s'" % (str(module), str(fields), message))

class ConfigurationError(Error):
    """
    Raised when an error in the script config or modules config happened.

    **Parameters**:
        message : str
            The message what the error was.
    """

    def __init__(self, message):
        super().__init__(message)
        logger.error("ConfigurationError: %s " % (message))

class LinePassedError(Error):
    """
    Raised when a given line number was already read. This ensures that no line is read twice.

    **Parameters**:
        message : str
            The message what the error was.
    """

    def __init__(self, message):
        super().__init__(message)
        logger.error("LinePassedError: %s " % (message))

class LineNotFoundError(Error):
    """
    Raised when a given line number was not found in the file.

    **Parameters**:
        message : str
            The message what the error was.
    """

    def __init__(self, message):
        super().__init__(message)
        logger.error("LineNotFoundError: %s " % (message))
