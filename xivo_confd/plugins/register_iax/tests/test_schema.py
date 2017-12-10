# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock
from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
    has_key,
)

from ..resource import RegisterIAXSchema


class TestRegisterIAXSchema(unittest.TestCase):

    def setUp(self):
        self.schema = RegisterIAXSchema(handle_error=False, exclude=('links',))

    def test_dump(self):
        register = Mock(var_val='auth_password:auth_username@'
                                'remote_host:6666/callback_extension?callback_context')

        result = self.schema.dump(register).data
        assert_that(result, has_entries(auth_password='auth_password',
                                        auth_username='auth_username',
                                        remote_host='remote_host',
                                        remote_port=6666,
                                        callback_extension='callback_extension',
                                        callback_context='callback_context'))

    def test_dump_only_required(self):
        register = Mock(var_val='remote_host')

        result = self.schema.dump(register).data
        assert_that(result, has_entries(auth_password=None,
                                        auth_username=None,
                                        remote_host='remote_host',
                                        remote_port=None,
                                        callback_extension=None,
                                        callback_context=None))

    def test_dump_without_auth_password(self):
        register = Mock(var_val='remote_host:6666/callback_extension?callback_context')

        result = self.schema.dump(register).data
        assert_that(result, has_entries(auth_password=None,
                                        auth_username=None,
                                        remote_host='remote_host',
                                        remote_port=6666,
                                        callback_extension='callback_extension',
                                        callback_context='callback_context'))

    def test_dump_without_auth_username(self):
        register = Mock(var_val='auth_password@'
                                'remote_host:6666/callback_extension?callback_context')

        result = self.schema.dump(register).data
        assert_that(result, has_entries(auth_password='auth_password',
                                        auth_username=None,
                                        remote_host='remote_host',
                                        remote_port=6666,
                                        callback_extension='callback_extension',
                                        callback_context='callback_context'))

    def test_dump_without_remote_port(self):
        register = Mock(var_val='auth_password:auth_username@'
                                'remote_host/callback_extension?callback_context')

        result = self.schema.dump(register).data
        assert_that(result, has_entries(auth_password='auth_password',
                                        auth_username='auth_username',
                                        remote_host='remote_host',
                                        remote_port=None,
                                        callback_extension='callback_extension',
                                        callback_context='callback_context'))

    def test_dump_without_callback_extension(self):
        register = Mock(var_val='auth_password:auth_username@'
                                'remote_host:6666?callback_context')

        result = self.schema.dump(register).data
        assert_that(result, has_entries(auth_password='auth_password',
                                        auth_username='auth_username',
                                        remote_host='remote_host',
                                        remote_port=6666,
                                        callback_extension=None,
                                        callback_context='callback_context'))

    def test_load(self):
        body = dict(auth_password='auth_password',
                    auth_username='auth_username',
                    remote_host='remote_host',
                    remote_port=6666,
                    callback_extension='callback_extension',
                    callback_context='callback_context')

        result = self.schema.load(body).data

        assert_that(result['var_val'], equal_to('auth_password:auth_username@'
                                                'remote_host:6666/callback_extension?callback_context'))

    def test_load_only_required(self):
        body = dict(remote_host='remote_host')

        result = self.schema.load(body).data

        assert_that(result['var_val'], equal_to('remote_host'))

    def test_load_without_auth_password(self):
        body = dict(remote_host='remote_host',
                    remote_port=6666,
                    callback_extension='callback_extension',
                    callback_context='callback_context')

        result = self.schema.load(body).data

        assert_that(result['var_val'], equal_to('remote_host:6666/callback_extension?callback_context'))

    def test_load_without_auth_username(self):
        body = dict(auth_password='auth_password',
                    remote_host='remote_host',
                    remote_port=6666,
                    callback_extension='callback_extension',
                    callback_context='callback_context')

        result = self.schema.load(body).data

        assert_that(result['var_val'], equal_to('auth_password@'
                                                'remote_host:6666/callback_extension?callback_context'))

    def test_load_without_remote_port(self):
        body = dict(auth_password='auth_password',
                    auth_username='auth_username',
                    remote_host='remote_host',
                    callback_extension='callback_extension',
                    callback_context='callback_context')

        result = self.schema.load(body).data

        assert_that(result['var_val'], equal_to('auth_password:auth_username@'
                                                'remote_host/callback_extension?callback_context'))

    def test_validate_total_length(self):
        body = dict(auth_password='auth_password_really_really_really_really_really_really_really_long_string',
                    auth_username='auth_username_really_really_really_really_really_really_really_long_string',
                    remote_host='remote_host_really_really_really_really_really_really_really_long_string',
                    remote_port=6666,
                    callback_extension='callback_extension_really_really_really_really_really_long_string')

        result = self.schema.load(body).errors
        assert_that(result, has_key('_schema'))

    def test_validate_auth_username(self):
        body = dict(auth_username='auth_username',
                    remote_host='remote_host')

        result = self.schema.load(body).errors
        assert_that(result, has_key('auth_username'))

    def test_validate_callback_context(self):
        body = dict(callback_context='callback_context',
                    remote_host='remote_host')

        result = self.schema.load(body).errors
        assert_that(result, has_key('callback_context'))
