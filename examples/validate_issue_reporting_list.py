import logging
from operator import ge, le

from rv.lists import Limits, ListTester
from rv.params import DateTimeParam, Param

STRING_OR_NULL = {"anyOf": [{"type": "string"}, {"type": "null"}]}
NUMERIC_STRING = {
    "type": "string",
    "pattern": "^-?[0-9]*(\.[0-9]+)?$"
}

NUMBER_OR_NUMERIC_STRING = {
    "anyOf": [
        {"type": "number"},
        NUMERIC_STRING
    ]
}

ISSUE_SCHEMA = {
    "type": "object",
    "properties": {
        "service_request_id": {"type": "string"},
        "status": {"type": "string", "parameter": True},
        "status_notes": {"type": "string"},
        "service_name": {"type": "string"},
        "service_code": {"type": "string", "parameter": True},
        "description": {"type": "string"},
        "agency_responsible": {"type": "string"},
        "service_notice": STRING_OR_NULL,
        "requested_datetime": {
            "type": "string",
        },
        "updated_datetime": STRING_OR_NULL,
        "expected_datetime": STRING_OR_NULL,
        "address": {"type": "string"},
        "address_id": {"type": "string"},
        "zipcode": {"type": "string"},
        "lat": NUMBER_OR_NUMERIC_STRING,
        "long": NUMBER_OR_NUMERIC_STRING,
        "media_url": STRING_OR_NULL,
        "extended_attributes": {"type": "object"},
        "distance": NUMBER_OR_NUMERIC_STRING,  # Not in the actual schema
    },
    "additionalProperties": False,
    "required": [
        "service_request_id",
        "status",
        "service_name",
        "service_code",
        "description",
        "requested_datetime",
        "updated_datetime",
        "expected_datetime",
    ]
}


def day_bucket(dt):
    return dt.strftime('%Y%m%d')


def run(endpoint, verbose=False):
    if verbose:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('rv').setLevel(level=logging.DEBUG)
        logging.getLogger('requests.packages.urllib3').setLevel(level=logging.WARN)

    tester = ListTester(
        endpoint=endpoint,
        schema=ISSUE_SCHEMA,
        parameters=[
            Param(property='status'),
            Param(property='service_code'),
            DateTimeParam(property='requested_datetime', parameter='start_date', operator=ge, bucket=day_bucket),
            DateTimeParam(property='requested_datetime', parameter='end_date', operator=le, bucket=day_bucket),
            DateTimeParam(property='updated_datetime', parameter='updated_after', operator=ge, bucket=day_bucket),
            DateTimeParam(property='updated_datetime', parameter='updated_before', operator=le, bucket=day_bucket),
        ],
        limits=Limits(
            max_single_tests_per_param=10,
            max_multi_tests=100,
            multi_param_probability=0.1,
        ),
    )
    tester.base_params = {
        'page_size': 500,
    }

    tester.run()

    print('-' * 80)

    for err in tester.errors:
        print('*', err)


def cmdline():
    import argparse
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument('-e', '--endpoint', default='http://127.0.0.1:8000/api/georeport/v2/requests.json', help='the endpoint to test')
    ap.add_argument('-v', '--verbose', default=False, action='store_true')
    args = ap.parse_args()
    run(**vars(args))


if __name__ == '__main__':
    cmdline()
