# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd import bus
from wazo_confd.plugins.device.builder import build_device_updater
from wazo_confd.plugins.line.service import build_service as build_line_service

from .dao import RegistrarDao
from .notifier import RegistrarNotifier
from .service import RegistrarService
from .validator import build_validator


def build_dao(provd_client):
    return RegistrarDao(provd_client)


def build_service(registrar_dao, provd_client):
    validator = build_validator()
    notifier = RegistrarNotifier(bus)
    line_service = build_line_service(provd_client)
    device_updater = build_device_updater(provd_client)

    registrar_service = RegistrarService(
        registrar_dao, validator, notifier, line_service, device_updater, provd_client
    )
    return registrar_service
