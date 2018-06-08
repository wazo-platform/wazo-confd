# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.endpoint_sccp import dao

from xivo_confd.helpers.resource import CRUDService
from xivo_confd.plugins.endpoint_sccp.validator import build_validator
from xivo_confd.plugins.endpoint_sccp.notifier import build_notifier


class SccpEndpointService(CRUDService):
    pass


def build_service():
    return SccpEndpointService(dao,
                               build_validator(),
                               build_notifier())
