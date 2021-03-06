from operator import ge, le

from click import Option

from rv.params import DateTimeParam, Param
from rv.shell import BaseValidator
from rv.suites.lists import Limits, ListTester

from .schema import ISSUE_SCHEMA


def day_bucket(dt):
    return dt.strftime('%Y%m%d')


class IssueReportingValidator(BaseValidator):
    DEFAULT_ENDPOINT = 'http://127.0.0.1:8000/api/georeport/v2/requests.json'

    def get_click_options(self):
        return [
            Option(
                param_decls=('-e', '--endpoint'),
                default=self.DEFAULT_ENDPOINT,
                help='the endpoint to test'
            ),
            Option(
                param_decls=('--page-size', 'page_size'),
                default=500,
                type=int,
                help='page size to pass in calls',
            ),
            Option(
                param_decls=('--max-single-tests-per-param', 'max_single_tests_per_param'),
                default=10,
                type=int,
            ),
            Option(
                param_decls=('--max-multi-tests', 'max_multi_tests'),
                default=100,
                type=int,
            ),

        ]

    def get_suites(
        self,
        endpoint=DEFAULT_ENDPOINT,
        page_size=500,
        max_single_tests_per_param=10,
        max_multi_tests=100,
        **kwargs
    ):
        tester = ListTester(
            endpoint=endpoint,
            schema=ISSUE_SCHEMA,
            parameters=[
                # Discrete-valued parameters; ListTester will read their values from the baseline and
                # act accordingly.
                # TODO: Maybe sometime in the future these could be preset instead of read from the baseline?
                #       In that case, though, we can't raise an error if we don't get any items at all...
                Param(property='status'),
                Param(property='service_code'),

                # Continuous-values parameters with differing property/parameters, and comparison functions.
                DateTimeParam(property='requested_datetime', parameter='start_date', operator=ge, bucket=day_bucket, discrete=False),
                DateTimeParam(property='requested_datetime', parameter='end_date', operator=le, bucket=day_bucket, discrete=False),
                DateTimeParam(property='updated_datetime', parameter='updated_after', operator=ge, bucket=day_bucket, discrete=False),
                DateTimeParam(property='updated_datetime', parameter='updated_before', operator=le, bucket=day_bucket, discrete=False),
            ],
            limits=Limits(
                max_single_tests_per_param=max_single_tests_per_param,
                max_multi_tests=max_multi_tests,
            ),
        )
        tester.base_params = {
            'page_size': page_size,
        }
        yield tester
