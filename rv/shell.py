import logging

import click

from rv.report import HTMLReportWriter
from rv.utils import find_class

log = logging.getLogger(__name__)


class BaseValidator(object):

    def get_click_options(self):
        """
        Get a list of Click options for this Validator.

        This is called by `get_click_command`, so if you
        override that function in your subclass, pay no
        attention to this one.

        :return: list[click.Option]
        """
        return []

    def get_click_command(self):
        """
        Get a Click command for running this Validator.

        Note that the CLI multicommand shell rewrites
        the `callback` for this command to actually
        rig up the tests for running!

        :return: Click command
        :rtype: click.Command
        """
        return click.Command(
            name=self.__class__.__name__,
            params=self.get_click_options(),
        )

    def get_suites(self, **kwargs):
        """
        Get the actual parametrized test suites to run.

        :param kwargs: Option values from Click (or elsewhere!)
        :rtype: Iterable[Suite]
        """
        while False:  # Mark this function as an iterator
            yield None
        raise NotImplementedError('Implement get_suites in a subclass')


class RvCLI(click.MultiCommand):
    """
    Command-line runner main class.

    Does quite some magic around Click -- hopefully you, dear reader,
    do not need to touch that voodoo.
    """

    def __init__(self):
        super().__init__(
            callback=self.init_callback,
            params=[
                click.Option(('-d', '--debug', 'loglevel'), flag_value=logging.DEBUG),
                click.Option(('-v', '--verbose', 'loglevel'), flag_value=logging.INFO),
                click.Option(
                    ('--html',),
                    help='emit HTML report to this path',
                    type=click.File(mode='w', encoding='utf-8', lazy=True),
                ),
            ],
        )

    def get_command(self, ctx, name):
        self.validator = find_class(name, BaseValidator)()
        command = self.validator.get_click_command()
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

        html_fp = self.options['html']
        if html_fp:
            hrw = HTMLReportWriter(suites)
            html_fp.write(hrw.render())

    def init_callback(self, **options):
        self.options = options
        loglevel = options.get('loglevel')
        if loglevel:
            logging.basicConfig(level=loglevel)
            logging.getLogger('requests.packages.urllib3').setLevel(level=logging.WARN)
