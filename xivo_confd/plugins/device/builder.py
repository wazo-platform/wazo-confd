# -*- coding: utf-8 -*-
# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.func_key_template import dao as template_dao
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.user_line import dao as user_line_dao

from xivo_confd import bus, sysconfd
from xivo_confd.database import (
    device as device_db,
    func_key_template as func_key_template_db,
)
from xivo_confd.plugins.device.funckey import build_converters
from xivo_confd.plugins.device.generators import (
    ConfigGenerator,
    ExtensionGenerator,
    FuncKeyGenerator,
    RawConfigGenerator,
    SccpGenerator,
    SipGenerator,
    UserGenerator,
)
from xivo_confd.plugins.device.service import (
    DeviceService,
    SearchEngine,
)
from xivo_confd.plugins.device.update import (
    DeviceUpdater,
    ProvdUpdater,
)

from xivo_confd.plugins.line_device.service import LineDeviceService
from xivo_confd.plugins.line_device.validator import build_validator as build_line_device_validator
from xivo_confd.plugins.line_device.notifier import LineDeviceNotifier

from .dao import DeviceDao
from .notifier import DeviceNotifier
from .validator import build_validator


def build_dao(provd_client):
    return DeviceDao(provd_client)


def build_service(device_dao, provd_client):
    search_engine = SearchEngine(device_dao)
    device_validator = build_validator(device_dao, line_dao)
    device_notifier = DeviceNotifier(bus)
    device_updater = build_device_updater(provd_client)
    line_device_validator = build_line_device_validator()
    line_device_notifier = LineDeviceNotifier(bus, sysconfd)
    line_device = LineDeviceService(line_device_validator, line_dao, line_device_notifier, device_updater)
    device_service = DeviceService(device_dao,
                                   device_validator,
                                   device_notifier,
                                   search_engine,
                                   line_dao,
                                   line_device)

    return device_service


def build_device_updater(provd_client):
    device_dao = build_dao(provd_client)
    generator = build_generators(device_dao)
    provd_updater = ProvdUpdater(device_dao, generator, line_dao)
    return DeviceUpdater(user_dao,
                         line_dao,
                         user_line_dao,
                         line_extension_dao,
                         func_key_template_db,
                         provd_updater)


def build_generators(device_dao):
    converters = build_converters()
    funckey_generator = FuncKeyGenerator(user_dao,
                                         line_dao,
                                         user_line_dao,
                                         template_dao,
                                         device_dao,
                                         converters)

    sip_generator = SipGenerator(device_dao,
                                 device_db)

    sccp_generator = SccpGenerator(device_dao,
                                   line_dao)

    user_generator = UserGenerator(device_db)

    extension_generator = ExtensionGenerator(extension_dao)

    raw_config_generator = RawConfigGenerator([user_generator,
                                               extension_generator,
                                               funckey_generator,
                                               sip_generator,
                                               sccp_generator])

    config_generator = ConfigGenerator(raw_config_generator)

    return config_generator
