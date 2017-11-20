# -*- coding: utf-8 -*-
# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .validator import build_validator
from .notifier import build_notifier

from xivo_confd.helpers.resource import CRUDService

from xivo_dao.resources.paging import dao as paging_dao


def build_service():
    return CRUDService(paging_dao,
                       build_validator(),
                       build_notifier())
