# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 Avencall
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
from hamcrest import assert_that, equal_to, none

from mock import Mock, sentinel
from xivo_confd.plugins.device.update import DeviceUpdater
from xivo_confd.plugins.device.service import DeviceService, SearchEngine, LineDeviceAssociationService
from xivo_confd.plugins.device.dao import DeviceDao
from xivo_confd.plugins.device.model import Device

from xivo_dao.alchemy.linefeatures import LineFeatures as Line


class TestDeviceService(unittest.TestCase):

    def setUp(self):
        self.device_dao = Mock(DeviceDao)
        self.validator = Mock()
        self.notifier = Mock()
        self.search_engine = Mock(SearchEngine)
        self.associator = Mock()

        self.service = DeviceService(self.device_dao,
                                     self.validator,
                                     self.notifier,
                                     self.search_engine,
                                     self.associator)

    def test_given_search_query_when_searching_then_calls_search_engine(self):
        result = self.service.search(sentinel.parameters)

        assert_that(result, equal_to(self.search_engine.search.return_value))
        self.search_engine.search.assert_called_once_with(sentinel.parameters)

    def test_when_synchronizing_then_synchronizes_using_dao(self):
        self.service.synchronize(sentinel.device)

        self.device_dao.synchronize.assert_called_once_with(sentinel.device)

    def test_when_resetting_to_autprov_then_resets_device_to_autoprov_using_dao(self):
        device = Mock(Device, id=sentinel.device_id)
        self.service.reset_autoprov(device)

        self.device_dao.reset_autoprov.assert_called_once_with(device)

    def test_when_resetting_to_autoprov_then_resets_line_associated_to_device(self):
        device = Mock(Device, id=sentinel.device_id)

        self.service.reset_autoprov(device)

        self.associator.dissociate_device.assert_called_once_with(device)


class TestLineDeviceAssociationService(unittest.TestCase):

    def setUp(self):
        self.device_updater = Mock(DeviceUpdater)
        self.line_dao = Mock()
        self.service = LineDeviceAssociationService(self.line_dao, self.device_updater)

    def test_when_associating_a_line_to_a_device_then_updates_device_id_on_line(self):
        device = Mock(Device, id=sentinel.device_id)
        line = Mock(Line)

        self.service.associate(line, device)

        assert_that(line.device_id, equal_to(sentinel.device_id))
        self.line_dao.edit.assert_called_once_with(line)

    def test_when_associating_a_line_to_a_device_then_updates_lines_on_device(self):
        device = Mock(Device, id=sentinel.device_id)
        line = Mock(Line)

        self.service.associate(line, device)

        self.device_updater.update_for_line.assert_called_once_with(line)

    def test_when_dissociating_a_line_to_a_device_then_removes_device_id_on_line(self):
        device = Mock(Device, id=sentinel.device_id)
        line = Mock(device_id=sentinel.device_id)

        self.service.dissociate(line, device)

        assert_that(line.device_id, equal_to(None))
        self.line_dao.edit.assert_called_once_with(line)

    def test_when_dissociating_a_line_to_a_device_then_updates_lines_on_device(self):
        device = Mock(Device, id=sentinel.device_id)
        line = Mock(Line)

        self.service.dissociate(line, device)

        self.device_updater.update_for_line.assert_called_once_with(line)
