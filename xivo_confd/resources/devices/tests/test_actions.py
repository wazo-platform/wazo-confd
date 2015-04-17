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
from mock import Mock, sentinel
from hamcrest import assert_that, equal_to

from xivo_confd.resources.devices.actions import DeviceResource


class TestDeviceResource(unittest.TestCase):

    def setUp(self):
        self.service = Mock()
        self.line_service = Mock()
        self.resource = DeviceResource(self.service, self.line_service, Mock())

    def test_synchronize_synchronizes_device(self):
        expected_device = self.service.get.return_value

        response = self.resource.synchronize(sentinel.device_id)

        self.service.synchronize.assert_called_once_with(expected_device)
        assert_that(response, equal_to(('', 204)))

    def test_autoprov_resets_device_to_autoprov(self):
        expected_device = self.service.get.return_value

        response = self.resource.autoprov(sentinel.device_id)

        self.service.reset_to_autoprov.assert_called_once_with(expected_device)
        assert_that(response, equal_to(('', 204)))

    def test_associate_line_associates_line_and_device(self):
        expected_device = self.service.get.return_value
        expected_line = self.line_service.get.return_value

        response = self.resource.associate_line(sentinel.device_id, sentinel.line_id)

        self.service.associate_line_to_device.assert_called_once_with(expected_device, expected_line)
        assert_that(response, equal_to(('', 204)))

    def test_remove_line_removes_line_from_device(self):
        expected_device = self.service.get.return_value
        expected_line = self.line_service.get.return_value

        response = self.resource.remove_line(sentinel.device_id, sentinel.line_id)

        self.service.remove_line_from_device.assert_called_once_with(expected_device, expected_line)
        assert_that(response, equal_to(('', 204)))
