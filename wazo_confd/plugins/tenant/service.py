# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.tenant import dao

from wazo_confd.helpers.resource import CRUDService


def build_service():
    return CRUDService(dao, None, None)
