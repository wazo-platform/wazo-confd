# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock
from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
    has_key,
)

from wazo_confd.plugins.trunk.resource import TrunkSchema  # noqa

from ..resource import RegisterSIPSchema


class TestRegisterSIPSchema(unittest.TestCase):

    def setUp(self):
        self.schema = RegisterSIPSchema(handle_error=False, exclude=('links',))

    def test_dump(self):
        register = Mock(var_val='tcp://sip_username:auth_password:auth_username@'
                                'remote_host:6666/callback_extension~10')

        result = self.schema.dump(register).data
        assert_that(result, has_entries(transport='tcp',
                                        sip_username='sip_username',
                                        auth_password='auth_password',
                                        auth_username='auth_username',
                                        remote_host='remote_host',
                                        remote_port=6666,
                                        callback_extension='callback_extension',
                                        expiration=10))

    def test_dump_only_required(self):
        register = Mock(var_val='sip_username@remote_host')

        result = self.schema.dump(register).data
        assert_that(result, has_entries(transport=None,
                                        sip_username='sip_username',
                                        auth_password=None,
                                        auth_username=None,
                                        remote_host='remote_host',
                                        remote_port=None,
                                        callback_extension=None,
                                        expiration=None))

    def test_dump_without_transport(self):
        register = Mock(var_val='sip_username:auth_password:auth_username@'
                                'remote_host:6666/callback_extension~10')

        result = self.schema.dump(register).data
        assert_that(result, has_entries(transport=None,
                                        sip_username='sip_username',
                                        auth_password='auth_password',
                                        auth_username='auth_username',
                                        remote_host='remote_host',
                                        remote_port=6666,
                                        callback_extension='callback_extension',
                                        expiration=10))

    def test_dump_without_auth_password(self):
        register = Mock(var_val='tcp://sip_username@'
                                'remote_host:6666/callback_extension~10')

        result = self.schema.dump(register).data
        assert_that(result, has_entries(transport='tcp',
                                        sip_username='sip_username',
                                        auth_password=None,
                                        auth_username=None,
                                        remote_host='remote_host',
                                        remote_port=6666,
                                        callback_extension='callback_extension',
                                        expiration=10))

    def test_dump_without_auth_username(self):
        register = Mock(var_val='tcp://sip_username:auth_password@'
                                'remote_host:6666/callback_extension~10')

        result = self.schema.dump(register).data
        assert_that(result, has_entries(transport='tcp',
                                        sip_username='sip_username',
                                        auth_password='auth_password',
                                        auth_username=None,
                                        remote_host='remote_host',
                                        remote_port=6666,
                                        callback_extension='callback_extension',
                                        expiration=10))

    def test_dump_without_remote_port(self):
        register = Mock(var_val='tcp://sip_username:auth_password:auth_username@'
                                'remote_host/callback_extension~10')

        result = self.schema.dump(register).data
        assert_that(result, has_entries(transport='tcp',
                                        sip_username='sip_username',
                                        auth_password='auth_password',
                                        auth_username='auth_username',
                                        remote_host='remote_host',
                                        remote_port=None,
                                        callback_extension='callback_extension',
                                        expiration=10))

    def test_dump_without_callback_extension(self):
        register = Mock(var_val='tcp://sip_username:auth_password:auth_username@'
                                'remote_host:6666~10')

        result = self.schema.dump(register).data
        assert_that(result, has_entries(transport='tcp',
                                        sip_username='sip_username',
                                        auth_password='auth_password',
                                        auth_username='auth_username',
                                        remote_host='remote_host',
                                        remote_port=6666,
                                        callback_extension=None,
                                        expiration=10))

    def test_dump_without_expiration(self):
        register = Mock(var_val='tcp://sip_username:auth_password:auth_username@'
                                'remote_host:6666/callback_extension')

        result = self.schema.dump(register).data
        assert_that(result, has_entries(transport='tcp',
                                        sip_username='sip_username',
                                        auth_password='auth_password',
                                        auth_username='auth_username',
                                        remote_host='remote_host',
                                        remote_port=6666,
                                        callback_extension='callback_extension',
                                        expiration=None))

    def test_load(self):
        body = dict(transport='tcp',
                    sip_username='sip_username',
                    auth_password='auth_password',
                    auth_username='auth_username',
                    remote_host='remote_host',
                    remote_port=6666,
                    callback_extension='callback_extension',
                    expiration=10)

        result = self.schema.load(body).data

        assert_that(result['var_val'], equal_to('tcp://sip_username:auth_password:auth_username@'
                                                'remote_host:6666/callback_extension~10'))

    def test_load_only_required(self):
        body = dict(sip_username='sip_username',
                    remote_host='remote_host')

        result = self.schema.load(body).data

        assert_that(result['var_val'], equal_to('sip_username@remote_host'))

    def test_load_without_protocol(self):
        body = dict(sip_username='sip_username',
                    auth_password='auth_password',
                    auth_username='auth_username',
                    remote_host='remote_host',
                    remote_port=6666,
                    callback_extension='callback_extension',
                    expiration=10)

        result = self.schema.load(body).data

        assert_that(result['var_val'], equal_to('sip_username:auth_password:auth_username@'
                                                'remote_host:6666/callback_extension~10'))

    def test_load_without_auth_password(self):
        body = dict(transport='tcp',
                    sip_username='sip_username',
                    remote_host='remote_host',
                    remote_port=6666,
                    callback_extension='callback_extension',
                    expiration=10)

        result = self.schema.load(body).data

        assert_that(result['var_val'], equal_to('tcp://sip_username@'
                                                'remote_host:6666/callback_extension~10'))

    def test_load_without_auth_username(self):
        body = dict(transport='tcp',
                    sip_username='sip_username',
                    auth_password='auth_password',
                    remote_host='remote_host',
                    remote_port=6666,
                    callback_extension='callback_extension',
                    expiration=10)

        result = self.schema.load(body).data

        assert_that(result['var_val'], equal_to('tcp://sip_username:auth_password@'
                                                'remote_host:6666/callback_extension~10'))

    def test_load_without_remote_port(self):
        body = dict(transport='tcp',
                    sip_username='sip_username',
                    auth_password='auth_password',
                    auth_username='auth_username',
                    remote_host='remote_host',
                    callback_extension='callback_extension',
                    expiration=10)

        result = self.schema.load(body).data

        assert_that(result['var_val'], equal_to('tcp://sip_username:auth_password:auth_username@'
                                                'remote_host/callback_extension~10'))

    def test_load_without_callback_extension(self):
        body = dict(transport='tcp',
                    sip_username='sip_username',
                    auth_password='auth_password',
                    auth_username='auth_username',
                    remote_host='remote_host',
                    remote_port=6666,
                    expiration=10)

        result = self.schema.load(body).data

        assert_that(result['var_val'], equal_to('tcp://sip_username:auth_password:auth_username@'
                                                'remote_host:6666~10'))

    def test_load_without_expiration(self):
        body = dict(transport='tcp',
                    sip_username='sip_username',
                    auth_password='auth_password',
                    auth_username='auth_username',
                    remote_host='remote_host',
                    remote_port=6666,
                    callback_extension='callback_extension')

        result = self.schema.load(body).data

        assert_that(result['var_val'], equal_to('tcp://sip_username:auth_password:auth_username@'
                                                'remote_host:6666/callback_extension'))

    def test_validate_total_length(self):
        body = dict(transport='tcp',
                    sip_username='sip_username_really_really_long_string',
                    auth_password='auth_password_really_really_long_string',
                    auth_username='auth_username_really_really_really_really_really_long_string',
                    remote_host='remote_host_really_really_really_really_really_really_really_long_string',
                    remote_port=6666,
                    callback_extension='callback_extension_really_long_string')

        result = self.schema.load(body).errors
        assert_that(result, has_key('_schema'))

    def test_validate_auth_username(self):
        body = dict(sip_username='sip_username',
                    auth_username='auth_username',
                    remote_host='remote_host')

        result = self.schema.load(body).errors
        assert_that(result, has_key('auth_username'))
