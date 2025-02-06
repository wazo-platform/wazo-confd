# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.tenant import dao

from .notifier import build_notifier


class RecordingsAnnouncementsService:
    def __init__(self, dao, notifier):
        self.dao = dao
        self.notifier = notifier

    def get(self, tenant_uuid):
        return self.dao.get(tenant_uuid)

    def edit(self, resource):
        self.dao.edit(resource)
        self.notifier.edited(resource)


def build_service():
    return RecordingsAnnouncementsService(dao, build_notifier())
