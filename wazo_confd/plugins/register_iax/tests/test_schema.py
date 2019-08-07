# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock
from hamcrest import (
    calling,
    assert_that,
    equal_to,
    has_entries,
    has_key,
    has_property,
)
from marshmallow import ValidationError
from xivo_test_helpers.hamcrest.raises import raises

from wazo_confd.plugins.trunk.resource import TrunkSchema  # noqa

from ..resource import RegisterIAXSchema


class TestRegisterIAXSchema(unittest.TestCase):

    def setUp(self):
        self.schema = RegisterIAXSchema(handle_error=False, exclude=('links', 'trunk'))

    def test_dump(self):
        register = Mock(var_val='auth_username:auth_password@'
                                'remote_host:6666/callback_extension?callback_context',
                        id=1)

        result = self.schema.dump(register)
        assert_that(
            result,
            has_entries(
                auth_username='auth_username',
                auth_password='auth_password',
                remote_host='remote_host',
                remote_port=6666,
                callback_extension='callback_extension',
                callback_context='callback_context',
            )
        )

    def test_dump_only_required(self):
        register = Mock(var_val='remote_host',
                        id=1)

        result = self.schema.dump(register)
        assert_that(
            result,
            has_entries(
                auth_username=None,
                auth_password=None,
                remote_host='remote_host',
                remote_port=None,
                callback_extension=None,
                callback_context=None,
            )
        )

    def test_dump_without_auth_username(self):
        register = Mock(var_val='remote_host:6666/callback_extension?callback_context',
                        id=1)

        result = self.schema.dump(register)
        assert_that(
            result,
            has_entries(
                auth_username=None,
                auth_password=None,
                remote_host='remote_host',
                remote_port=6666,
                callback_extension='callback_extension',
                callback_context='callback_context',
            )
        )

    def test_dump_without_auth_password(self):
        register = Mock(var_val='auth_username@'
                                'remote_host:6666/callback_extension?callback_context',
                        id=1)

        result = self.schema.dump(register)
        assert_that(
            result,
            has_entries(
                auth_username='auth_username',
                auth_password=None,
                remote_host='remote_host',
                remote_port=6666,
                callback_extension='callback_extension',
                callback_context='callback_context',
            )
        )

    def test_dump_without_remote_port(self):
        register = Mock(var_val='auth_username:auth_password@'
                                'remote_host/callback_extension?callback_context',
                        id=1)

        result = self.schema.dump(register)
        assert_that(
            result,
            has_entries(
                auth_username='auth_username',
                auth_password='auth_password',
                remote_host='remote_host',
                remote_port=None,
                callback_extension='callback_extension',
                callback_context='callback_context',
            )
        )

    def test_dump_without_callback_extension(self):
        register = Mock(var_val='auth_username:auth_password@'
                                'remote_host:6666?callback_context',
                        id=1)

        result = self.schema.dump(register)
        assert_that(
            result,
            has_entries(
                auth_username='auth_username',
                auth_password='auth_password',
                remote_host='remote_host',
                remote_port=6666,
                callback_extension=None,
                callback_context='callback_context',
            )
        )

    def test_load(self):
        body = {
            'auth_username': 'auth_username',
            'auth_password': 'auth_password',
            'remote_host': 'remote_host',
            'remote_port': 6666,
            'callback_extension': 'callback_extension',
            'callback_context': 'callback_context',
        }

        result = self.schema.load(body)

        assert_that(
            result['var_val'],
            equal_to('auth_username:auth_password@'
                     'remote_host:6666/callback_extension?callback_context'),
        )

    def test_load_only_required(self):
        body = {'remote_host': 'remote_host'}

        result = self.schema.load(body)

        assert_that(result['var_val'], equal_to('remote_host'))

    def test_load_without_auth_username(self):
        body = {
            'remote_host': 'remote_host',
            'remote_port': 6666,
            'callback_extension': 'callback_extension',
            'callback_context': 'callback_context',
        }

        result = self.schema.load(body)

        assert_that(result['var_val'], equal_to('remote_host:6666/callback_extension?callback_context'))

    # FIXME(sileht):
    @unittest.skip("This tests shouldn't have passed with marshmallow 2.x "
                   "but it does...")
    def test_load_without_auth_password(self):
        body = {
            'auth_username': 'auth_username',
            'remote_host': 'remote_host',
            'remote_port': 6666,
            'callback_extension': 'callback_extension',
            'callback_context': 'callback_context',
        }

        result = self.schema.load(body)

        assert_that(
            result['var_val'],
            equal_to('auth_username@'
                     'remote_host:6666/callback_extension?callback_context'),
        )

    def test_load_without_remote_port(self):
        body = {
            'auth_username': 'auth_username',
            'auth_password': 'auth_password',
            'remote_host': 'remote_host',
            'callback_extension': 'callback_extension',
            'callback_context': 'callback_context',
        }

        result = self.schema.load(body)

        assert_that(
            result['var_val'],
            equal_to('auth_username:auth_password@'
                     'remote_host/callback_extension?callback_context'),
        )

    def test_validate_total_length(self):
        body = {
            'auth_username': 'auth_username_really_really_really_really_really_really_really_long_string',
            'auth_password': 'auth_password_really_really_really_really_really_really_really_long_string',
            'remote_host': 'remote_host_really_really_really_really_really_really_really_long_string',
            'remote_port': 6666,
            'callback_extension': 'callback_extension_really_really_really_really_really_long_string',
        }

        assert_that(
            calling(self.schema.load).with_args(body),
            raises(ValidationError, has_property(
                'messages', has_key('_schema')
            ))
        )

    def test_validate_auth_username(self):
        body = {
            'auth_username': 'auth_username',
            'remote_host': 'remote_host',
        }

        assert_that(
            calling(self.schema.load).with_args(body),
            raises(ValidationError, has_property(
                'messages', has_key('auth_username')
            ))
        )

    def test_validate_callback_context(self):
        body = {
            'callback_context': 'callback_context',
            'remote_host': 'remote_host',
        }

        assert_that(
            calling(self.schema.load).with_args(body),
            raises(ValidationError, has_property(
                'messages', has_key('callback_context')
            ))
        )
