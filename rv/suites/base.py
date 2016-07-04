import logging
import statistics
from itertools import chain

import requests


class Suite(object):
    """
    Generates and groups logically similar Tests.
    """

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
        """
        Return a dictionary of timing statistics.
        :rtype: dict[str, float]
        """
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

    def calculate_apdex(self, satisfied_threshold_sec):
        """
        Calculate the Apdex score given a "satisfied" threshold.

        See https://en.wikipedia.org/wiki/Apdex#Apdex_method

        :param satisfied_threshold_sec:
            How many seconds a request should take to be considered satisfactorily fast
        :return: Decimal value between 0 and 1
        """
        durations = [t.duration for t in self.tests if t.duration is not None]
        if not durations:
            return None
        tolerating_threshold_sec = satisfied_threshold_sec * 4
        n_satisfied = 0
        n_tolerating = 0
        for duration in durations:
            if duration <= satisfied_threshold_sec:
                n_satisfied += 1
            elif duration <= tolerating_threshold_sec:
                n_tolerating += 1
        return (n_satisfied + (n_tolerating / 2)) / len(durations)

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
    """
    A Suite with an additional `requests` Session (for connection pooling).

    In addition, lets one set additional base query parameters to
    send with each request (provided `.session` isn't accessed directly).
    """
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
