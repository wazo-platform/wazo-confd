from hamcrest import (
    assert_that,
    calling,
    not_,
    raises,
)
import unittest

from marshmallow.exceptions import ValidationError

from ..schema import RangeSchema


class TestRangeValidator(unittest.TestCase):

    def setUp(self):
        self.range_schema = RangeSchema()

    def test_start_cant_be_higher_than_end(self):
        start = 20
        end = 10

        assert_that(
            calling(self.range_schema.validate_range).with_args(start, end),
            raises(ValidationError, pattern='Start of range')
        )

    def test_start_can_be_equal_to_end(self):
        start = 10
        end = 10

        assert_that(
            calling(self.range_schema.validate_range).with_args(start, end),
            not_(raises(ValidationError, pattern='Start of range'))
        )

    def test_start_can_be_lower_than_end(self):
        start = 10
        end = 20

        assert_that(
            calling(self.range_schema.validate_range).with_args(start, end),
            not_(raises(ValidationError, pattern='Start of range'))
        )
