# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.helpers.resource import CRUDService
from xivo_dao.resources.register_sip import dao as register_sip_dao

from .validator import build_validator
from .notifier import build_notifier


def build_service():
    return CRUDService(register_sip_dao,
                       build_validator(),
                       build_notifier())
