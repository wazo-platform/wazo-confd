# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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
from xivo_confd.resources.devices.service import DeviceService, DeviceValidator, SearchEngine, LineDeviceUpdater, DeviceUpdater, LineDeviceAssociationService
from xivo_confd.resources.devices.dao import DeviceDao
from xivo_confd.resources.devices.model import LineSCCPConverter, LineSIPConverter

from xivo_confd.resources.devices.model import Device
from xivo_dao.resources.extension.model import Extension
from xivo_dao.resources.line_extension.model import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures as Line


class TestDeviceService(unittest.TestCase):

    def setUp(self):
        self.device_dao = Mock(DeviceDao)
        self.validator = Mock(DeviceValidator)
        self.notifier = Mock()
        self.search_engine = Mock(SearchEngine)
        self.line_dao = Mock()

        self.service = DeviceService(self.device_dao,
                                     self.validator,
                                     self.notifier,
                                     self.search_engine,
                                     self.line_dao)

    def test_given_search_query_when_searching_then_calls_search_engine(self):
        result = self.service.search(sentinel.parameters)

        assert_that(result, equal_to(self.search_engine.search.return_value))
        self.search_engine.search.assert_called_once_with(sentinel.parameters)

    def test_when_synchronizing_then_synchronizes_using_dao(self):
        self.service.synchronize(sentinel.device)

        self.device_dao.synchronize.assert_called_once_with(sentinel.device)

    def test_when_resetting_to_autprov_then_resets_device_to_autoprov_using_dao(self):
        device = Device(id=sentinel.device_id)
        self.service.reset_autoprov(device)

        self.device_dao.reset_autoprov.assert_called_once_with(device)

    def test_when_resetting_to_autoprov_then_resets_line_associated_to_device(self):
        device = Device(id=sentinel.device_id)
        line = self.line_dao.find_by.return_value

        self.service.reset_autoprov(device)

        self.line_dao.edit.assert_called_once_with(line)
        assert_that(line.device_id, none())


class TestLineDeviceAssociationService(unittest.TestCase):

    def setUp(self):
        self.device_updater = Mock(DeviceUpdater)
        self.line_dao = Mock()
        self.service = LineDeviceAssociationService(self.line_dao, self.device_updater)

    def test_when_associating_a_line_to_a_device_then_updates_device_id_on_line(self):
        device = Device(id=sentinel.device_id)
        line = Mock(Line)

        self.service.associate(line, device)

        assert_that(line.device_id, equal_to(sentinel.device_id))
        self.line_dao.edit.assert_called_once_with(line)

    def test_when_associating_a_line_to_a_device_then_updates_lines_on_device(self):
        device = Device(id=sentinel.device_id)
        line = Mock(Line)

        self.service.associate(line, device)

        self.device_updater.update_for_line.assert_called_once_with(line)

    def test_when_dissociating_a_line_to_a_device_then_removes_device_id_on_line(self):
        device = Device(id=sentinel.device_id)
        line = Mock(device_id=sentinel.device_id)

        self.service.dissociate(line, device)

        assert_that(line.device_id, equal_to(None))
        self.line_dao.edit.assert_called_once_with(line)

    def test_when_dissociating_a_line_to_a_device_then_updates_lines_on_device(self):
        device = Device(id=sentinel.device_id)
        line = Mock(Line)

        self.service.dissociate(line, device)

        self.device_updater.update_for_line.assert_called_once_with(line)


class TestLineDeviceUpdater(unittest.TestCase):

    def setUp(self):
        self.line_dao = Mock()
        self.extension_dao = Mock()
        self.line_extension_dao = Mock()
        self.device_dao = Mock(DeviceDao)
        self.service = LineDeviceUpdater(self.line_dao,
                                         self.extension_dao,
                                         self.line_extension_dao,
                                         self.device_dao)

        self.device = Device(id=sentinel.device_id)

        self.device_dao.get_registrar.return_value = sentinel.registrar

    def build_line(self, **kwargs):
        parameters = {'id': sentinel.line_id,
                      'device_id': sentinel.device_id,
                      'configregistrar': 'registrar'}
        parameters.update(kwargs)
        line = Mock(Line, **parameters)
        self.line_dao.find_all_by.return_value = [line]
        return line

    def build_extension(self, **kwargs):
        parameters = {'id': sentinel.extension_id}
        parameters.update(kwargs)
        extension = Extension(**parameters)
        self.extension_dao.get.return_value = extension
        return extension

    def build_line_extension(self, line, extension):
        line_extension = LineExtension(line_id=line.id,
                                       extension_id=extension.id)

        self.line_extension_dao.find_by_line_id.return_value = line_extension
        return line_extension

    def test_given_no_lines_then_lines_on_device_are_emptied(self):
        self.line_dao.find_all_by.return_value = []

        self.service.update(self.device)

        self.device_dao.update_lines.assert_called_once_with(self.device, [])

    def test_given_no_lines_then_resets_device_to_autoprov(self):
        self.line_dao.find_all_by.return_value = []

        self.service.update(self.device)

        self.device_dao.reset_autoprov.assert_called_once_with(self.device)

    def test_given_unknown_line_protocol_then_does_not_update_lines(self):
        self.build_line(protocol='foobar')

        self.service.update(self.device)

        self.device_dao.update_lines.assert_called_once_with(self.device, [])

    def test_given_sccp_line_then_updates_lines_using_sccp_converter(self):
        line = self.build_line(protocol='sccp')
        expected_converter = LineSCCPConverter(sentinel.registrar)

        self.service.update(self.device)

        self.device_dao.update_lines.assert_called_once_with(self.device, [expected_converter])

        self.device_dao.get_registrar.assert_called_once_with(line.configregistrar)
        self.line_dao.find_all_by.assert_called_once_with(device=line.device_id)

    def test_given_sip_line_without_extension_then_does_not_update_lines(self):
        self.build_line(protocol='sip')
        self.line_extension_dao.find_by_line_id.return_value = None

        self.service.update(self.device)

        self.device_dao.update_lines.assert_called_once_with(self.device, [])

    def test_given_sip_line_with_extension_then_updates_lines_using_sip_converter(self):
        line = self.build_line(protocol='sip')
        extension = self.build_extension()
        self.build_line_extension(line, extension)

        expected_converter = LineSIPConverter(sentinel.registrar, line, extension)

        self.service.update(self.device)

        self.device_dao.update_lines.assert_called_once_with(self.device, [expected_converter])

        self.device_dao.get_registrar.assert_called_once_with(line.configregistrar)
        self.line_dao.find_all_by.assert_called_once_with(device=line.device_id)
        self.line_extension_dao.find_by_line_id.assert_called_once_with(line.id)
        self.extension_dao.get.assert_called_once_with(extension.id)
