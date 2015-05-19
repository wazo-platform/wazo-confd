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

from mock import patch, Mock

from xivo_dao.helpers.exception import ResourceError
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers.exception import InputError

from xivo_dao.resources.extension.model import Extension
from xivo_dao.resources.line_extension.model import LineExtension
from xivo_dao.resources.user_line.model import UserLine

from xivo_confd.resources.line_extension import validator


class TestValidateModel(unittest.TestCase):

    def test_validate_model_no_parameters(self):
        line_extension = LineExtension()

        self.assertRaises(InputError, validator.validate_model, line_extension)


class TestValidateLine(unittest.TestCase):

    @patch('xivo_dao.resources.line.dao.get')
    def test_validate_line_when_no_line(self, line_get):
        line_extension = Mock(LineExtension, line_id=1)

        line_get.side_effect = NotFoundError

        self.assertRaises(InputError, validator.validate_line, line_extension)
        line_get.assert_called_once_with(line_extension.line_id)

    @patch('xivo_dao.resources.line.dao.get')
    def test_validate_line_with_line(self, line_get):
        line_extension = Mock(LineExtension, line_id=1)

        line_get.return_value = line_extension

        validator.validate_line(line_extension)
        line_get.assert_called_once_with(line_extension.line_id)


class TestValidateExtension(unittest.TestCase):

    @patch('xivo_dao.resources.extension.dao.get')
    def test_validate_extension_when_no_extension(self, extension_get):
        line_extension = Mock(LineExtension, line_id=1, extension_id=2)

        extension_get.side_effect = NotFoundError

        self.assertRaises(InputError, validator.validate_extension, line_extension)
        extension_get.assert_called_once_with(line_extension.extension_id)

    @patch('xivo_dao.resources.extension.dao.get')
    def test_validate_extension_with_extension(self, extension_get):
        line_extension = Mock(LineExtension, line_id=1, extension_id=2)
        extension_get.return_value = Mock(Extension, id=2)

        validator.validate_extension(line_extension)

        extension_get.assert_called_once_with(line_extension.extension_id)


class TestValidateLineNotAssociatedToExtension(unittest.TestCase):

    @patch('xivo_dao.resources.line_extension.dao.find_by_line_id')
    def test_validate_line_not_associated_to_extension_with_extension(self, find_by_line_id):
        line_extension = Mock(LineExtension, line_id=1, extension_id=2)

        find_by_line_id.return_value = Mock()

        self.assertRaises(ResourceError, validator.validate_line_not_associated_to_extension, line_extension)
        find_by_line_id.assert_called_once_with(line_extension.line_id)

    @patch('xivo_dao.resources.line_extension.dao.find_by_line_id')
    def test_validate_line_not_associated_to_extension_with_no_extension(self, find_by_line_id):
        line_extension = Mock(LineExtension, line_id=1, extension_id=2)

        find_by_line_id.return_value = None

        validator.validate_line_not_associated_to_extension(line_extension)
        find_by_line_id.assert_called_once_with(line_extension.line_id)


class TestValidateAssociatedToUser(unittest.TestCase):

    @patch('xivo_dao.resources.user_line.dao.find_all_by_line_id')
    def test_given_user_not_associated_to_line_then_raises_error(self, find_all_by_line_id):
        find_all_by_line_id.return_value = None
        line_extension = Mock(LineExtension, line_id=1)

        self.assertRaises(ResourceError, validator.validate_associated_to_user, line_extension)

    @patch('xivo_dao.resources.user_line.dao.find_all_by_line_id')
    def test_given_user_associated_to_line_then_validation_passes(self, find_all_by_line_id):
        find_all_by_line_id.return_value = [Mock(UserLine)]
        line_extension = Mock(LineExtension, line_id=1)

        validator.validate_associated_to_user(line_extension)
        find_all_by_line_id.assert_called_once_with(line_extension.line_id)


@patch('xivo_dao.resources.incall.dao.find_all_line_extensions_by_line_id')
@patch('xivo_dao.resources.line_extension.dao.find_all_by_line_id')
class TestValidateAssociated(unittest.TestCase):

    def test_given_line_not_associated_to_extension_then_raises_error(self,
                                                                      find_all_by_line_id,
                                                                      find_all_line_extensions_by_line_id):
        find_all_by_line_id.return_value = []

        line_extension = Mock(LineExtension, line_id=1, extension_id=2)

        self.assertRaises(ResourceError, validator.validate_associated, line_extension)

    def test_given_line_associated_to_internal_extension_then_validation_passes(self,
                                                                                find_all_by_line_id,
                                                                                find_all_line_extensions_by_line_id):
        line_extension = Mock(LineExtension, line_id=1, extension_id=2)
        find_all_by_line_id.return_value = [line_extension]
        find_all_line_extensions_by_line_id.return_value = []

        validator.validate_associated(line_extension)

        find_all_by_line_id.assert_called_once_with(line_extension.line_id)

    def test_given_line_associated_to_incall_extension_then_validation_passes(self,
                                                                              find_all_by_line_id,
                                                                              find_all_line_extensions_by_line_id):
        line_extension = Mock(LineExtension, line_id=1, extension_id=2)
        find_all_by_line_id.return_value = []
        find_all_line_extensions_by_line_id.return_value = [line_extension]

        validator.validate_associated(line_extension)

        find_all_by_line_id.assert_called_once_with(line_extension.line_id)
        find_all_line_extensions_by_line_id.assert_called_once_with(line_extension.line_id)
