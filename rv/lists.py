import random
from collections import Counter
from itertools import product
from urllib.parse import urlparse

import jsonschema
import requests

from rv.suites import RequestSuite
from rv.tests import MultipleParamsTest, SingleParamTest
from rv.utils import cached_property


class Limits(object):

    def __init__(
        self,
        *,
        max_single_tests_per_param=None,
        max_multi_tests_involving_param=None,
        max_multi_tests=None,
        multi_param_probability=1.0
    ):
        self.max_single_tests_per_param = int(max_single_tests_per_param or 0)
        self.max_multi_tests_involving_param = int(max_multi_tests_involving_param or 0)
        self.max_multi_tests = int(max_multi_tests or 0)
        self.multi_param_probability = float(multi_param_probability)


class ListTester(RequestSuite):

    def __init__(self, *, endpoint, schema, parameters, name=None, limits=None):
        if not name:
            name = urlparse(endpoint).path.replace('.', '_').strip('/')
        super(ListTester, self).__init__(name=name)
        self.session = requests.Session()
        self.endpoint = endpoint
        self.schema = schema
        self.parameters = parameters
        self.limits = (limits or Limits())

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
        if self.validator:
            for item in items:
                self.validator.validate(item)
        return items

    @cached_property
    def validator(self):
        if self.schema:
            return jsonschema.Draft4Validator(self.schema)
        return None

    @cached_property
    def baseline_items(self):
        items = self.get_list(self.request("GET", self.endpoint))
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
                yield SingleParamTest(tester=self, param=param, value=value)

    def _produce_combinations(self):
        prob = self.limits.multi_param_probability
        prop_values = self.baseline_values
        param_to_values = [
            (param, prop_values[param.parameter])
            for param
            in self.parameters
        ]
        params, values = zip(*param_to_values)
        for v_values in product(*values):
            if prob < 1 and random.random() >= prob:
                continue
            yield {
                param: value
                for (param, value)
                in zip(params, v_values)
                if value is not None
            }

    def _build_multi_param_tests(self):
        involvement_counter = Counter()
        n_tests = 0
        for param_to_values in self._produce_combinations():
            params = param_to_values.keys()
            if self.limits.max_multi_tests_involving_param:
                if any(
                        involvement_counter[param] > self.limits.max_multi_tests_involving_param
                        for param in params
                ):
                    continue
            yield MultipleParamsTest(tester=self, params_to_values=param_to_values)
            for param in params:
                involvement_counter[param] += 1
            n_tests += 1
            if self.limits.max_multi_tests and n_tests >= self.limits.max_multi_tests:
                break

    @cached_property
    def tests(self):
        return list(self._build_tests())

    def run(self):
        if not self.baseline_items:
            raise ValueError('no baseline, unable to test test anything.')
        self.log.info('%d baseline items', len(self.baseline_items))
        return super(ListTester, self).run()
