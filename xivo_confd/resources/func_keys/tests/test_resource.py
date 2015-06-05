# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import unittest
from mock import sentinel, Mock, patch
from hamcrest import assert_that, equal_to, is_not, has_key, calling, raises

from xivo_confd.helpers.converter import Converter

from xivo_confd.resources.func_keys.service import TemplateService
from xivo_confd.resources.func_keys.resource import FuncKeyResource

from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.func_key.model import FuncKey
from xivo_dao.resources.func_key_template.model import FuncKeyTemplate


@patch('xivo_confd.resources.func_keys.resource.request')
class TestFuncKeyTemplateResource(unittest.TestCase):

    def setUp(self):
        self.service = Mock(TemplateService)
        self.funckey_converter = Mock(Converter)

        self.resource = FuncKeyResource(self.service,
                                        self.funckey_converter)

    def test_when_getting_func_key_then_returns_encoded_funckey(self, request):
        funckey = Mock(FuncKey)
        template = FuncKeyTemplate(keys={1: funckey})
        self.service.get.return_value = template

        expected_response = self.funckey_converter.encode.return_value

        response = self.resource.get_funckey(sentinel.template_id, 1)

        assert_that(response, equal_to((expected_response, 200,
                                        {'Content-Type': 'application/json'})))

    def test_given_template_empty_when_getting_func_key_then_raises_error(self, request):
        template = FuncKeyTemplate(keys={})
        self.service.get.return_value = template

        assert_that(calling(self.resource.get_funckey).with_args(sentinel.template_id, 1),
                    raises(NotFoundError))

    def test_when_updating_func_key_then_updates_template_using_request(self, request):
        funckey = Mock(FuncKey)
        expected_funckey = Mock(FuncKey)

        template = FuncKeyTemplate(keys={1: funckey})
        self.service.get.return_value = template
        self.funckey_converter.decode.return_value = expected_funckey

        response = self.resource.update_funckey(sentinel.template_id, 1)

        assert_that(template.keys[1], equal_to(expected_funckey))
        assert_that(response, equal_to(('', 204)))
        self.service.get.assert_called_once_with(sentinel.template_id)
        self.service.edit.assert_called_once_with(template)

    def test_given_position_does_not_exist_when_updating_then_adds_key(self, request):
        expected_funckey = Mock(FuncKey)

        template = FuncKeyTemplate(keys={})
        self.service.get.return_value = template
        self.funckey_converter.decode.return_value = expected_funckey

        self.resource.update_funckey(sentinel.template_id, 2)

        assert_that(template.keys[2], equal_to(expected_funckey))

    def test_when_deleting_func_key_then_removes_func_key_from_template(self, request):
        funckey = Mock(FuncKey)
        template = FuncKeyTemplate(keys={1: funckey})
        self.service.get.return_value = template

        self.resource.remove_funckey(sentinel.template_id, 1)

        assert_that(template.keys, is_not(has_key(1)))
        self.service.get.assert_called_once_with(sentinel.template_id)
        self.service.edit.assert_called_once_with(template)

    def test_given_template_is_empty_when_deleting_func_key_then_returns_success(self, request):
        template = FuncKeyTemplate(keys={})
        self.service.get.return_value = template

        response = self.resource.remove_funckey(sentinel.template_id, 1)

        assert_that(response, equal_to(('', 204)))
