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

from xivo_confd import bus

from xivo_confd.plugins.device.service import (DeviceService,
                                               LineDeviceAssociationService,
                                               SearchEngine,
                                               LineDeviceUpdater,
                                               DeviceUpdater,
                                               FuncKeyDeviceUpdater)

from xivo_confd.plugins.device.dao import ProvdDeviceDao, DeviceDao
from xivo_confd.plugins.device.notifier import DeviceNotifier
from xivo_confd.plugins.device.validator import build_validator

from xivo_confd.plugins.device.funckey import build_converters

from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.func_key_template import dao as template_dao


def build_dao(provd_client):
    provd_dao = ProvdDeviceDao(provd_client.device_manager(),
                               provd_client.config_manager())
    device_dao = DeviceDao(provd_client, provd_dao)
    return device_dao


def build_service(device_dao):
    search_engine = SearchEngine(device_dao.provd_dao)
    device_validator = build_validator(device_dao, line_dao)
    device_notifier = DeviceNotifier(bus)
    device_service = DeviceService(device_dao,
                                   device_validator,
                                   device_notifier,
                                   search_engine,
                                   line_dao)

    return device_service


def build_device_updater(device_dao):
    converters = build_converters()

    funckey_updater = FuncKeyDeviceUpdater(user_dao,
                                           line_dao,
                                           user_line_dao,
                                           template_dao,
                                           device_dao,
                                           converters)

    line_updater = LineDeviceUpdater(line_dao,
                                     extension_dao,
                                     line_extension_dao,
                                     device_dao)

    return DeviceUpdater(line_updater,
                         funckey_updater,
                         user_dao,
                         line_dao,
                         user_line_dao,
                         line_extension_dao,
                         device_dao)


def build_line_device_associator(updater):
    associator = LineDeviceAssociationService(line_dao,
                                              updater)
    return associator
