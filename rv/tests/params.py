from rv.excs import ExpectedMoreItems, ParamValueError
from rv.tests.base import Test
from rv.tests.validation import ValidationTest


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


class SingleParamTest(BaseParamTest):
    """
    Test that given a list/search endpoint, all of the items returned
    match the single parameter attempted.
    """

    def __init__(self, suite, param, value):
        super(SingleParamTest, self).__init__(suite)
        self.param = param
        self.value = value

    def execute(self):
        param = self.param
        query = {param.parameter: param.to_wire(self.value)}
        self.response = self.suite.request('GET', self.suite.endpoint, params=query)
        self.response.raise_for_status()
        self.items = items = self.suite.get_list(self.response)
        if not items:
            yield ExpectedMoreItems(test=self)
        self.suite.log.debug('testing %s against %d items' % (self.name, len(items)))
        for item in items:
            item_value = param.get_value(item)
            if not param.operator(item_value, self.value):
                yield ParamValueError(test=self, item=item, item_value=item_value)

        yield from ValidationTest(
            suite=self.suite,
            validate=self.suite.validate,
            items=items
        ).execute()

    @property
    def name(self):
        return "Single: %s=%s" % (
            self.param.parameter,
            self.value,
        )

    @property
    def description(self):
        return (
            "If the parameter {parameter} has the value {value}, "
            "{property} {op} {value} should hold true for all items"
        ).format(
            op=self.param.operator.__name__,
            parameter=self.param.parameter,
            property=self.param.property,
            value=self.value,
        )


class MultipleParamsTest(BaseParamTest):
    """
    Test that given a list/search endpoint, all of the items returned
    match the multiple parameters attempted.
    """

    def __init__(self, suite, params_to_values, min_expected=0):
        super(MultipleParamsTest, self).__init__(suite)
        self.params_to_values = params_to_values
        self.min_expected = min_expected

    def execute(self):
        query = {
            param.parameter: param.to_wire(value)
            for (param, value)
            in self.params_to_values.items()
        }
        self.response = self.suite.request('GET', self.suite.endpoint, params=query)
        self.response.raise_for_status()
        self.items = items = self.suite.get_list(self.response)
        if len(items) < self.min_expected:
            yield ExpectedMoreItems(
                test=self,
                message='expected at least %d items, got %d' % (self.min_expected, len(items))
            )
        self.suite.log.debug('testing %s against %d items' % (self.name, len(items)))
        for item in items:
            for param, exp_value in self.params_to_values.items():
                item_value = param.get_value(item)
                if not param.operator(item_value, exp_value):
                    yield ParamValueError(test=self, item=item, item_value=item_value)

        yield from ValidationTest(
            suite=self.suite,
            validate=self.suite.validate,
            items=items
        ).execute()

    @property
    def name(self):
        return "Multi: %s" % (",".join(sorted(
            "%s=%s" % (param.parameter, value)
            for (param, value)
            in self.params_to_values.items()
        )))
