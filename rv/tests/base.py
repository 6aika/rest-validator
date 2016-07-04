from uuid import uuid4

from rv.excs import WrappedTestException, TestException
from rv.utils import wallclock


class Test(object):
    """
    Tests are the lowest, simplest unit of execution and encapsulate
    a single attempt at verifying something.

    Unlike regular unit tests though, these tests may yield several errors.
    """
    name = "Some Test"
    description = ""
    url = ""

    def __init__(self, suite):
        self.id = 't%s' % uuid4()
        self.suite = suite
        self.has_been_run = False
        self.errors = None
        self.duration = None

    def run(self):
        """
        Run the test if it hasn't been run yet.

        Keeps track of execution time and stores errors;
        if you're looking to override something in a sub-
        class, it should be `.execute()` instead.

        :return: True if no errors were found, False otherwise.
        """
        if not self.has_been_run:
            start_time = wallclock()
            errors = []
            try:
                errors.extend(self.execute())
            except Exception as exc:
                errors.append(WrappedTestException(test=self, exception=exc))
            self.errors = errors
            self.duration = wallclock() - start_time
            self.has_been_run = True
        return not bool(self.errors)

    def execute(self):
        """
        Actually execute the test.

        This function should yield (or return an iterable of) `TestException`
        (or subclasses thereof) instances.  It _may_ also raise exceptions.

        :return: Iterable of exceptions
        :rtype: Iterable[TestException]
        """
        yield TestException(self, '%s has not been implemented' % self.__class__.__name__)

    def get_report_detail(self):
        """
        Get a dict (or a sorted dict?) of any additional "detail" that is worthwhile to show in a report.
        """
        return {}

    @property
    def type(self):
        """
        Get the type of this test (from the classname).
        :return: str
        """
        typename = self.__class__.__name__
        if typename.endswith('Test'):
            typename = typename[:-4]
        return typename
