from rv.excs import ExpectedItemsGotNone, ParamValueError
from rv.utils import wallclock


class Test(object):
    name = "Some Test"

    def __init__(self, tester):
        self.tester = tester
        self.has_been_run = False
        self.errors = None
        self.duration = None

    def run(self):
        if not self.has_been_run:
            start_time = wallclock()
            self.errors = list(self.execute())
            self.duration = wallclock() - start_time
            self.has_been_run = True
        return not bool(self.errors)

    def execute(self):
        raise NotImplementedError("...")


class SingleParamTest(Test):

    def __init__(self, tester, param, value):
        super(SingleParamTest, self).__init__(tester)
        self.param = param
        self.value = value

    def execute(self):
        param = self.param
        query = {param.parameter: param.to_wire(self.value)}
        items = self.tester.get_list(
            self.tester.request('GET', self.tester.endpoint, params=query)
        )
        if not items:
            yield ExpectedItemsGotNone(test=self)
        self.tester.log.debug('testing %s against %d items' % (self.name, len(items)))
        for item in items:
            item_value = param.get_value(item)
            if not param.operator(item_value, self.value):
                yield ParamValueError(test=self, item=item, item_value=item_value)

    @property
    def name(self):
        return "%s=%s (%s %s %s)" % (
            self.param.parameter,
            self.value,
            self.param.property,
            self.param.operator.__name__,
            self.value
        )


class MultipleParamsTest(Test):

    def __init__(self, tester, params_to_values):
        super(MultipleParamsTest, self).__init__(tester)
        self.params_to_values = params_to_values

    def execute(self):
        query = {
            param.parameter: param.to_wire(value)
            for (param, value)
            in self.params_to_values.items()
        }
        items = self.tester.get_list(
            self.tester.request('GET', self.tester.endpoint, params=query)
        )
        self.tester.log.debug('testing %s against %d items' % (self.name, len(items)))
        for item in items:
            for param, exp_value in self.params_to_values.items():
                item_value = param.get_value(item)
                if not param.operator(item_value, exp_value):
                    yield ParamValueError(test=self, item=item, item_value=item_value)

    @property
    def name(self):
        return ",".join(sorted(
            "%s=%s" % (param.parameter, value)
            for (param, value)
            in self.params_to_values.items()
        ))
