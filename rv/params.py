from operator import eq

import dateutil.parser


class Param(object):

    def __init__(self, *, property, parameter=None, operator=eq, bucket=None):
        self.property = property
        self.parameter = (parameter or property)
        self.operator = operator
        self.bucket_fn = bucket

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
        if not self.bucket_fn:
            return values
        bucketed = {}
        for value in values:
            bucketed[self.bucket_fn(value)] = value
        return set(bucketed.values())

    def to_wire(self, value):
        return str(value)

    def to_python(self, value):
        return value


class DateTimeParam(Param):

    def to_wire(self, value):
        return value.isoformat()

    def to_python(self, value):
        return dateutil.parser.parse(value)


class NumberParam(Param):

    def to_python(self, value):
        return float(value)

# TODO: Allow generating tests for non-discrete params on a range (e.g.
#       a NumericParam/DateTimeParam could derive min/max from values)
