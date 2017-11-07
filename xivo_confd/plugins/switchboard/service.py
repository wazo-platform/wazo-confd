# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from .notifier import build_notifier

from xivo_confd.helpers.resource import CRUDService
from xivo_confd.helpers.validator import ValidationGroup

from xivo_dao.resources.switchboard import dao as switchboard_dao


def build_service():
    return CRUDService(switchboard_dao,
                       ValidationGroup(),
                       build_notifier())
