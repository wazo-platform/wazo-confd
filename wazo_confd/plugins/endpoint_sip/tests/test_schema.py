# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from unittest import TestCase

from hamcrest import assert_that, has_entries

# Adding schemas to the marshmallow registry
from wazo_confd.plugins.trunk.resource import TrunkSchema  # noqa
from wazo_confd.plugins.line.resource import LineSchema  # noqa

from ..schema import SipSchema


class TestSipSchema(TestCase):
    def setUp(self):
        self.schema = SipSchema()

    def test_that_the_name_matches_the_username_if_missing(self):
        body = {'username': 'foo'}

        result = self.schema.load(body)

        assert_that(result, has_entries(username='foo', name='foo'))

    def test_that_the_name_and_username_can_be_specified(self):
        body = {'username': 'foo', 'name': 'bar'}

        result = self.schema.load(body)

        assert_that(result, has_entries(username='foo', name='bar'))

    def test_that_the_username_matches_the_name_when_dumping_if_none(self):
        object_ = {'name': 'foobar', 'username': None}

        body = self.schema.dump(object_)

        assert_that(body, has_entries(username='foobar', name='foobar'))
