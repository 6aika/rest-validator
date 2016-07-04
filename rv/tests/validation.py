from rv.excs import ValidationException
from rv.tests.base import Test


class ValidationTest(Test):

    def __init__(self, suite, validate, items, name=None):
        super().__init__(suite)
        self.validate = validate
        self.items = items
        if name:
            self.name = name

    def execute(self):
        for item in self.items:
            for err in self.validate(item):
                yield ValidationException(test=self, item=item, error=err)
