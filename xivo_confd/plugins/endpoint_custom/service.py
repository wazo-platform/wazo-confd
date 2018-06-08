# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.endpoint_custom import dao

from xivo_confd.helpers.resource import CRUDService
from xivo_confd.plugins.endpoint_custom.validator import build_validator
from xivo_confd.plugins.endpoint_custom.notifier import build_notifier


def build_service():
    return CRUDService(dao,
                       build_validator(),
                       build_notifier())
