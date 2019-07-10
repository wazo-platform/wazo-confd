import unittest

from hamcrest import (
    assert_that,
    has_entries,
    has_key,
)

from ..schema import RangeSchema


class TestRangeSchema(unittest.TestCase):

    def setUp(self):
        self.schema = RangeSchema(handle_error=False)

    def test_load(self):
        context_range = dict(start='10', end='20')

        result = self.schema.load(context_range).data
        assert_that(result, has_entries(
            start='10',
            end='20',
        ))

    def test_load_prefix(self):
        context_range = dict(start='010', end='020')

        result = self.schema.load(context_range).data
        assert_that(result, has_entries(
            start='010',
            end='020',
        ))

    def test_load_start_equals_to_end(self):
        context_range = dict(start='10', end='10')

        result = self.schema.load(context_range).data
        assert_that(result, has_entries(
            start='10',
            end='10',
        ))

    def test_load_different_length(self):
        context_range = dict(start='001', end='02')

        result = self.schema.load(context_range).errors
        assert_that(result, has_key('_schema'))

    def test_load_end_before_start(self):
        context_range = dict(start='02', end='01')

        result = self.schema.load(context_range).errors
        assert_that(result, has_key('_schema'))

    def test_load_end_before_start_different_length(self):
        context_range = dict(start='02', end='001')

        result = self.schema.load(context_range).errors
        assert_that(result, has_key('_schema'))
