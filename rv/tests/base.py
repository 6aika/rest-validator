from uuid import uuid4

from rv.excs import WrappedTestException
from rv.utils import wallclock


class Test(object):
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
        raise NotImplementedError("...")

    def get_report_detail(self):
        """
        Get a dict (or a sorted dict?) of any additional "detail" that is worthwhile to show in a report.
        """
        return {}

    @property
    def type(self):
        typename = self.__class__.__name__
        if typename.endswith('Test'):
            typename = typename[:-4]
        return typename


class BaseParamTest(Test):

    def __init__(self, suite):
        super().__init__(suite)
        self.response = None
        self.items = None

    @property
    def url(self):
        if self.response:
            return self.response.request.url
        return None

    def get_report_detail(self):
        return {
            'num_items': len(self.items or ()),
        }
