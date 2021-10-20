# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.meeting import dao

from wazo_confd.helpers.resource import CRUDService
from wazo_confd.plugins.ingress_http.service import (
    build_service as build_ingress_http_service,
)

from .notifier import build_notifier
from .validator import build_validator


def build_service():
    ingress_http_service = build_ingress_http_service()
    return CRUDService(dao, build_validator(), build_notifier(ingress_http_service))
