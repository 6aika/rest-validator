import importlib
import inspect
import logging

import click

log = logging.getLogger(__name__)


class BaseValidator(object):
    def get_cli_params(self):
        return []

    def get_cli_command(self):
        return click.Command(
            name=self.__class__.__name__,
            params=self.get_cli_params(),
        )

    def get_suites(self, **kwargs):
        raise NotImplementedError('...')


def find_class(classpath, subclass):
    bits = classpath.split('.')
    if bits[-1][0].isupper():  # Last bit is capitalized; assume it's a classpath
        val = getattr(importlib.import_module('.'.join(bits[:-1])), bits[-1])
        assert issubclass(val, subclass)
        return val
    else:  # Last bit not capitalized; assume it's a module and find the first valid subclass
        mod = importlib.import_module(classpath)
        for var, val in vars(mod).items():
            if inspect.isclass(val) and val is not subclass and issubclass(val, subclass):
                return val


class RvCLI(click.MultiCommand):
    def __init__(self):
        super().__init__(
            callback=self.init_callback,
            params=[
                click.Option(('-d', '--debug', 'loglevel'), flag_value=logging.DEBUG),
                click.Option(('-v', '--verbose', 'loglevel'), flag_value=logging.INFO),
            ])

    def get_command(self, ctx, name):
        self.validator = find_class(name, BaseValidator)()
        command = self.validator.get_cli_command()
        command.callback = self.run
        return command

    def run(self, **kwargs):
        suites = list(self.validator.get_suites(**kwargs))
        for suite in suites:
            print('## %s' % suite.name)
            suite.run()
            print('-' * 80)
            for err in suite.errors:
                print('*', err)
            print('=' * 80)

    def init_callback(self, **options):
        self.options = options
        loglevel = options.get('loglevel')
        if loglevel:
            logging.basicConfig(level=loglevel)
            logging.getLogger('requests.packages.urllib3').setLevel(level=logging.WARN)
