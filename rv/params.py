import datetime
import random
from operator import eq

import dateutil.parser


class Param(object):
    discrete = True

    def __init__(self, *, property, parameter=None, operator=eq, bucket=None):
        self.property = property
        self.parameter = (parameter or property)
        self.operator = operator
        self.bucket_value = bucket

    def __repr__(self):
        return '<%s(%r) at 0x%x>' % (self.__class__.__name__, self.parameter, id(self))

    def get_values(self, objects):
        """
        Retrieve this Param's values from the given objects.

        :param objects: List of source objects.
        :return: Set of values.
        """
        return set(
            self.get_value(obj)
            for obj in objects
            if self.property in obj
        )

    def get_value(self, obj):
        """
        Retrieve this Param's value from a single object.

        :param obj: Source object.
        :return: This param's value
        """
        return self.to_python(obj[self.property])

    def embucket(self, values):
        """
        Embucket the given values based on the Param's bucketing function.

        For all buckets the bucketing function returns, only one input value is retained.

        :param values: Input values
        :return: Output values
        """
        if not self.bucket_value:
            return values
        bucketed = {}
        for value in values:
            bucketed[self.bucket_value(value)] = value
        return set(bucketed.values())

    def to_wire(self, value):
        return str(value)

    def to_python(self, value):
        return value

    def generate_values(self, value_range, count=None):
        """
        Generate at most `count` values from the range `range`.

        For discrete values, this generates either the full value range,
        or a random sample thereof.

        For continuous values, a random sampling is likely to be used, and
        as such, duplicate values could well be returned.

        :rtype: Iterable[object]
        """

        if count:
            yield from sorted(random.sample(value_range, min(len(value_range), count)))
        else:
            yield from value_range


class DateTimeParam(Param):
    discrete = False

    def to_wire(self, value):
        return value.isoformat()

    def to_python(self, value):
        return dateutil.parser.parse(value)

    def generate_values(self, value_range, count=None):
        min_val = min(value_range)
        max_val = max(value_range)
        total_delta = (max_val - min_val).total_seconds()
        n = 0
        while not count or n < count:
            yield min_val + datetime.timedelta(seconds=random.uniform(0, total_delta))
            n += 1


class NumberParam(Param):
    discrete = False

    def to_python(self, value):
        return float(value)

    def generate_values(self, value_range, count=None):
        min_val = min(value_range)
        max_val = max(value_range)
        n = 0
        while not count or n < count:
            yield random.uniform(min_val, max_val)
            n += 1
