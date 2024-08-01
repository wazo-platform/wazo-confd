# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.tenant import dao

from .notifier import build_notifier


class LocalizationService:
    def __init__(self, dao, notifier):
        self.dao = dao
        self.notifier = notifier

    def get(self, tenant_uuid):
        return self.dao.get(tenant_uuid)

    def edit(self, resource):
        self.dao.edit(resource)
        self.notifier.edited(resource)


def build_service():
    return LocalizationService(dao, build_notifier())
