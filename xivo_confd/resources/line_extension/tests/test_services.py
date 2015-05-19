# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest
from mock import Mock, patch
from hamcrest import assert_that, equal_to, has_items, none

from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.context.model import Context
from xivo_dao.resources.line.model import Line
from xivo_dao.resources.line_extension.model import LineExtension

from xivo_confd.resources.line_extension import services as line_extension_service


@patch('xivo_confd.resources.line_extension.notifier.associated')
@patch('xivo_confd.resources.line_extension.services.association_manager')
class TestLineExtensionAssociate(unittest.TestCase):

    def test_associate(self, manager, notifier_associated):
        line_extension = Mock(LineExtension)

        result = line_extension_service.associate(line_extension)
        assert_that(result, equal_to(line_extension))

        manager.associate.assert_called_once_with(line_extension)
        notifier_associated.assert_called_once_with(line_extension)


class TestGetByLineId(unittest.TestCase):

    @patch('xivo_dao.resources.line_extension.dao.get_by_line_id')
    @patch('xivo_dao.resources.line.dao.get')
    def test_get_by_line_id(self, line_get, dao_get_by_line_id):
        line = line_get.return_value = Mock(Line, id=1)
        line_extension = dao_get_by_line_id.return_value = Mock(LineExtension, line_id=line.id)

        result = line_extension_service.get_by_line_id(line.id)

        assert_that(result, equal_to(line_extension))
        line_get.assert_called_once_with(line.id)
        dao_get_by_line_id.assert_called_once_with(line.id)


class TestFindByLineId(unittest.TestCase):

    @patch('xivo_dao.resources.line_extension.dao.find_by_line_id')
    def test_find_by_line_id(self, dao_find_by_line_id):
        line_extension = Mock(LineExtension, line_id=1)
        dao_find_by_line_id.return_value = line_extension

        result = line_extension_service.find_by_line_id(1)

        assert_that(result, equal_to(line_extension))
        dao_find_by_line_id.assert_called_once_with(1)


class TestFindByExtensionId(unittest.TestCase):

    @patch('xivo_dao.resources.context.dao.find_by_extension_id')
    def test_given_extension_does_not_exist_then_returns_nothing(self, context_find_by_extension_id):
        context_find_by_extension_id.return_value = None

        result = line_extension_service.find_by_extension_id(2)

        assert_that(result, none())
        context_find_by_extension_id.assert_called_once_with(2)

    @patch('xivo_dao.resources.line_extension.dao.find_by_extension_id')
    @patch('xivo_dao.resources.context.dao.find_by_extension_id')
    def test_given_internal_extension_then_returns_line_extension(self,
                                                                  context_find_by_extension_id,
                                                                  line_extension_find_by_extension_id):
        context_find_by_extension_id.return_value = Mock(Context, type='internal')
        line_extension = line_extension_find_by_extension_id.return_value = Mock(LineExtension, line_id=1, extension_id=2)

        result = line_extension_service.find_by_extension_id(2)

        assert_that(result, equal_to(line_extension))
        context_find_by_extension_id.assert_called_once_with(2)
        line_extension_find_by_extension_id.assert_called_once_with(2)

    @patch('xivo_dao.resources.incall.dao.find_line_extension_by_extension_id')
    @patch('xivo_dao.resources.context.dao.find_by_extension_id')
    def test_given_incall_extension_then_returns_line_extension(self,
                                                                context_find_by_extension_id,
                                                                find_line_extension_by_extension_id):
        context_find_by_extension_id.return_value = Mock(Context, type='incall')
        line_extension = find_line_extension_by_extension_id.return_value = Mock(LineExtension, line_id=1, extension_id=2)

        result = line_extension_service.find_by_extension_id(2)

        assert_that(result, equal_to(line_extension))
        context_find_by_extension_id.assert_called_once_with(2)
        find_line_extension_by_extension_id.assert_called_once_with(2)


