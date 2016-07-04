import os
from operator import attrgetter

import jinja2

TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__),
    'templates'
)

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader([TEMPLATE_PATH]),
    autoescape=True,
    undefined=jinja2.DebugUndefined,
)


class HTMLReportWriter(object):

    def __init__(self, suites):
        self.suites = list(sorted(suites, key=attrgetter('name')))

    def render(self):
        template = jinja_env.get_template('report.html')
        return template.render({
            'title': 'RV Report',
            'suites': self.suites,
        })
