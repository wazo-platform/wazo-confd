# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.switchboard import dao as switchboard_dao

from xivo_confd.helpers.resource import CRUDService
from xivo_confd.helpers.validator import ValidationGroup

from .notifier import build_notifier


def build_service():
    return CRUDService(switchboard_dao,
                       ValidationGroup(),
                       build_notifier())
