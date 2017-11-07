# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.plugins.entity.validator import build_validator
from xivo_confd.plugins.entity.notifier import build_notifier

from xivo_confd.helpers.resource import CRUDService

from xivo_dao.resources.entity import dao as entity_dao


def build_service():
    return CRUDService(entity_dao,
                       build_validator(),
                       build_notifier())
