# -*- coding: utf-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from .validator import build_validator
from .notifier import build_notifier

from xivo_confd.helpers.resource import CRUDService

from xivo_dao.resources.ivr import dao as ivr_dao


def build_service():
    return CRUDService(ivr_dao,
                       build_validator(),
                       build_notifier())
