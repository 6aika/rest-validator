import random
from collections import Counter
from urllib.parse import urlparse

import jsonschema
import requests

from rv.suites import RequestSuite
from rv.tests import MultipleParamsTest, SingleParamTest, ValidationTest
from rv.utils import cached_property, wallclock


class Limits(object):
    def __init__(
        self,
        *,
        max_single_tests_per_param=None,
        max_multi_tests_involving_param=None,
        max_multi_tests=250
    ):
        self.max_single_tests_per_param = int(max_single_tests_per_param or 0)
        self.max_multi_tests_involving_param = int(max_multi_tests_involving_param or 0)
        self.max_multi_tests = int(max_multi_tests)


class ListTester(RequestSuite):
    description = "Test that filters work in a list endpoint"

    def __init__(self, *, endpoint, schema, parameters, name=None, limits=None):
        if not name:
            name = urlparse(endpoint).path.replace('.', '_').strip('/')
        super(ListTester, self).__init__(name=name)
        self.session = requests.Session()
        self.endpoint = endpoint
        self.schema = schema
        self.parameters = parameters
        self.limits = (limits or Limits())

    def get_report_detail(self):
        return dict(
            vars(self.limits),
            endpoint=self.endpoint,
        )

    def peel(self, data):
        """
        "Peel" incoming data to a list.

        This is handy when the endpoint returns something like `{"items": [...]}`.

        :param data: Data object, fresh from JSON
        :return: list[dict]
        """
        return data

    def get_list(self, response):
        items = self.peel(response.json())
        return items

    def validate(self, item):
        if self.validator:
            yield from self.validator.iter_errors(item)

    @cached_property
    def validator(self):
        if self.schema:
            return jsonschema.Draft4Validator(self.schema)
        return None

    @cached_property
    def baseline_items(self):
        start_time = wallclock()
        items = self.get_list(self.request("GET", self.endpoint))
        self.baseline_duration = wallclock() - start_time
        assert isinstance(items, list), 'baseline response not a list'
        return items

    @cached_property
    def baseline_values(self):
        values = {}
        for param in self.parameters:
            param_vals = param.get_values(self.baseline_items)
            if not param_vals:
                self.log.info('no values for %s', param)
                continue
            values[param.parameter] = sorted(param_vals, key=str)
        return values

    def _build_tests(self):
        yield ValidationTest(suite=self, validate=self.validate, items=self.baseline_items, name='Baseline Item Validation')
        yield from self._build_single_param_tests()
        yield from self._build_multi_param_tests()

    def _build_single_param_tests(self):
        prop_values = self.baseline_values
        param_to_values = {
            param: param.embucket(prop_values[param.parameter])
            for param
            in self.parameters
            }
        limit = self.limits.max_single_tests_per_param
        for param, values in param_to_values.items():
            if param.discrete:
                test_values = param.generate_values(values, count=limit)
            else:  # Try to avoid duplicate tests here
                test_values = set()
                generator = param.generate_values(values, count=limit)
                while len(test_values) < min(len(values), (limit or 9000)):
                    test_values.add(next(generator))
            for value in test_values:
                yield SingleParamTest(suite=self, param=param, value=value)

    def _build_multi_param_tests(self):
        prop_values = self.baseline_values
        params_to_value_ranges = [
            (param, prop_values[param.parameter])
            for param
            in self.parameters
            ]
        involvement_counter = Counter()  # not updated if not limited
        n_tests = 0
        while n_tests < self.limits.max_multi_tests:
            param_vr_tuples = random.sample(params_to_value_ranges, random.randint(2, len(params_to_value_ranges)))
            if len({param[0].property for param in param_vr_tuples}) != len(param_vr_tuples):
                # duplicate properties; no sense testing this
                continue
            # TODO: This could be made to use `.generate_values()` too
            params_to_values = {param: random.choice(values) for (param, values) in param_vr_tuples}
            params = params_to_values.keys()
            if self.limits.max_multi_tests_involving_param:
                if any(
                        involvement_counter[param] > self.limits.max_multi_tests_involving_param
                        for param in params
                ):
                    continue
                for param in params:
                    involvement_counter[param] += 1
            yield MultipleParamsTest(
                suite=self,
                params_to_values=params_to_values
            )
            n_tests += 1

    @cached_property
    def tests(self):
        return list(self._build_tests())

    def run(self):
        if not self.baseline_items:
            raise ValueError('no baseline, unable to test test anything.')
        self.log.info('%d baseline items', len(self.baseline_items))
        return super(ListTester, self).run()
