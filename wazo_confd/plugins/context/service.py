# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.context import dao as context_dao

from wazo_confd.helpers.resource import CRUDService

from .notifier import build_notifier
from .validator import build_validator


def build_service():
    return CRUDService(context_dao, build_validator(), build_notifier())
