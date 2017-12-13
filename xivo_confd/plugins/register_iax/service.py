# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.helpers.resource import CRUDService

from xivo_dao.resources.register_iax import dao as register_iax_dao

from .notifier import build_notifier
from .validator import build_validator


def build_service():
    return CRUDService(register_iax_dao,
                       build_validator(),
                       build_notifier())
