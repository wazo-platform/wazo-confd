# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from mock import Mock

from xivo_confd.resources.extensions.actions import ExtensionService


class TestExtensionService(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.line_extension_dao = Mock()
        self.line_dao = Mock()
        self.validator = Mock()
        self.notifier = Mock()

        self.service = ExtensionService(self.dao, self.line_extension_dao,
                                        self.line_dao, self.validator, self.notifier)

    def test_when_editing_an_extension_then_dependencies_called(self):
        extension = Mock()

        self.service.edit(extension)

        self.validator.validate_edit.assert_called_once_with(extension)
        self.dao.edit.assert_called_once_with(extension)
        self.notifier.edited.assert_called_once_with(extension)

    def test_given_extension_has_line_then_extension_gets_associated(self):
        extension = Mock(id=1111)
        line_extension = Mock(line_id=1234)
        self.line_extension_dao.find_by_extension_id.return_value = line_extension

        self.service.edit(extension)

        self.line_extension_dao.find_by_extension_id.assert_called_once_with(extension.id)
        self.line_dao.associate_extension.assert_called_once_with(extension, line_extension.line_id)
