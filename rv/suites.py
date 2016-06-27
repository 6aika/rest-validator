import logging
from itertools import chain

import requests


class Suite(object):

    def __init__(self, *, name):
        self.name = name
        self.log = logging.getLogger("%s.%s" % (self.__class__.__name__.rsplit(".")[-1], self.name))

    @property
    def tests(self):
        raise NotImplementedError("implement me in a Suite subclass")

    @property
    def errors(self):
        return chain(*(t.errors for t in self.tests))

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