class TestGetByExtensionId(unittest.TestCase):

    @patch('xivo_dao.resources.context.dao.find_by_extension_id')
    def test_given_extension_does_not_exist_then_raises_error(self, context_find_by_extension_id):
        context_find_by_extension_id.return_value = None

        self.assertRaises(NotFoundError, line_extension_service.get_by_extension_id, 2)

    @patch('xivo_dao.resources.line_extension.dao.find_by_extension_id')
    @patch('xivo_dao.resources.context.dao.find_by_extension_id')
    def test_given_internal_extension_then_returns_line_extension(self,
                                                                  context_find_by_extension_id,
                                                                  line_extension_find_by_extension_id):
        line_extension = line_extension_find_by_extension_id.return_value = Mock(LineExtension, line_id=1, extension_id=2)
        context_find_by_extension_id.return_value = Mock(Context, type='internal')

        result = line_extension_service.get_by_extension_id(2)

        assert_that(result, equal_to(line_extension))
        context_find_by_extension_id.assert_called_once_with(2)
        line_extension_find_by_extension_id.assert_called_once_with(2)

    @patch('xivo_dao.resources.line_extension.dao.find_by_extension_id')
    @patch('xivo_dao.resources.context.dao.find_by_extension_id')
    def test_given_internal_extension_without_line_then_raises_error(self,
                                                                     context_find_by_extension_id,
                                                                     line_extension_find_by_extension_id):
        context_find_by_extension_id.return_value = Mock(Context, type='internal')
        line_extension_find_by_extension_id.return_value = None

        self.assertRaises(NotFoundError, line_extension_service.get_by_extension_id, 2)
        line_extension_find_by_extension_id.assert_called_once_with(2)

    @patch('xivo_dao.resources.incall.dao.find_line_extension_by_extension_id')
    @patch('xivo_dao.resources.context.dao.find_by_extension_id')
    def test_given_incall_extension_then_returns_line_extension(self,
                                                                context_find_by_extension_id,
                                                                find_line_extension_by_extension_id):
        line_extension = find_line_extension_by_extension_id.return_value = Mock(LineExtension, line_id=1, extension_id=2)
        context_find_by_extension_id.return_value = Mock(Context, type='incall')

        result = line_extension_service.get_by_extension_id(2)

        assert_that(result, equal_to(line_extension))
        context_find_by_extension_id.assert_called_once_with(2)
        find_line_extension_by_extension_id.assert_called_once_with(2)

    @patch('xivo_dao.resources.incall.dao.find_line_extension_by_extension_id')
    @patch('xivo_dao.resources.context.dao.find_by_extension_id')
    def test_given_incall_extension_without_line_then_raises_error(self,
                                                                   context_find_by_extension_id,
                                                                   find_line_extension_by_extension_id):
        context_find_by_extension_id.return_value = Mock(Context, type='incall')
        find_line_extension_by_extension_id.return_value = None

        self.assertRaises(NotFoundError, line_extension_service.get_by_extension_id, 2)
        find_line_extension_by_extension_id.assert_called_once_with(2)


@patch('xivo_confd.resources.line_extension.notifier.dissociated')
@patch('xivo_confd.resources.line_extension.services.association_manager')
class TestLineExtensionDissociate(unittest.TestCase):

    def test_dissociate(self, manager, notifier_dissociated):
        line_extension = Mock(LineExtension)

        result = line_extension_service.dissociate(line_extension)
        assert_that(result, equal_to(line_extension))

        manager.dissociate.assert_called_once_with(line_extension)
        notifier_dissociated.assert_called_once_with(line_extension)


class TestGetAllByLineId(unittest.TestCase):

    @patch('xivo_dao.resources.incall.dao.find_all_line_extensions_by_line_id')
    @patch('xivo_dao.resources.line_extension.dao.find_all_by_line_id')
    @patch('xivo_dao.resources.line.dao.get')
    def test_get_all_by_line_id(self,
                                line_get,
                                line_extension_find_all_by_line_id,
                                incall_find_all_line_extension_by_line_id):

        line = line_get.return_value = Mock(Line, id=1)
        line_extension = Mock(LineExtension)
        incall_line_extension = Mock(LineExtension)

        line_extension_find_all_by_line_id.return_value = [line_extension]
        incall_find_all_line_extension_by_line_id.return_value = [incall_line_extension]

        result = line_extension_service.get_all_by_line_id(line.id)

        assert_that(result, has_items(line_extension, incall_line_extension))
        line_get.assert_called_once_with(line.id)
        line_extension_find_all_by_line_id.assert_called_once_with(line.id)
        incall_find_all_line_extension_by_line_id.assert_called_once_with(line.id)
