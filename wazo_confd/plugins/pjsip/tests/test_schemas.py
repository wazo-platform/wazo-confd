# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from unittest import TestCase

from hamcrest import assert_that, calling, has_entries, contains, raises
from werkzeug.exceptions import BadRequest

from ..schema import PJSIPTransportSchema


class TestTransportSchema(TestCase):
    def test_load_valid(self):
        body = {
            'name': 'my-transport',
            'options': [
                ['bind', '0.0.0.0:5060'],
                ['local_net', '192.168.1.0/24'],
                ['protocol', 'udp'],
            ],
        }

        result = PJSIPTransportSchema().load(body)
        assert_that(
            result,
            has_entries(
                name='my-transport',
                options=contains(
                    contains('bind', '0.0.0.0:5060'),
                    contains('local_net', '192.168.1.0/24'),
                    contains('protocol', 'udp'),
                ),
            ),
        )

    def test_name(self):
        body = {
            'name': 'name]\n[global]\nkey = value\n',
            'options': [['option', 'value']],
        }
        assert_that(
            calling(PJSIPTransportSchema().load).with_args(body), raises(BadRequest)
        )

    def test_load_without_2_values(self):
        body = {
            'name': 'my-transport',
            'options': [['option', 'value', 'what??']],
        }
        assert_that(
            calling(PJSIPTransportSchema().load).with_args(body), raises(BadRequest)
        )

        body = {
            'name': 'my-transport',
            'options': [['what??']],
        }
        assert_that(
            calling(PJSIPTransportSchema().load).with_args(body), raises(BadRequest)
        )

        body = {
            'name': 'my-transport',
            'options': [['option', '']],
        }
        assert_that(
            calling(PJSIPTransportSchema().load).with_args(body), raises(BadRequest)
        )

    def test_no_options(self):
        body = {'name': 'my-transport'}
        assert_that(
            calling(PJSIPTransportSchema().load).with_args(body), raises(BadRequest)
        )

    def test_injection_in_optoins(self):
        body = {
            'name': 'my-transport',
            'options': [['option', 'value\n[global]\nkey = value']],
        }
        assert_that(
            calling(PJSIPTransportSchema().load).with_args(body), raises(BadRequest)
        )

        body = {
            'name': 'my-transport',
            'options': [['value\n[global]\nkey = value', 'value']],
        }
        assert_that(
            calling(PJSIPTransportSchema().load).with_args(body), raises(BadRequest)
        )

    def test_empty_options_key_or_value(self):
        body = {'name': 'my-transport', 'options': ['', 'value']}
        assert_that(
            calling(PJSIPTransportSchema().load).with_args(body), raises(BadRequest)
        )

        body = {'name': 'my-transport', 'options': ['key', '']}
        assert_that(
            calling(PJSIPTransportSchema().load).with_args(body), raises(BadRequest)
        )

    def test_that_name_is_not_empty(self):
        body = {'name': ''}
        assert_that(
            calling(PJSIPTransportSchema().load).with_args(body), raises(BadRequest)
        )
