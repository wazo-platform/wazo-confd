# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.meeting import dao

from wazo_confd.helpers.resource import CRUDService

from .validator import build_validator


def build_service(notifier):
    return CRUDService(dao, build_validator(), notifier)
