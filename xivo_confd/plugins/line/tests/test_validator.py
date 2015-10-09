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
from mock import Mock

from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.helpers.exception import ResourceError

from xivo_confd.plugins.line.validator import ProvCodeAvailable, ProvCodeChanged


class TestProvCodeAvailble(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = ProvCodeAvailable(self.dao)

    def test_given_no_lines_with_code_then_validation_passes(self):
        self.dao.find_by.return_value = None
        line = Mock(Line, provisioning_code="123456", provisioningid=123456)

        self.validator.validate(line)

        self.dao.find_by.assert_called_once_with(provisioningid=123456)

    def test_given_line_with_same_code_exists_then_validation_fails(self):
        line = Mock(Line, provisioning_code="123456", provisioningid=123456)
        self.dao.find_by.return_value = line

        self.assertRaises(ResourceError, self.validator.validate, line)
        self.dao.find_by.assert_called_once_with(provisioningid=123456)


class TestProvCodeChanged(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = ProvCodeChanged(self.dao)

    def test_given_code_has_not_changed_then_validation_passes(self):
        line = Mock(Line, id=1, provisioning_code="123456", provisioningid=123456)
        self.dao.get.return_value = line

        self.validator.validate(line)

        self.dao.get.assert_called_once_with(line.id)

    def test_given_code_has_changed_and_is_available_then_validation_passes(self):
        existing_line = Mock(Line, id=1, provisioning_code="123456", provisioningid=123456)
        new_line = Mock(Line, id=1, provisioning_code="234567", provisioningid=234567)

        self.dao.get.return_value = existing_line
        self.dao.find_by.return_value = None

        self.validator.validate(new_line)

        self.dao.get.assert_called_once_with(new_line.id)
        self.dao.find_by.assert_called_once_with(provisioningid=234567)

    def test_given_code_has_changed_and_same_code_exists_then_validation_fails(self):
        old_line = Mock(Line, id=1, provisioning_code="123456", provisioningid=123456)
        new_line = Mock(Line, id=1, provisioning_code="234567", provisioningid=234567)
        existing_line = Mock(Line, id=2, provisioning_code="234567", provisioningid=234567)

        self.dao.get.return_value = old_line
        self.dao.find_by.return_value = existing_line

        self.assertRaises(ResourceError, self.validator.validate, new_line)

        self.dao.get.assert_called_once_with(new_line.id)
        self.dao.find_by.assert_called_once_with(provisioningid=234567)
