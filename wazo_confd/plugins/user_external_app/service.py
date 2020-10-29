# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user_external_app import dao as user_external_app_dao

from wazo_confd.helpers.resource import CRUDService

from .notifier import build_notifier
from .validator import build_validator


class UserExternalAppService(CRUDService):
    def search(self, user_uuid, parameters):
        return self.dao.search(user_uuid, **parameters)

    def get(self, user_uuid, external_app_name):
        return self.dao.get(user_uuid, external_app_name)


def build_service():
    return UserExternalAppService(
        user_external_app_dao,
        build_validator(),
        build_notifier(),
    )
