# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from .validator import build_validator
from .notifier import build_notifier

from xivo_confd.helpers.resource import CRUDService

from xivo_dao.resources.outcall import dao as outcall_dao


def build_service():
    return CRUDService(outcall_dao,
                       build_validator(),
                       build_notifier())
