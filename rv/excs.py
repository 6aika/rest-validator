"""
A module of exceptions and problems.
"""
import traceback

from jinja2.filters import do_truncate
from jsonschema import ValidationError as JSONSchemaValidationError


class TestException(Exception):
    """
    An exception occurring during a test.

    Captures the Test object as `.test`.
    """
    default_message = "Oops."

    def __init__(self, test, message=None):
        self.test = test
        if message is None:
            message = self.default_message
        super(TestException, self).__init__(message)


class ParamValueError(TestException):
    """
    A parameter/property value test failed.
    """

    message_template = (
        '{param}\'s value {item_value} in item {item} '
        'was not the expected {expected_value}'
    )

    def __init__(self, test, item, item_value):
        self.test = test
        self.item = item
        self.item_value = item_value
        message = self.message_template.format(
            expected_value=self.test.value,
            item=self.item,
            item_value=self.item_value,
            param=self.test.param,
        )
        super(ParamValueError, self).__init__(test=test, message=message)


class ExpectedMoreItems(TestException):
    """
    Some items were expected but none were received.
    """
    default_message = 'expected to receive items but got none'


class WrappedTestException(TestException):
    """
    Another exception.
    """

    def __init__(self, test, exception):
        self.exception = exception
        super(WrappedTestException, self).__init__(test=test, message=self._format_exception())

    def _format_exception(self):
        return traceback.format_exception_only(
            self.exception.__class__,
            self.exception
        )


class ValidationException(TestException):
    def __init__(self, test, item, error, message=None):
        self.item = item
        self.error = error
        if not message:
            if isinstance(error, JSONSchemaValidationError):
                error = error.message  # Avoid the huge "verbose" dump
            message = '{error} (in {item})'.format(
                error=error,
                item=do_truncate(str(item), 40),
            )
        super(ValidationException, self).__init__(test=test, message=message)
