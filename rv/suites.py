import logging
import statistics
from itertools import chain

import requests


class Suite(object):
    description = ""

    def __init__(self, *, name):
        self.name = name
        self.log = logging.getLogger("%s.%s" % (self.__class__.__name__.rsplit(".")[-1], self.name))

    @property
    def tests(self):
        raise NotImplementedError("implement me in a Suite subclass")

    @property
    def errors(self):
        return chain(*((t.errors or ()) for t in self.tests))

    @property
    def num_errors(self):
        return len(list(self.errors))

    def get_report_detail(self):
        """
        Get a dict (or a sorted dict?) of any additional "detail" that is worthwhile to show in a report.
        """
        return {}

    def get_timing_stats(self):
        durations = sorted(t.duration * 1000 for t in self.tests if t.duration is not None)
        if not durations:
            return None

        return {
            'min': min(durations),
            'max': max(durations),
            'total': sum(durations),
            'mean': statistics.mean(durations),
            'median': statistics.median(durations),
            'stdev': statistics.stdev(durations),
        }

    def run(self):
        """
        Run all the tests and print results to stdout.
        """
        self.log.info('%d tests to run...', len(self.tests))
        for i, test in enumerate(self.tests, 1):
            print('{index}/{total}: {name}'.format(index=i, total=len(self.tests), name=test.name))
            test.run()
            for error in test.errors:
                print("[!]", error)


class RequestSuite(Suite):
    base_params = {}

    def __init__(self, *, name):
        super().__init__(name=name)
        self.session = requests.Session()

    def request(self, method, url, **kwargs):
        method = method.upper()
        if method == "GET":
            params = self.base_params.copy()
            kwargs['params'] = dict(params, **kwargs.get('params', {}))
        return self.session.request(method=method, url=url, **kwargs)
