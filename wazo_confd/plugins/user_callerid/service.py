# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.helpers.resource import CRUDService


class UserCallerIDService(CRUDService):
    ...


def build_service():
    return UserCallerIDService()
