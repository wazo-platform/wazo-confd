# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.endpoint_sccp import dao

from wazo_confd.helpers.resource import CRUDService

from .notifier import build_notifier
from .validator import build_validator


class SccpEndpointService(CRUDService):
    pass


def build_service():
    return SccpEndpointService(dao, build_validator(), build_notifier())
