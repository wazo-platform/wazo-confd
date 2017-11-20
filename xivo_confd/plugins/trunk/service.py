# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from .validator import build_validator
from .notifier import build_notifier

from xivo_confd.helpers.resource import CRUDService

from xivo_dao.resources.trunk import dao as trunk_dao


def build_service():
    return CRUDService(trunk_dao,
                       build_validator(),
                       build_notifier())
