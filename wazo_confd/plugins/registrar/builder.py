# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd import bus

from .dao import RegistrarDao
from .notifier import RegistrarNotifier
from .service import RegistrarService, SearchEngine
from .validator import build_validator


def build_dao(provd_client):
    return RegistrarDao(provd_client)


def build_service(registrar_dao):
    search_engine = SearchEngine(registrar_dao)
    validator = build_validator()
    notifier = RegistrarNotifier(bus)

    registrar_service = RegistrarService(registrar_dao, validator, notifier, search_engine)
    return registrar_service
